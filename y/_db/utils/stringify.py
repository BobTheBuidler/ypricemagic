from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Final, Iterable


UTC: Final = timezone.utc

astimezone: Final = datetime.astimezone
isoformat: Final = datetime.isoformat


def stringify_column_value(value: Any, provider: str) -> str:
    """
    Convert a Python value to a string representation suitable for SQL insertion.

    This function handles various Python types and converts them to SQL-compatible string representations.
    It supports different database providers (currently 'postgres' and 'sqlite') for certain data types.

    Args:
        value: The value to stringify. Can be None, bytes, str, int, Decimal, or datetime.
        provider: The database provider. Currently supports 'postgres' and 'sqlite'.

    Raises:
        NotImplementedError: If the value type is not supported or if an unsupported provider is specified for bytes.

    Note:
        - None values are converted to 'null'.
        - Bytes are handled differently for 'postgres' (converted to bytea using `f"'{value.decode()}'::bytea"`) and 'sqlite' (converted to hex).
        - Strings are wrapped in single quotes.
        - Integers and Decimals are converted to their string representation.
        - Datetimes are converted to UTC and formatted as ISO8601 strings.

    Examples:
        >>> stringify_column_value(None, 'sqlite')
        'null'
        >>> stringify_column_value(b'\\x01\\x02', 'postgres')
        "'\\x0102'::bytea"
        >>> stringify_column_value('text', 'sqlite')
        "'text'"
        >>> stringify_column_value(123, 'postgres')
        '123'
        >>> stringify_column_value(datetime(2023, 1, 1, 12, 0, 0), 'sqlite')
        "'2023-01-01T12:00:00+00:00'"

    See Also:
        - :func:`build_row`
    """
    if value is None:
        return "null"
    elif isinstance(value, bytes):
        if provider == "postgres":
            # return f"E'\\x{value.hex()}"
            return f"'{value.decode()}'::bytea"
        elif provider == "sqlite":
            return f"X'{value.hex()}'"
        raise NotImplementedError(provider)
    elif isinstance(value, str):
        return f"'{value}'"
    elif isinstance(value, (int, Decimal)):
        return str(value)
    elif isinstance(value, datetime):
        return f"'{isoformat(astimezone(value, UTC))}'"
    else:
        raise NotImplementedError(type(value), value)


def build_row(row: Iterable[Any], provider: str) -> str:
    """
    Build a SQL row string from an iterable of values.

    This function takes an iterable of values and converts each value to its SQL string representation,
    then combines them into a single row string suitable for SQL insertion.

    Args:
        row: An iterable of values to be converted into a SQL row string.
        provider: The database provider to use for value conversion.

    Returns:
        A string representing a SQL row, formatted as (value1,value2,...).

    Note:
        This function uses :func:`stringify_column_value` internally to convert each value.

    Examples:
        >>> build_row([None, b'\\x01\\x02', 'text', 123], 'sqlite')
        "(null,X'0102','text',123)"

    See Also:
        - :func:`stringify_column_value`
    """
    return f"({','.join(stringify_column_value(col, provider) for col in row)})"


def build_query(
    provider_name: str, entity_name: str, columns: Iterable[str], items: Iterable[Any]
) -> str:
    data = ",".join(build_row(i, provider_name) for i in items)
    if provider_name == "sqlite":
        return f'insert or ignore into {entity_name} ({",".join(columns)}) values {data}'
    elif provider_name == "postgres":
        return (
            f'insert into {entity_name} ({",".join(columns)}) values {data} on conflict do nothing'
        )
    else:
        raise NotImplementedError(provider_name)
