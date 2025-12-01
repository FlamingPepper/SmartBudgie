import sqlite3
from datetime import datetime
from models import User, Income, Expense, Category

# database for users, transactions, amd all their functions

class DatabaseManager:
    def __init__(self, db_path="budget_app.db"):
        self.db_path = db_path
        self._create_tables()
        self._add_default_categories()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _create_tables(self):
        conn = self._get_connection()
        cursor = conn.cursor()

        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)

        # Categories table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category_type TEXT NOT NULL,
                icon TEXT DEFAULT '',
                UNIQUE(name, category_type)
            )
        """)

        # Transactions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                description TEXT,
                date TEXT NOT NULL,
                transaction_type TEXT NOT NULL,
                extra_info TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)

        conn.commit()
        conn.close()

    def _add_default_categories(self):
        """Add default categories to database."""
        conn = self._get_connection()
        cursor = conn.cursor()

        for name, icon in Category.DEFAULT_EXPENSE_CATEGORIES:
            cursor.execute(
                "INSERT OR IGNORE INTO categories (name, category_type, icon) VALUES (?, ?, ?)",
                (name, "expense", icon)
            )

        for name, icon in Category.DEFAULT_INCOME_CATEGORIES:
            cursor.execute(
                "INSERT OR IGNORE INTO categories (name, category_type, icon) VALUES (?, ?, ?)",
                (name, "income", icon)
            )

        conn.commit()
        conn.close()

    # user methods

    # create user
    def create_user(self, user):
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO users (username, email, password_hash, created_at) VALUES (?, ?, ?, ?)",
            (user.username, user.email, user.password_hash, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )

        user.id = cursor.lastrowid
        conn.commit()
        conn.close()
        return user.id

    # find user
    def get_user_by_username(self, username):
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return User(
                username=row["username"],
                email=row["email"],
                password_hash=row["password_hash"],
                user_id=row["id"]
            )
        return None

    # hadling unique usernames
    def username_exists(self, username):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM users WHERE username = ? ", (username,))
        result = cursor.fetchone() is not None
        conn.close()
        return result

    # handling unique emails
    def email_exists(self, email):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM users WHERE email = ?", (email,))
        result = cursor.fetchone() is not None
        conn.close()
        return result

    # create transaction
    def add_transaction(self, transaction):
        conn = self._get_connection()
        cursor = conn.cursor()

        # Get extra info based on type
        if isinstance(transaction, Income):
            extra_info = transaction.source
        else:
            extra_info = transaction.payment_method

        cursor.execute("""
            INSERT INTO transactions (user_id, amount, category, description, date, transaction_type, extra_info)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            transaction.user_id,
            transaction.amount,
            transaction.category,
            transaction.description,
            transaction.date.strftime("%Y-%m-%d %H:%M:%S"),
            transaction.transaction_type,
            extra_info
        ))

        transaction.id = cursor.lastrowid
        conn.commit()
        conn.close()
        return transaction.id

    # gets all transactions for that user
    def get_transactions_for_user(self, user_id, start_date=None, end_date=None, transaction_type=None):
        conn = self._get_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM transactions WHERE user_id = ?"
        params = [user_id]

        if start_date:
            query += " AND date >= ?"
            params.append(start_date.strftime("%Y-%m-%d 00:00:00"))

        if end_date:
            query += " AND date <= ?"
            params.append(end_date.strftime("%Y-%m-%d 23:59:59"))

        if transaction_type:
            query += " AND transaction_type = ?"
            params.append(transaction_type)

        query += " ORDER BY date DESC"

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        transactions = []
        for row in rows:
            date = datetime.strptime(row["date"], "%Y-%m-%d %H:%M:%S")

            if row["transaction_type"] == "income":
                t = Income(
                    amount=row["amount"],
                    category=row["category"],
                    source=row["extra_info"] or "",
                    description=row["description"] or "",
                    date=date,
                    transaction_id=row["id"],
                    user_id=row["user_id"]
                )
            else:
                t = Expense(
                    amount=row["amount"],
                    category=row["category"],
                    payment_method=row["extra_info"] or "Cash",
                    description=row["description"] or "",
                    date=date,
                    transaction_id=row["id"],
                    user_id=row["user_id"]
                )
            transactions.append(t)

        return transactions

    # delete transaction
    def delete_transaction(self, transaction_id):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM transactions WHERE id = ?", (transaction_id,))
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return deleted

    # update transaction
    def update_transaction(self, transaction):
        conn = self._get_connection()
        cursor = conn.cursor()

        # Get extra info based on type
        if isinstance(transaction, Income):
            extra_info = transaction.source
        else:
            extra_info = transaction.payment_method

        cursor.execute("""
            UPDATE transactions
            SET amount = ?, category = ?, description = ?, date = ?, extra_info = ? 
            WHERE id = ? 
        """, (
            transaction.amount,
            transaction.category,
            transaction.description,
            transaction.date.strftime("%Y-%m-%d %H:%M:%S"),
            extra_info,
            transaction.id
        ))

        conn.commit()
        conn.close()
        return cursor.rowcount > 0

    # get and grouping transactions with category
    def get_spending_by_category(self, user_id, transaction_type="expense"):
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT category, SUM(amount) as total
            FROM transactions
            WHERE user_id = ? AND transaction_type = ?
            GROUP BY category
            ORDER BY total DESC
        """, (user_id, transaction_type))

        results = [(row["category"], row["total"]) for row in cursor.fetchall()]
        conn.close()
        return results

    # get and group by month
    def get_monthly_totals(self, user_id, year):
        conn = self._get_connection()
        cursor = conn.cursor()

        results = []
        for month in range(1, 13):
            # Get income
            cursor.execute("""
                SELECT COALESCE(SUM(amount), 0) as total FROM transactions
                WHERE user_id = ? AND transaction_type = 'income'
                AND strftime('%Y', date) = ?  AND strftime('%m', date) = ?
            """, (user_id, str(year), f"{month:02d}"))
            income = cursor.fetchone()["total"]

            # Get expenses
            cursor.execute("""
                SELECT COALESCE(SUM(amount), 0) as total FROM transactions
                WHERE user_id = ? AND transaction_type = 'expense'
                AND strftime('%Y', date) = ? AND strftime('%m', date) = ?
            """, (user_id, str(year), f"{month:02d}"))
            expense = cursor.fetchone()["total"]

            results.append((month, income, expense))

        conn.close()
        return results

    # get defined categories
    def get_categories(self, category_type=None):
        conn = self._get_connection()
        cursor = conn.cursor()

        if category_type:
            cursor.execute("SELECT * FROM categories WHERE category_type = ?  ORDER BY name", (category_type,))
        else:
            cursor.execute("SELECT * FROM categories ORDER BY name")

        categories = [
            Category(
                name=row["name"],
                category_type=row["category_type"],
                icon=row["icon"],
                category_id=row["id"]
            )
            for row in cursor.fetchall()
        ]
        conn.close()
        return categories