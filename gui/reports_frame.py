import tkinter as tk
from tkinter import ttk
from datetime import datetime

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class ReportsFrame(ttk.Frame):

    def __init__(self, parent, db_manager, user):
        super().__init__(parent)

        self.db_manager = db_manager
        self.user = user

        self._setup_ui()
        self.refresh_charts()

    def _setup_ui(self):
        ttk.Label(self, text="Financial Reports", font=("Helvetica", 18, "bold")).pack(pady=(0, 20))
        self.charts_frame = ttk.Frame(self)
        self.charts_frame.pack(fill="both", expand=True)
        ttk.Button(self, text="Refresh Charts", command=self.refresh_charts).pack(pady=10)

    def refresh_charts(self):
        # Clear existing charts
        for widget in self.charts_frame.winfo_children():
            widget.destroy()

        # 2 subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

        # Spending by category (pie chart)
        spending = self.db_manager.get_spending_by_category(self.user.id, "expense")

        if spending:
            categories = [s[0] for s in spending]
            amounts = [s[1] for s in spending]
            ax1.pie(amounts, labels=categories, autopct='%1.1f%%')
            ax1.set_title("Expenses by Category")
        else:
            ax1.text(0.5, 0.5, "No expense data", ha = 'center', va = 'center')
            ax1.set_title("Expenses by Category")

        # Monthly income vs expenses (bar chart)
        year = datetime.now().year
        monthly = self.db_manager.get_monthly_totals(self.user.id, year)

        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        income_data = [m[1] for m in monthly]
        expense_data = [m[2] for m in monthly]

        x = range(len(months))
        width = 0.35

        ax2.bar([i - width / 2 for i in x], income_data, width, label='Income', color='green')
        ax2.bar([i + width / 2 for i in x], expense_data, width, label='Expenses', color='red')
        ax2.set_xlabel("Month")
        ax2.set_ylabel("Amount ($)")
        ax2.set_title(f"Income vs Expenses ({year})")
        ax2.set_xticks(x)
        ax2.set_xticklabels(months, rotation=45)
        ax2.legend()

        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, self.charts_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)