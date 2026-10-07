"""
file_handler.py
----------------
Handles all disk I/O: reading/writing the CSV expense store, and creating /
restoring timestamped backups. All functions here fail loudly with clear
exceptions rather than silently corrupting data.
"""

import csv
import os
import shutil
from datetime import datetime

from expense import Expense

FIELDNAMES = ["id", "amount", "category", "date", "description"]


class FileHandler:
    """
    Encapsulates all CSV persistence and backup/restore operations for a
    single data file.
    """

    def __init__(self, data_file="data/expenses.csv", backup_dir="backups"):
        self.data_file = data_file
        self.backup_dir = backup_dir
        self._ensure_paths_exist()

    # ------------------------------------------------------------------
    # Setup
    # ------------------------------------------------------------------

    def _ensure_paths_exist(self):
        """Create the data directory, backup directory, and an empty CSV
        (with header row) if they don't already exist."""
        data_dir = os.path.dirname(self.data_file)
        if data_dir and not os.path.exists(data_dir):
            os.makedirs(data_dir, exist_ok=True)
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir, exist_ok=True)
        if not os.path.exists(self.data_file):
            self._write_rows([])

    # ------------------------------------------------------------------
    # Core CSV read/write
    # ------------------------------------------------------------------

    def _write_rows(self, rows):
        """Overwrite the data file with the given list of dict rows."""
        try:
            with open(self.data_file, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
                writer.writeheader()
                writer.writerows(rows)
        except OSError as e:
            raise IOError(f"Failed to write to '{self.data_file}': {e}")

    def load_expenses(self):
        """
        Read all expenses from the CSV file.

        Returns:
            list[Expense]: All valid expenses found in the file.

        Malformed rows are skipped with a warning rather than crashing the
        whole load, so one bad row doesn't lock the user out of their data.
        """
        expenses = []
        if not os.path.exists(self.data_file):
            return expenses

        try:
            with open(self.data_file, mode="r", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for i, row in enumerate(reader, start=2):  # row 1 = header
                    try:
                        expenses.append(Expense.from_dict(row))
                    except (ValueError, KeyError) as e:
                        print(f"  [Warning] Skipping malformed row {i} in "
                              f"{self.data_file}: {e}")
        except OSError as e:
            raise IOError(f"Failed to read from '{self.data_file}': {e}")

        return expenses

    def save_expenses(self, expenses):
        """
        Persist a full list of Expense objects to the CSV file,
        overwriting existing content.

        Args:
            expenses (list[Expense])
        """
        rows = [e.to_dict() for e in expenses]
        self._write_rows(rows)

    def append_expense(self, expense):
        """
        Append a single Expense to the CSV file without rewriting
        the whole file. Assumes the file already has a header.
        """
        try:
            with open(self.data_file, mode="a", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
                writer.writerow(expense.to_dict())
        except OSError as e:
            raise IOError(f"Failed to append to '{self.data_file}': {e}")

    def get_next_id(self, expenses=None):
        """Return the next available integer id, based on current data."""
        if expenses is None:
            expenses = self.load_expenses()
        if not expenses:
            return 1
        existing_ids = [e.expense_id for e in expenses if e.expense_id is not None]
        return max(existing_ids, default=0) + 1

    # ------------------------------------------------------------------
    # Backup / restore
    # ------------------------------------------------------------------

    def create_backup(self):
        """
        Copy the current data file into the backup directory with a
        timestamped filename.

        Returns:
            str: Path to the created backup file.

        Raises:
            IOError: If the data file doesn't exist or copy fails.
        """
        if not os.path.exists(self.data_file):
            raise IOError("No data file exists yet; nothing to back up.")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = os.path.splitext(os.path.basename(self.data_file))[0]
        backup_name = f"{base_name}_backup_{timestamp}.csv"
        backup_path = os.path.join(self.backup_dir, backup_name)

        try:
            shutil.copy2(self.data_file, backup_path)
        except OSError as e:
            raise IOError(f"Backup failed: {e}")

        return backup_path

    def list_backups(self):
        """
        Returns:
            list[str]: Backup filenames sorted newest first.
        """
        if not os.path.exists(self.backup_dir):
            return []
        files = [
            f for f in os.listdir(self.backup_dir)
            if f.endswith(".csv")
        ]
        files.sort(reverse=True)
        return files

    def restore_backup(self, backup_filename):
        """
        Restore the data file from a given backup filename (must exist in
        the backup directory). The current data file is itself backed up
        first, so a restore is never destructive/irreversible.

        Args:
            backup_filename (str): A filename as returned by list_backups().

        Raises:
            IOError: If the backup file doesn't exist or copy fails.
        """
        backup_path = os.path.join(self.backup_dir, backup_filename)
        if not os.path.exists(backup_path):
            raise IOError(f"Backup file not found: {backup_filename}")

        # Safety net: back up current state before overwriting it.
        if os.path.exists(self.data_file):
            try:
                self.create_backup()
            except IOError:
                pass  # current file may be empty/new; not fatal

        try:
            shutil.copy2(backup_path, self.data_file)
        except OSError as e:
            raise IOError(f"Restore failed: {e}")
