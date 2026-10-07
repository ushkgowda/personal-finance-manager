#!/usr/bin/env python3
"""
main.py
-------
Entry point for the Personal Finance Manager. Run this file to start the
interactive command-line application:

    python main.py
"""

import sys

from ui import FinanceManagerUI


def main():
    app = FinanceManagerUI(
        data_file="data/expenses.csv",
        backup_dir="backups",
    )
    try:
        app.run()
    except KeyboardInterrupt:
        print("\n\nInterrupted. Saving your data before exit...")
        app._persist_all()
        print("Goodbye!")
        sys.exit(0)


if __name__ == "__main__":
    main()
