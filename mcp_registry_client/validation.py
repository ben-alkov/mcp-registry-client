"""Input validation helpers for CLI commands."""


def validate_non_empty_string(value: str, field_name: str) -> None:
    """Validate that a string is non-empty after stripping whitespace.

    Args:
        value: The string value to validate
        field_name: Name of the field for error messages

    Raises:
        ValueError: If the string is empty or only whitespace

    """
    if not value or not value.strip():
        msg = f'{field_name} cannot be empty'
        raise ValueError(msg)


def validate_search_term(search_term: str) -> None:
    """Validate search term for server search.

    Args:
        search_term: The search term to validate

    Raises:
        ValueError: If search term is invalid

    """
    validate_non_empty_string(search_term, 'Search term')

    # Additional validation rules can be added here
    if len(search_term.strip()) < 1:
        msg = 'Search term must be at least 1 character long'
        raise ValueError(msg)


def validate_server_name(server_name: str) -> None:
    """Validate server name for info retrieval.

    Args:
        server_name: The server name to validate

    Raises:
        ValueError: If server name is invalid

    """
    validate_non_empty_string(server_name, 'Server name')

    # Additional validation rules can be added here
    if len(server_name.strip()) < 1:
        msg = 'Server name must be at least 1 character long'
        raise ValueError(msg)
