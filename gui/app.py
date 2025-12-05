import tkinter as tk
from tkinter import ttk

from database import DatabaseManager
from gui.login_frame import LoginFrame
from gui.dashboard_frame import DashboardFrame
from gui.transaction_frame import TransactionFrame
from gui.reports_frame import ReportsFrame


class BudgetApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Budget Tracker")
        self.root.geometry("1000x700")

        # Initialize database
        self.db_manager = DatabaseManager()

        # Current user
        self.current_user = None

        # Main container
        self.main_frame = ttk.Frame(self.root, padding=10)
        self.main_frame.pack(fill="both", expand=True)

        # Show login screen
        self._show_login()

    def _show_login(self):
        self._clear_main_frame()

        login_frame = LoginFrame(
            self.main_frame,
            self.db_manager,
            self._on_login_success
        )
        login_frame.pack(fill="both", expand=True)

    def _on_login_success(self, user):
        self.current_user = user
        self._show_main_app()

    def _show_main_app(self):
        self._clear_main_frame()

        # Create notebook (tabs)
        notebook = ttk.Notebook(self.main_frame)
        notebook.pack(fill="both", expand=True)

        # Dashboard tab
        self.dashboard = DashboardFrame(notebook, self.db_manager, self.current_user)
        notebook.add(self.dashboard, text="Dashboard")

        # Transactions tab
        self.transactions = TransactionFrame(
            notebook,
            self.db_manager,
            self.current_user,
            on_transaction_added=self._refresh_dashboard
        )
        notebook.add(self.transactions, text="Transactions")

        # Reports tab
        self.reports = ReportsFrame(notebook, self.db_manager, self.current_user)
        notebook.add(self.reports, text="Reports")

        # Logout button
        logout_frame = ttk.Frame(self.main_frame)
        logout_frame.pack(fill="x", pady=(10, 0))

        ttk.Button(logout_frame, text="Logout", command=self._logout).pack(side="right")

    def _refresh_dashboard(self):
        self.dashboard.refresh_data()

    def _logout(self):
        self.current_user = None
        self._show_login()

    def _clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def run(self):
        self.root.mainloop()