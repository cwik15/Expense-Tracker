import sqlite3
from datetime import datetime


# ============================================================
# DATABASE SETUP
# sqlite3.connect() creates the .db file if it doesn't exist.
# The connection object 'conn' is our link to the database.
# A 'cursor' is what actually runs SQL commands.
# ============================================================

def init_db():
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()

    # CREATE TABLE IF NOT EXISTS = only creates once, safe to call every run
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            title     TEXT    NOT NULL,
            amount    REAL    NOT NULL,
            category  TEXT    NOT NULL,
            date      TEXT    NOT NULL
        )
    """)

    conn.commit()   # Save changes
    conn.close()    # Always close when done
    return


# ============================================================
# EXPENSE TRACKER CLASS
# All database operations are methods inside this class.
# __init__ runs automatically when you create an object.
# ============================================================

class ExpenseTracker:

    def __init__(self):
        self.db_name = "expenses.db"
        init_db()  # Make sure table exists before anything else

    def get_connection(self):
        # Helper method — avoids repeating connect() everywhere
        return sqlite3.connect(self.db_name)

    # --------------------------------------------------------
    # ADD EXPENSE
    # INSERT INTO adds a new row to the table.
    # We use ? placeholders (never put values directly in SQL
    # strings — that's a security risk called SQL Injection).
    # --------------------------------------------------------
    def add_expense(self, title, amount, category):
        conn = self.get_connection()
        cursor = conn.cursor()

        date_today = datetime.now().strftime("%Y-%m-%d %H:%M")

        cursor.execute("""
            INSERT INTO expenses (title, amount, category, date)
            VALUES (?, ?, ?, ?)
        """, (title, amount, category, date_today))

        conn.commit()
        conn.close()
        print(f"\n Expense '{title}' of ₹{amount:.2f} added successfully!\n")

    # --------------------------------------------------------
    # VIEW ALL EXPENSES
    # SELECT * FROM = fetch every row from the table.
    # fetchall() returns a list of tuples.
    # Each tuple = one row: (id, title, amount, category, date)
    # --------------------------------------------------------
    def view_expenses(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM expenses ORDER BY id DESC")
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            print("\n No expenses found. Add one first!\n")
            return

        print("\n" + "=" * 60)
        print(f"{'ID':<5} {'Title':<20} {'Amount':>10} {'Category':<15} {'Date'}")
        print("=" * 60)

        total = 0
        for row in rows:
            id_, title, amount, category, date = row
            print(f"{id_:<5} {title:<20} ₹{amount:>9.2f} {category:<15} {date}")
            total += amount

        print("-" * 60)
        print(f"{'TOTAL':<26} ₹{total:>9.2f}")
        print("=" * 60 + "\n")

    # --------------------------------------------------------
    # VIEW BY CATEGORY
    # WHERE clause filters rows — only fetch matching category.
    # LIKE with % = partial match (so "food" matches "Food" too)
    # --------------------------------------------------------
    def view_by_category(self, category):
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM expenses
            WHERE category LIKE ?
            ORDER BY date DESC
        """, (f"%{category}%",))

        rows = cursor.fetchall()
        conn.close()

        if not rows:
            print(f"\n No expenses found in category '{category}'.\n")
            return

        print(f"\n Expenses in category: {category}")
        print("=" * 60)
        print(f"{'ID':<5} {'Title':<20} {'Amount':>10} {'Date'}")
        print("=" * 60)

        total = 0
        for row in rows:
            id_, title, amount, cat, date = row
            print(f"{id_:<5} {title:<20} ₹{amount:>9.2f} {date}")
            total += amount

        print("-" * 60)
        print(f"{'TOTAL':<26} ₹{total:>9.2f}\n")

    # --------------------------------------------------------
    # DELETE EXPENSE
    # DELETE FROM removes a row. We match by id (unique).
    # cursor.rowcount tells us if any row was actually deleted.
    # --------------------------------------------------------
    def delete_expense(self, expense_id):
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
        conn.commit()

        if cursor.rowcount == 0:
            print(f"\n No expense found with ID {expense_id}.\n")
        else:
            print(f"\n Expense ID {expense_id} deleted successfully!\n")

        conn.close()

    # --------------------------------------------------------
    # SUMMARY — total spent per category
    # GROUP BY groups rows with same category together.
    # SUM(amount) adds up amounts within each group.
    # --------------------------------------------------------
    def summary(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT category, SUM(amount), COUNT(*)
            FROM expenses
            GROUP BY category
            ORDER BY SUM(amount) DESC
        """)

        rows = cursor.fetchall()
        conn.close()

        if not rows:
            print("\n No expenses to summarize yet.\n")
            return

        print("\n EXPENSE SUMMARY BY CATEGORY")
        print("=" * 45)
        print(f"{'Category':<20} {'Total':>10} {'Count':>8}")
        print("=" * 45)

        grand_total = 0
        for category, total, count in rows:
            print(f"{category:<20} ₹{total:>9.2f} {count:>7} items")
            grand_total += total

        print("-" * 45)
        print(f"{'GRAND TOTAL':<20} ₹{grand_total:>9.2f}\n")


# ============================================================
# HELPER — safe input functions
# These prevent crashes when user types wrong input.
# ============================================================

def get_float_input(prompt):
    while True:
        try:
            value = float(input(prompt))
            if value <= 0:
                print("  Please enter a positive amount.")
                continue
            return value
        except ValueError:
            print("  Invalid amount. Please enter a number (e.g. 150 or 99.50)")

def get_int_input(prompt):
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("  Please enter a valid number.")


# ============================================================
# MAIN MENU — the CLI loop
# while True keeps the program running until user exits.
# Each option calls a method on the tracker object.
# ============================================================

def main():
    tracker = ExpenseTracker()  # Create one tracker object for the whole session

    print("\n Welcome to Expense Tracker!")
    print("   Your expenses are saved in expenses.db\n")

    while True:
        print("┌─────────────────────────────┐")
        print("│        EXPENSE TRACKER      │")
        print("├─────────────────────────────┤")
        print("│  1. Add Expense             │")
        print("│  2. View All Expenses       │")
        print("│  3. View by Category        │")
        print("│  4. Delete Expense          │")
        print("│  5. Summary                 │")
        print("│  6. Exit                    │")
        print("└─────────────────────────────┘")

        choice = input("Enter choice (1-6): ").strip()

        if choice == "1":
            print("\n── Add New Expense ──")
            title    = input("Title (e.g. Lunch, Bus fare): ").strip()
            amount   = get_float_input("Amount (₹): ")
            print("Categories: Food | Transport | Shopping | Bills | Health | Other")
            category = input("Category: ").strip().capitalize()
            tracker.add_expense(title, amount, category)

        elif choice == "2":
            tracker.view_expenses()

        elif choice == "3":
            category = input("\nEnter category to filter: ").strip()
            tracker.view_by_category(category)

        elif choice == "4":
            tracker.view_expenses()
            expense_id = get_int_input("Enter ID to delete: ")
            tracker.delete_expense(expense_id)

        elif choice == "5":
            tracker.summary()

        elif choice == "6":
            print("\n Bye! Keep tracking your expenses.\n")
            break

        else:
            print("\n  Invalid choice. Please enter 1-6.\n")


# ============================================================
# Entry point
# This block only runs when you execute this file directly.
# If someone imports this file, main() won't auto-run.
# ============================================================

if __name__ == "__main__":
    main()