def prepare_row(headers: list, info: dict) -> list:
    """
    Собирает из info значения в порядке headers.
    """
    return [info.get(col, '') for col in headers]
