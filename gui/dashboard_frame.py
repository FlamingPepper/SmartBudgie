import tkinter as tk
from tkinter import ttk
from datetime import datetime


class DashboardFrame(ttk.Frame):
    def __init__(self, parent, db_manager, user):
        super().__init__(parent)

        self.db_manager = db_manager
        self.user = user

        self._setup_ui()
        self.refresh_data()

    def _setup_ui(self):
        # Welcome message
        ttk.Label(
            self,
            text=f"Welcome, {self.user.username}!",
            font=("Helvetica", 18, "bold")
        ).pack(anchor="w", pady=(0, 5))

        ttk.Label(
            self,
            text=datetime.now().strftime("%A, %B %d, %Y")
        ).pack(anchor="w", pady=(0, 20))

        # Summary cards frame
        cards = ttk.Frame(self)
        cards.pack(fill="x", pady=(0, 20))

        # Balance card
        balance_frame = ttk.LabelFrame(cards, text="Balance", padding=15)
        balance_frame.pack(side="left", expand=True, fill="both", padx=(0, 10))

        self.balance_label = ttk.Label(balance_frame, text="$0.00", font=("Helvetica", 20, "bold"))
        self.balance_label.pack()

        # Income card
        income_frame = ttk.LabelFrame(cards, text="Income", padding=15)
        income_frame.pack(side="left", expand=True, fill="both", padx=5)

        self.income_label = ttk.Label(income_frame, text="$0.00", font=("Helvetica", 20, "bold"), foreground="green")
        self.income_label.pack()

        # Expense card
        expense_frame = ttk.LabelFrame(cards, text="Expenses", padding=15)
        expense_frame.pack(side="left", expand=True, fill="both", padx=(10, 0))

        self.expense_label = ttk.Label(expense_frame, text="$0.00", font=("Helvetica", 20, "bold"), foreground="red")
        self.expense_label.pack()

        # Recent transactions
        ttk.Label(self, text="Recent Transactions", font=("Helvetica", 14, "bold")).pack(anchor="w", pady=(10, 5))

        # Transactions list
        columns = ("date", "type", "category", "amount")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=10)

        self.tree.heading("date", text="Date")
        self.tree.heading("type", text="Type")
        self.tree.heading("category", text="Category")
        self.tree.heading("amount", text="Amount")

        self.tree.column("date", width=100)
        self.tree.column("type", width=80)
        self.tree.column("category", width=150)
        self.tree.column("amount", width=100)

        self.tree.pack(fill="both", expand=True)

    def refresh_data(self):
        # Get this month's transactions
        today = datetime.now()
        start_of_month = today.replace(day=1, hour=0, minute=0, second=0)

        transactions = self.db_manager.get_transactions_for_user(
            self.user.id,
            start_date=start_of_month
        )

        # Calculate totals
        total_income = sum(t.amount for t in transactions if t.transaction_type == "income")
        total_expenses = sum(t.amount for t in transactions if t.transaction_type == "expense")
        balance = total_income - total_expenses

        # Update labels
        if balance >= 0:
            self.balance_label.config(text=f"${balance:.2f}", foreground="green")
        else:
            self.balance_label.config(text=f"-${abs(balance):.2f}", foreground="red")

        self.income_label.config(text=f"${total_income:.2f}")
        self.expense_label.config(text=f"${total_expenses:.2f}")

        # Update transactions list
        for item in self.tree.get_children():
            self.tree.delete(item)

        for t in transactions[:10]:
            info = t.get_display_info()
            self.tree.insert("", "end", values=(
                info["date"],
                info["type"],
                info["category"],
                info["amount"]
            ))