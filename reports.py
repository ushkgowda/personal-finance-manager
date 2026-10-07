"""
reports.py
----------
Report generation and spending analysis calculations. Pure functions that
take a list of Expense objects and return computed summaries - kept
separate from I/O and UI so they're easy to test independently.
"""

from collections import defaultdict
from datetime import date

from validators import format_currency, format_percentage


def total_spent(expenses):
    """Return the sum of all expense amounts."""
    return round(sum(e.amount for e in expenses), 2)


def average_spent(expenses):
    """Return the average expense amount, or 0.0 if the list is empty."""
    if not expenses:
        return 0.0
    return round(total_spent(expenses) / len(expenses), 2)


def category_breakdown(expenses):
    """
    Group expenses by category and sum amounts.

    Returns:
        dict[str, float]: category -> total amount, sorted descending
        by amount.
    """
    totals = defaultdict(float)
    for e in expenses:
        totals[e.category] += e.amount
    return dict(
        sorted(totals.items(), key=lambda kv: kv[1], reverse=True)
    )


def monthly_breakdown(expenses):
    """
    Group expenses by year-month.

    Returns:
        dict[str, float]: "YYYY-MM" -> total amount, sorted chronologically.
    """
    totals = defaultdict(float)
    for e in expenses:
        key = e.date.strftime("%Y-%m")
        totals[key] += e.amount
    return dict(sorted(totals.items()))


def highest_expense(expenses):
    """Return the single largest Expense, or None if list is empty."""
    if not expenses:
        return None
    return max(expenses, key=lambda e: e.amount)


def lowest_expense(expenses):
    """Return the single smallest Expense, or None if list is empty."""
    if not expenses:
        return None
    return min(expenses, key=lambda e: e.amount)


def filter_by_date_range(expenses, start_date, end_date):
    """Return expenses with date in [start_date, end_date] inclusive."""
    return [e for e in expenses if start_date <= e.date <= end_date]


def filter_by_category(expenses, category):
    """Return expenses matching the given category (case-insensitive)."""
    category = category.strip().lower()
    return [e for e in expenses if e.category.lower() == category]


def build_summary_report(expenses):
    """
    Build a full text summary report string covering totals, averages,
    category breakdown, and highest/lowest expenses.

    Args:
        expenses (list[Expense])

    Returns:
        str: A formatted, human-readable report.
    """
    lines = []
    lines.append("=" * 50)
    lines.append("EXPENSE SUMMARY REPORT")
    lines.append("=" * 50)

    if not expenses:
        lines.append("No expenses recorded yet.")
        lines.append("=" * 50)
        return "\n".join(lines)

    total = total_spent(expenses)
    avg = average_spent(expenses)

    lines.append(f"Generated: {date.today().strftime('%Y-%m-%d')}")
    lines.append(f"Total Expenses Recorded: {len(expenses)}")
    lines.append(f"Total Spent:             {format_currency(total)}")
    lines.append(f"Average per Expense:     {format_currency(avg)}")

    high = highest_expense(expenses)
    low = lowest_expense(expenses)
    lines.append(f"Highest Expense:         {format_currency(high.amount)} "
                 f"({high.category} on {high.date})")
    lines.append(f"Lowest Expense:          {format_currency(low.amount)} "
                 f"({low.category} on {low.date})")

    lines.append("-" * 50)
    lines.append("BY CATEGORY")
    lines.append("-" * 50)
    breakdown = category_breakdown(expenses)
    for category, amount in breakdown.items():
        pct = format_percentage(amount, total)
        lines.append(f"  {category:<15} {format_currency(amount):>12}   ({pct})")

    lines.append("-" * 50)
    lines.append("BY MONTH")
    lines.append("-" * 50)
    months = monthly_breakdown(expenses)
    for month, amount in months.items():
        lines.append(f"  {month:<15} {format_currency(amount):>12}")

    lines.append("=" * 50)
    return "\n".join(lines)
