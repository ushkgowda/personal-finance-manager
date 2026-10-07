"""
expense.py
----------
Defines the Expense class: the core data model for a single expense record.
"""

from datetime import datetime


class Expense:
    """
    Represents a single expense entry.

    Attributes:
        amount (float): The monetary value of the expense. Always positive.
        category (str): The category the expense belongs to (e.g. "Food").
        date (datetime.date): The date the expense occurred.
        description (str): A short free-text description of the expense.
        expense_id (int): A unique identifier assigned by the manager/storage layer.
    """

    # Date format used everywhere for parsing/formatting consistency
    DATE_FORMAT = "%Y-%m-%d"

    def __init__(self, amount, category, date, description="", expense_id=None):
        """
        Create a new Expense.

        Args:
            amount (float): Positive numeric amount.
            category (str): Category name.
            date (datetime.date | str): A date object, or a string in YYYY-MM-DD format.
            description (str): Optional free-text note.
            expense_id (int | None): Optional unique id (assigned later if None).

        Raises:
            ValueError: If amount is not positive, or date string is malformed.
        """
        self.expense_id = expense_id
        self.amount = self._validate_amount(amount)
        self.category = self._validate_category(category)
        self.date = self._validate_date(date)
        self.description = description.strip() if description else ""

    # ------------------------------------------------------------------
    # Validation helpers (kept as static/internal methods so the class is
    # self-contained and always constructs a valid object or raises).
    # ------------------------------------------------------------------

    @staticmethod
    def _validate_amount(amount):
        try:
            amount = float(amount)
        except (TypeError, ValueError):
            raise ValueError(f"Amount must be a number, got: {amount!r}")
        if amount <= 0:
            raise ValueError("Amount must be greater than zero.")
        return round(amount, 2)

    @staticmethod
    def _validate_category(category):
        if not category or not str(category).strip():
            raise ValueError("Category cannot be empty.")
        return str(category).strip().title()

    @classmethod
    def _validate_date(cls, date):
        if isinstance(date, datetime):
            return date.date()
        if hasattr(date, "year") and hasattr(date, "month") and hasattr(date, "day"):
            # Already a date object
            return date
        try:
            return datetime.strptime(str(date).strip(), cls.DATE_FORMAT).date()
        except ValueError:
            raise ValueError(
                f"Date must be in {cls.DATE_FORMAT} format, got: {date!r}"
            )

    # ------------------------------------------------------------------
    # Conversion helpers
    # ------------------------------------------------------------------

    def to_dict(self):
        """Return a dict representation suitable for CSV writing."""
        return {
            "id": self.expense_id,
            "amount": f"{self.amount:.2f}",
            "category": self.category,
            "date": self.date.strftime(self.DATE_FORMAT),
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, row):
        """
        Build an Expense from a dict (e.g. a row read from a CSV file
        via csv.DictReader).

        Raises:
            ValueError: If required fields are missing or invalid.
        """
        try:
            expense_id = int(row["id"]) if row.get("id") not in (None, "") else None
        except (TypeError, ValueError):
            expense_id = None

        return cls(
            amount=row["amount"],
            category=row["category"],
            date=row["date"],
            description=row.get("description", ""),
            expense_id=expense_id,
        )

    def __repr__(self):
        return (
            f"Expense(id={self.expense_id}, amount={self.amount}, "
            f"category={self.category!r}, date={self.date}, "
            f"description={self.description!r})"
        )

    def __str__(self):
        return (
            f"#{self.expense_id:<4} {self.date.strftime(self.DATE_FORMAT)}  "
            f"{self.category:<15} ${self.amount:>10.2f}  {self.description}"
        )
