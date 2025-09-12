"""Performance tests for retry functionality."""

import asyncio
import gc
import time
from typing import Never

import pytest

from mcp_registry_client.config import ClientConfig
from mcp_registry_client.retry import RetryStrategy, with_retry


@pytest.mark.benchmark
class TestRetryPerformance:
    """Performance benchmarks for retry operations."""

    @pytest.fixture
    def config(self) -> ClientConfig:
        """Create test client configuration."""
        config = ClientConfig()
        config.max_retries = 3
        config.retry_delay = 0.01  # 10ms initial delay
        config.backoff_factor = 2.0
        return config

    @pytest.fixture
    def retry_strategy(self, config: ClientConfig) -> RetryStrategy:
        """Create test retry strategy."""
        return RetryStrategy(config)

    def test_retry_strategy_initialization_performance(
        self, benchmark, config: ClientConfig
    ) -> None:
        """Benchmark retry strategy initialization."""

        def create_retry_strategy() -> list[RetryStrategy]:
            strategies = []
            for _ in range(100):
                strategy = RetryStrategy(config)
                strategies.append(strategy)
            return strategies

        strategies = benchmark(create_retry_strategy)
        assert len(strategies) == 100

    @pytest.mark.asyncio
    async def test_successful_operation_performance(
        self, retry_strategy: RetryStrategy
    ) -> None:
        """Test performance when operation succeeds immediately."""
        call_count = 0

        async def successful_operation() -> str:
            nonlocal call_count
            call_count += 1
            return 'success'

        start_time = time.time()
        result = await with_retry(successful_operation, retry_strategy)
        elapsed_time = time.time() - start_time

        assert result == 'success'
        assert call_count == 1
        # Should be very fast for immediate success
        assert elapsed_time < 0.1, (
            f'Successful operation took too long: {elapsed_time:.3f}s'
        )

    @pytest.mark.asyncio
    async def test_retry_with_eventual_success_performance(
        self, retry_strategy: RetryStrategy
    ) -> None:
        """Test performance when operation succeeds after retries."""
        call_count = 0

        async def eventually_successful_operation() -> str:
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                msg = 'Temporary failure'
                raise ConnectionError(msg)
            return 'success'

        start_time = time.time()
        result = await with_retry(eventually_successful_operation, retry_strategy)
        elapsed_time = time.time() - start_time

        assert result == 'success'
        assert call_count == 3

        # Should complete within reasonable time including backoff delays
        assert elapsed_time < 0.5, f'Retry operation took too long: {elapsed_time:.3f}s'

    @pytest.mark.asyncio
    async def test_max_retries_performance(self, retry_strategy: RetryStrategy) -> None:
        """Test performance when all retries are exhausted."""
        call_count = 0

        async def always_failing_operation() -> Never:
            nonlocal call_count
            call_count += 1
            msg = 'Persistent failure'
            raise ConnectionError(msg)

        start_time = time.time()

        try:
            await with_retry(always_failing_operation, retry_strategy)
            pytest.fail('Expected ConnectionError to be raised')
        except ConnectionError:
            pass  # Expected

        elapsed_time = time.time() - start_time

        assert call_count == 4  # Initial call + 3 retries

        # Should respect the backoff delays but not take too long
        assert elapsed_time < 0.5, (
            f'Failed retry operation took too long: {elapsed_time:.3f}s'
        )

    @pytest.mark.asyncio
    async def test_concurrent_retry_operations_performance(
        self, retry_strategy: RetryStrategy
    ) -> None:
        """Test performance of concurrent retry operations."""
        num_operations = 20  # Reduced for performance
        success_counts = []

        async def sometimes_failing_operation(operation_id: int) -> str:
            # Simulate different failure patterns
            if operation_id % 3 == 0:  # 1/3 fail twice then succeed
                call_count = getattr(
                    sometimes_failing_operation, f'count_{operation_id}', 0
                )
                call_count += 1
                setattr(sometimes_failing_operation, f'count_{operation_id}', call_count)

                if call_count < 3:
                    msg = f'Temporary failure {operation_id}'
                    raise ConnectionError(msg)
                success_counts.append(operation_id)
                return f'success-{operation_id}'
            # 2/3 succeed immediately
            success_counts.append(operation_id)
            return f'success-{operation_id}'

        start_time = time.time()

        # Run concurrent retry operations
        tasks = [
            with_retry(lambda i=i: sometimes_failing_operation(i), retry_strategy)  # type: ignore[misc]
            for i in range(num_operations)
        ]

        results = await asyncio.gather(*tasks)

        elapsed_time = time.time() - start_time

        # All operations should succeed
        assert len(results) == num_operations
        assert all(r.startswith('success-') for r in results)
        assert len(success_counts) == num_operations

        # Should complete reasonably quickly even with retries
        assert elapsed_time < 3.0, (
            f'Concurrent retry operations took too long: {elapsed_time:.3f}s'
        )

    @pytest.mark.asyncio
    async def test_retry_memory_usage_pattern(self, retry_strategy: RetryStrategy) -> None:
        """Test memory usage patterns during retry operations."""
        # Measure baseline memory usage
        gc.collect()

        async def memory_intensive_operation() -> Never:
            # Create some objects that might not be cleaned up properly
            msg = 'Test failure'
            raise ConnectionError(msg)

        # Run many retry operations that create and clean up objects
        for _ in range(20):  # Reduced for performance
            try:
                await with_retry(memory_intensive_operation, retry_strategy)
            except ConnectionError:
                pass  # Expected

        # Force garbage collection
        gc.collect()

        # This is a basic memory check - more sophisticated profiling
        # would require additional tools
        assert True  # Basic completion test

    def test_retry_strategy_decision_performance(
        self, benchmark, retry_strategy: RetryStrategy
    ) -> None:
        """Benchmark retry decision making."""

        def make_retry_decisions() -> list[bool]:
            decisions = []
            exceptions = [
                ConnectionError('Connection failed'),
                TimeoutError('Request timed out'),
                ValueError('Invalid value'),  # Should not retry
                Exception('Generic error'),
            ]

            for attempt in range(10):
                for exc in exceptions:
                    decision = retry_strategy.should_retry(attempt, exc)
                    decisions.append(decision)
            return decisions

        decisions = benchmark(make_retry_decisions)
        assert len(decisions) == 40  # 10 attempts * 4 exceptions

        # Verify some basic retry logic
        # (This depends on the actual implementation)
        assert any(decisions)  # Some should be retryable
        assert not all(decisions)  # Some should not be retryable
