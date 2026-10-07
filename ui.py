"""
ui.py
-----
Interactive command-line interface. Handles all user-facing menus, input
prompts, and dispatch to the underlying business logic (Expense,
FileHandler, reports). This is the only module that calls input()/print()
for interaction, keeping the rest of the codebase UI-agnostic.
"""

from datetime import date

from expense import Expense
from file_handler import FileHandler
import reports
import validators


class FinanceManagerUI:
    """Drives the interactive menu loop for the personal finance manager."""

    def __init__(self, data_file="data/expenses.csv", backup_dir="backups"):
        self.file_handler = FileHandler(data_file=data_file, backup_dir=backup_dir)
        self.expenses = self.file_handler.load_expenses()

    # ------------------------------------------------------------------
    # Generic input helpers
    # ------------------------------------------------------------------

    def _prompt(self, message, validator_fn=None, allow_empty=False):
        """
        Prompt the user repeatedly until valid input is given.

        Args:
            message (str): The prompt text.
            validator_fn (callable | None): A function that takes the raw
                string and returns a validated value, or raises ValueError.
            allow_empty (bool): If True, an empty string bypasses the
                validator and is returned as-is (useful for optional fields).

        Returns:
            The validated value (or raw string if no validator given).
        """
        while True:
            raw = input(message).strip()
            if allow_empty and raw == "":
                return "" if validator_fn is None else validator_fn(raw)
            if validator_fn is None:
                return raw
            try:
                return validator_fn(raw)
            except ValueError as e:
                print(f"  ⚠ {e} Please try again.")

    def _confirm(self, message):
        """Ask a yes/no question. Returns True/False."""
        while True:
            raw = input(f"{message} (y/n): ").strip().lower()
            if raw in ("y", "yes"):
                return True
            if raw in ("n", "no"):
                return False
            print("  ⚠ Please enter 'y' or 'n'.")

    # ------------------------------------------------------------------
    # Menu loop
    # ------------------------------------------------------------------

    MENU_TEXT = """
╔══════════════════════════════════════════╗
║      PERSONAL FINANCE MANAGER             ║
╠══════════════════════════════════════════╣
║  1. Add Expense                           ║
║  2. View All Expenses                     ║
║  3. Edit Expense                          ║
║  4. Delete Expense                        ║
║  5. Search / Filter Expenses              ║
║  6. Generate Summary Report               ║
║  7. Backup Data                           ║
║  8. Restore from Backup                   ║
║  9. Exit                                  ║
╚══════════════════════════════════════════╝
"""

    def run(self):
        """Main interactive loop."""
        print("Welcome to your Personal Finance Manager!")
        print(f"Loaded {len(self.expenses)} existing expense(s).")

        actions = {
            "1": self.add_expense,
            "2": self.view_expenses,
            "3": self.edit_expense,
            "4": self.delete_expense,
            "5": self.search_expenses,
            "6": self.generate_report,
            "7": self.backup_data,
            "8": self.restore_data,
            "9": self.exit_app,
        }

        while True:
            print(self.MENU_TEXT)
            choice = input("Select an option (1-9): ").strip()
            action = actions.get(choice)
            if action is None:
                print("  ⚠ Invalid option. Please choose 1-9.")
                continue
            try:
                should_continue = action()
            except Exception as e:  # noqa: BLE001 - top-level safety net
                print(f"  ⚠ Unexpected error: {e}")
                should_continue = True
            if should_continue is False:
                break

    # ------------------------------------------------------------------
    # Menu actions
    # ------------------------------------------------------------------

    def add_expense(self):
        print("\n--- Add New Expense ---")
        amount = self._prompt("Amount ($): ", validators.validate_amount)

        print(f"Suggested categories: {', '.join(validators.DEFAULT_CATEGORIES)}")
        category = self._prompt("Category: ", validators.validate_category)

        date_val = self._prompt(
            "Date (YYYY-MM-DD, or blank/'today' for today): ",
            validators.validate_date,
            allow_empty=True,
        )
        description = self._prompt(
            "Description (optional): ",
            validators.validate_description,
            allow_empty=True,
        )

        next_id = self.file_handler.get_next_id(self.expenses)
        try:
            expense = Expense(
                amount=amount,
                category=category,
                date=date_val,
                description=description,
                expense_id=next_id,
            )
        except ValueError as e:
            print(f"  ⚠ Could not create expense: {e}")
            return True

        self.expenses.append(expense)
        try:
            self.file_handler.append_expense(expense)
        except IOError as e:
            print(f"  ⚠ Saved in memory but failed to write to disk: {e}")
            return True

        print(f"  ✔ Added: {expense}")
        return True

    def view_expenses(self):
        print("\n--- All Expenses ---")
        self._print_expense_table(self.expenses)
        return True

    def _print_expense_table(self, expenses):
        if not expenses:
            print("  No expenses to show.")
            return
        sorted_expenses = sorted(expenses, key=lambda e: e.date)
        print(f"  {'ID':<5}{'Date':<12}{'Category':<15}{'Amount':>12}   Description")
        print("  " + "-" * 70)
        for e in sorted_expenses:
            print(
                f"  {e.expense_id:<5}{e.date.strftime('%Y-%m-%d'):<12}"
                f"{e.category:<15}{validators.format_currency(e.amount):>12}   "
                f"{e.description}"
            )
        print("  " + "-" * 70)
        print(f"  Total: {validators.format_currency(reports.total_spent(expenses))} "
              f"across {len(expenses)} expense(s)")

    def _find_expense_by_id(self, expense_id):
        for e in self.expenses:
            if e.expense_id == expense_id:
                return e
        return None

    def edit_expense(self):
        print("\n--- Edit Expense ---")
        if not self.expenses:
            print("  No expenses to edit.")
            return True

        self._print_expense_table(self.expenses)
        raw_id = self._prompt("\nEnter the ID of the expense to edit: ")
        try:
            expense_id = int(raw_id)
        except ValueError:
            print("  ⚠ ID must be a number.")
            return True

        target = self._find_expense_by_id(expense_id)
        if target is None:
            print(f"  ⚠ No expense found with ID {expense_id}.")
            return True

        print(f"Editing: {target}")
        print("Leave a field blank to keep its current value.")

        new_amount = self._prompt(
            f"Amount [{target.amount}]: ",
            lambda raw: validators.validate_amount(raw) if raw else target.amount,
            allow_empty=True,
        )
        new_category = self._prompt(
            f"Category [{target.category}]: ",
            lambda raw: validators.validate_category(raw) if raw else target.category,
            allow_empty=True,
        )
        new_date = self._prompt(
            f"Date [{target.date}]: ",
            lambda raw: validators.validate_date(raw) if raw else target.date,
            allow_empty=True,
        )
        new_description = self._prompt(
            f"Description [{target.description}]: ",
            lambda raw: validators.validate_description(raw) if raw else target.description,
            allow_empty=True,
        )

        try:
            updated = Expense(
                amount=new_amount,
                category=new_category,
                date=new_date,
                description=new_description,
                expense_id=target.expense_id,
            )
        except ValueError as e:
            print(f"  ⚠ Could not update expense: {e}")
            return True

        idx = self.expenses.index(target)
        self.expenses[idx] = updated
        self._persist_all()
        print(f"  ✔ Updated: {updated}")
        return True

    def delete_expense(self):
        print("\n--- Delete Expense ---")
        if not self.expenses:
            print("  No expenses to delete.")
            return True

        self._print_expense_table(self.expenses)
        raw_id = self._prompt("\nEnter the ID of the expense to delete: ")
        try:
            expense_id = int(raw_id)
        except ValueError:
            print("  ⚠ ID must be a number.")
            return True

        target = self._find_expense_by_id(expense_id)
        if target is None:
            print(f"  ⚠ No expense found with ID {expense_id}.")
            return True

        if not self._confirm(f"Delete '{target}'?"):
            print("  Cancelled.")
            return True

        self.expenses.remove(target)
        self._persist_all()
        print("  ✔ Deleted.")
        return True

    def search_expenses(self):
        print("\n--- Search / Filter Expenses ---")
        print("  1. By category")
        print("  2. By date range")
        sub_choice = self._prompt(
            "Choose a filter type (1-2): ",
            lambda raw: validators.validate_menu_choice(raw, ["1", "2"]),
        )

        if sub_choice == "1":
            category = self._prompt("Category to search for: ", validators.validate_category)
            results = reports.filter_by_category(self.expenses, category)
        else:
            start_raw = self._prompt(
                "Start date (YYYY-MM-DD, blank = earliest): ", allow_empty=True
            )
            end_raw = self._prompt(
                "End date (YYYY-MM-DD, blank = today): ", allow_empty=True
            )
            try:
                start, end = validators.validate_date_range(start_raw, end_raw)
            except ValueError as e:
                print(f"  ⚠ {e}")
                return True
            results = reports.filter_by_date_range(self.expenses, start, end)

        print(f"\nFound {len(results)} matching expense(s):")
        self._print_expense_table(results)
        return True

    def generate_report(self):
        print()
        report_text = reports.build_summary_report(self.expenses)
        print(report_text)

        if self._confirm("\nSave this report to a text file?"):
            filename = f"report_{date.today().strftime('%Y%m%d')}.txt"
            try:
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(report_text)
                print(f"  ✔ Report saved to '{filename}'.")
            except OSError as e:
                print(f"  ⚠ Failed to save report: {e}")
        return True

    def backup_data(self):
        print("\n--- Backup Data ---")
        try:
            path = self.file_handler.create_backup()
            print(f"  ✔ Backup created: {path}")
        except IOError as e:
            print(f"  ⚠ {e}")
        return True

    def restore_data(self):
        print("\n--- Restore from Backup ---")
        backups = self.file_handler.list_backups()
        if not backups:
            print("  No backups available.")
            return True

        print("Available backups (newest first):")
        for i, name in enumerate(backups, start=1):
            print(f"  {i}. {name}")

        raw_choice = self._prompt(
            f"Choose a backup to restore (1-{len(backups)}), or blank to cancel: ",
            allow_empty=True,
        )
        if raw_choice == "":
            print("  Cancelled.")
            return True
        try:
            index = int(raw_choice) - 1
            if not (0 <= index < len(backups)):
                raise ValueError
        except ValueError:
            print("  ⚠ Invalid selection.")
            return True

        chosen = backups[index]
        if not self._confirm(
            f"This will overwrite current data with '{chosen}'. Continue?"
        ):
            print("  Cancelled.")
            return True

        try:
            self.file_handler.restore_backup(chosen)
            self.expenses = self.file_handler.load_expenses()
            print(f"  ✔ Restored from '{chosen}'. {len(self.expenses)} expense(s) loaded.")
        except IOError as e:
            print(f"  ⚠ {e}")
        return True

    def exit_app(self):
        print("\nSaving and exiting. Goodbye!")
        self._persist_all()
        return False

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _persist_all(self):
        """Rewrite the entire CSV from the current in-memory expense list."""
        try:
            self.file_handler.save_expenses(self.expenses)
        except IOError as e:
            print(f"  ⚠ Failed to save data to disk: {e}")
