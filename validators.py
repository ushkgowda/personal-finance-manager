"""
validators.py
-------------
Standalone validation and formatting helper functions used by the UI layer
to sanitize raw user input before it ever reaches the Expense class or the
file handling layer.
"""

from datetime import datetime, date

DATE_FORMAT = "%Y-%m-%d"

# A reasonably open-ended default category list. Users can still type a
# custom category; this is just used for the menu of suggestions.
DEFAULT_CATEGORIES = [
    "Food",
    "Transport",
    "Housing",
    "Utilities",
    "Entertainment",
    "Health",
    "Shopping",
    "Education",
    "Savings",
    "Other",
]


def validate_amount(raw_value):
    """
    Validate and convert a raw string into a positive float.

    Returns:
        float: The validated amount, rounded to 2 decimal places.

    Raises:
        ValueError: If the value is not a valid positive number.
    """
    if raw_value is None or str(raw_value).strip() == "":
        raise ValueError("Amount cannot be empty.")
    cleaned = str(raw_value).strip().replace("$", "").replace(",", "")
    try:
        value = float(cleaned)
    except ValueError:
        raise ValueError(f"'{raw_value}' is not a valid number.")
    if value <= 0:
        raise ValueError("Amount must be greater than zero.")
    if value > 1_000_000_000:
        raise ValueError("Amount is unreasonably large.")
    return round(value, 2)


def validate_category(raw_value):
    """
    Validate a category string.

    Returns:
        str: The cleaned, title-cased category name.

    Raises:
        ValueError: If empty or contains only whitespace/invalid characters.
    """
    if raw_value is None or not str(raw_value).strip():
        raise ValueError("Category cannot be empty.")
    cleaned = str(raw_value).strip()
    if len(cleaned) > 40:
        raise ValueError("Category name is too long (max 40 characters).")
    return cleaned.title()


def validate_date(raw_value):
    """
    Validate a date string in YYYY-MM-DD format. Accepts empty string /
    the word "today" to mean today's date.

    Returns:
        datetime.date

    Raises:
        ValueError: If the format is invalid or the date is in the future.
    """
    if raw_value is None or str(raw_value).strip() == "" or str(raw_value).strip().lower() == "today":
        return date.today()
    cleaned = str(raw_value).strip()
    try:
        parsed = datetime.strptime(cleaned, DATE_FORMAT).date()
    except ValueError:
        raise ValueError(f"Date must be in YYYY-MM-DD format (got '{raw_value}').")
    if parsed > date.today():
        raise ValueError("Date cannot be in the future.")
    return parsed


def validate_description(raw_value, max_length=200):
    """
    Validate/clean an optional description field.

    Returns:
        str: The cleaned description (may be empty string).

    Raises:
        ValueError: If longer than max_length.
    """
    if raw_value is None:
        return ""
    cleaned = str(raw_value).strip()
    if len(cleaned) > max_length:
        raise ValueError(f"Description too long (max {max_length} characters).")
    return cleaned


def validate_menu_choice(raw_value, valid_choices):
    """
    Validate that raw_value (as a stripped string) is one of valid_choices.

    Args:
        raw_value (str): User input.
        valid_choices (iterable[str]): Acceptable choices.

    Returns:
        str: The matched choice.

    Raises:
        ValueError: If not a valid choice.
    """
    cleaned = str(raw_value).strip()
    if cleaned not in valid_choices:
        raise ValueError(
            f"Invalid choice '{raw_value}'. Valid options: {', '.join(valid_choices)}"
        )
    return cleaned


def validate_date_range(start_raw, end_raw):
    """
    Validate a start/end date pair, ensuring start <= end.

    Returns:
        tuple(date, date)

    Raises:
        ValueError: If either date is invalid or start is after end.
    """
    start = validate_date(start_raw) if start_raw else date.min
    end = validate_date(end_raw) if end_raw else date.today()
    if start > end:
        raise ValueError("Start date cannot be after end date.")
    return start, end


def format_currency(amount):
    """Format a number as a currency string, e.g. 1234.5 -> '$1,234.50'."""
    return f"${amount:,.2f}"


def format_percentage(part, whole):
    """Format part/whole as a percentage string. Handles whole == 0 safely."""
    if whole == 0:
        return "0.0%"
    return f"{(part / whole) * 100:.1f}%"
