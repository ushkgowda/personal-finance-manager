# personal-finance-manager

# 💰 Personal Finance Manager

A simple and modular **Personal Finance Manager** built with Python. This command-line application allows users to manage their daily expenses, analyze spending patterns, generate reports, and securely back up and restore financial data.

## 🚀 Features

* ➕ **Add Expenses**

  * Record amount, category, date, and description.
* 👀 **View Expenses**

  * Display all recorded expenses.
* ✏️ **Edit Expenses**

  * Update existing expense details.
* 🗑️ **Delete Expenses**

  * Remove unwanted expense records.
* 🔎 **Search & Filter**

  * Search expenses by category or date range.
* 📊 **Spending Reports**

  * Calculate total spending.
  * Calculate average expense.
  * Find highest and lowest expenses.
  * View category-wise spending.
  * View spending percentages.
  * View month-by-month spending totals.
* 💾 **CSV Data Storage**

  * Expenses are automatically stored in a CSV file.
* 🔐 **Backup & Restore**

  * Create timestamped backups.
  * Restore data from previous backups.
* ✅ **Input Validation**

  * Validates amounts, dates, categories, and other user input.
  * Prevents invalid data from crashing the application.

## 🛠️ Technologies Used

* **Python 3**
* Python Standard Library
* CSV File Handling
* Object-Oriented Programming (OOP)
* Modular Programming
* Input Validation
* File Handling

No external Python packages are required.

## 📁 Project Structure

```text
finance_manager/
│
├── main.py             # Application entry point
├── expense.py          # Expense data model
├── file_handler.py     # CSV storage and backup/restore
├── validators.py       # Input validation and formatting
├── reports.py          # Spending analysis and reports
├── ui.py               # Command-line user interface
│
├── data/
│   └── expenses.csv    # Expense data (created automatically)
│
└── backups/            # Timestamped backups (created automatically)
```

## ⚙️ How to Run

### 1. Clone the repository

```bash
git clone https://github.com/your-username/finance_manager.git
```

### 2. Open the project

```bash
cd finance_manager
```

### 3. Run the application

```bash
python main.py
```

On some systems, you may need:

```bash
python3 main.py
```

## 🖥️ Example

```text
╔══════════════════════════════════════════╗
║       PERSONAL FINANCE MANAGER            ║
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

Select an option (1-9): 1

--- Add New Expense ---
Amount: 45.50
Category: Food
Date: 2026-09-22
Description: Groceries

✔ Expense added successfully!
```

## 🧠 Project Architecture

The project follows a modular design where each Python file has a specific responsibility.

### `expense.py`

Contains the `Expense` class, which represents an individual expense and handles expense-related data validation.

### `file_handler.py`

Handles:

* Reading expenses from CSV
* Writing expenses to CSV
* Creating backups
* Restoring previous backups

### `validators.py`

Provides reusable functions for validating and formatting user input.

### `reports.py`

Handles financial calculations and generates spending summaries and reports.

### `ui.py`

Contains the interactive command-line interface and menu system.

### `main.py`

Acts as the entry point of the application and starts the Finance Manager.

## 📊 Sample Operations

The application can answer questions such as:

* How much have I spent?
* What is my average expense?
* Which expense was the highest?
* Which expense was the lowest?
* How much did I spend on Food?
* What percentage of my spending went toward Transport?
* How much did I spend each month?

## 🔒 Data Management

Expense records are stored locally in:

```text
data/expenses.csv
```

Backups are stored in:

```text
backups/
```

This allows users to maintain their financial data locally without requiring an external database.

## 🎯 Learning Objectives

This project demonstrates practical Python programming concepts including:

* Object-Oriented Programming
* Classes and Objects
* Functions and Modules
* File Handling
* CSV Processing
* Exception Handling
* Data Validation
* Searching and Filtering
* Data Analysis
* Software Modularization

## 🔮 Future Improvements

Possible future enhancements include:

* 📈 Graphical spending charts
* 🖥️ GUI application
* 🌐 Web-based interface
* 🗄️ Database integration using SQLite
* 📱 Mobile-friendly version
* 🔐 Password protection
* 📤 Export reports to PDF or Excel
* 📅 Monthly budget tracking
* 💡 Budget alerts and spending recommendations

