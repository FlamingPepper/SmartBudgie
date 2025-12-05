import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from models import Income, Expense
from utils import validate_amount

class TransactionFrame(ttk.Frame):
    def __init__(self, parent, db_manager, user, on_transaction_added=None):
        super().__init__(parent)

        self.db_manager = db_manager
        self.user = user
        self.on_transaction_added = on_transaction_added

        # if user is editing a transaction or not
        self.editing_transaction = None

        self._setup_ui()
        self._load_transactions()

    def _setup_ui(self):
        # Left side - Add/Edit form
        self.form_frame = ttk.LabelFrame(self, text="Add Transaction", padding=15)
        self.form_frame.pack(side="left", fill="y", padx=(0, 10))

        # Transaction type
        ttk.Label(self.form_frame, text="Type:").pack(anchor="w")
        self.type_var = tk.StringVar(value="expense")

        type_frame = ttk.Frame(self.form_frame)
        type_frame.pack(fill="x", pady=(5, 15))

        self.expense_radio = ttk.Radiobutton(type_frame, text="Expense", variable=self.type_var,
                                             value="expense", command=self._on_type_change)
        self.expense_radio.pack(side="left")
        self.income_radio = ttk.Radiobutton(type_frame, text="Income", variable=self.type_var,
                                            value="income", command=self._on_type_change)
        self.income_radio.pack(side="left", padx=(20, 0))

        # Amount
        ttk.Label(self.form_frame, text="Amount ($):").pack(anchor="w")
        self.amount_entry = ttk.Entry(self.form_frame)
        self.amount_entry.pack(fill="x", pady=(5, 15))

        # Category
        ttk.Label(self.form_frame, text="Category:").pack(anchor="w")
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(self.form_frame, textvariable=self.category_var, state="readonly")
        self.category_combo.pack(fill="x", pady=(5, 15))
        self._load_categories()

        # Date
        ttk.Label(self.form_frame, text="Date (YYYY-MM-DD):").pack(anchor="w")
        self.date_entry = ttk.Entry(self.form_frame)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.date_entry.pack(fill="x", pady=(5, 15))

        # Payment method / Source
        self.extra_label = ttk.Label(self.form_frame, text="Payment Method:")
        self.extra_label.pack(anchor="w")
        self.extra_var = tk.StringVar()
        self.extra_combo = ttk.Combobox(self.form_frame, textvariable=self.extra_var, state="readonly")
        self.extra_combo["values"] = Expense.PAYMENT_METHODS
        self.extra_combo.set("Cash")
        self.extra_combo.pack(fill="x", pady=(5, 15))

        # Description
        ttk.Label(self.form_frame, text="Description:").pack(anchor="w")
        self.desc_entry = ttk.Entry(self.form_frame)
        self.desc_entry.pack(fill="x", pady=(5, 15))

        # Error label
        self.error_label = ttk.Label(self.form_frame, text="", foreground="red")
        self.error_label.pack(pady=5)

        # Buttons frame
        buttons_frame = ttk.Frame(self.form_frame)
        buttons_frame.pack(fill="x")

        # Add/Save button
        self.submit_btn = ttk.Button(buttons_frame, text="Add Transaction", command=self._save_transaction)
        self.submit_btn.pack(fill="x", pady=(0, 5))

        # Cancel edit button (hidden initially)
        self.cancel_btn = ttk.Button(buttons_frame, text="Cancel Edit", command=self._cancel_edit)

        # Right side - Transaction list
        right_frame = ttk.LabelFrame(self, text="All Transactions", padding=10)
        right_frame.pack(side="right", fill="both", expand=True)

        # Filter
        filter_frame = ttk.Frame(right_frame)
        filter_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(filter_frame, text="Filter:").pack(side="left")
        self.filter_var = tk.StringVar(value="all")
        ttk.Radiobutton(filter_frame, text="All", variable=self.filter_var,
                        value="all", command=self._load_transactions).pack(side="left", padx=5)
        ttk.Radiobutton(filter_frame, text="Income", variable=self.filter_var,
                        value="income", command=self._load_transactions).pack(side="left", padx=5)
        ttk.Radiobutton(filter_frame, text="Expenses", variable=self.filter_var,
                        value="expense", command=self._load_transactions).pack(side="left", padx=5)

        # Edit and Delete buttons
        ttk.Button(filter_frame, text="Edit Selected", command=self._edit_selected).pack(side="right", padx=(5, 0))
        ttk.Button(filter_frame, text="Delete Selected", command=self._delete_selected).pack(side="right")

        # Transactions list
        columns = ("id", "date", "type", "category", "description", "amount")
        self.tree = ttk.Treeview(right_frame, columns=columns, show="headings")

        self.tree.heading("id", text="ID")
        self.tree.heading("date", text="Date")
        self.tree.heading("type", text="Type")
        self.tree.heading("category", text="Category")
        self.tree.heading("description", text="Description")
        self.tree.heading("amount", text="Amount")

        self.tree.column("id", width=40)
        self.tree.column("date", width=100)
        self.tree.column("type", width=70)
        self.tree.column("category", width=120)
        self.tree.column("description", width=150)
        self.tree.column("amount", width=80)

        # Double-click to edit
        self.tree.bind("<Double-1>", lambda e: self._edit_selected())

        scrollbar = ttk.Scrollbar(right_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _on_type_change(self):
        self._load_categories()
        if self.type_var.get() == "income":
            self.extra_label.config(text="Source:")
            self.extra_combo["values"] = ["Job", "Freelance", "Gift", "Other"]
            self.extra_combo.set("Job")
        else:
            self.extra_label.config(text="Payment Method:")
            self.extra_combo["values"] = Expense.PAYMENT_METHODS
            self.extra_combo.set("Cash")

    def _load_categories(self):
        categories = self.db_manager.get_categories(self.type_var.get())
        self.category_combo["values"] = [c.name for c in categories]
        if categories:
            self.category_combo.set(categories[0].name)

    def _load_transactions(self):
        # Clear list
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Get filter
        filter_type = self.filter_var.get()
        if filter_type == "all":
            filter_type = None

        # Load from database
        transactions = self.db_manager.get_transactions_for_user(
            self.user.id,
            transaction_type=filter_type
        )

        # Add to list
        for t in transactions:
            info = t.get_display_info()
            self.tree.insert("", "end", values=(
                t.id,
                info["date"],
                info["type"],
                info["category"],
                t.description[:20] if t.description else "",
                info["amount"]
            ))

    def _save_transaction(self):
        # Validate amount
        valid, error, amount = validate_amount(self.amount_entry.get())
        if not valid:
            self.error_label.config(text=error)
            return

        # Get values
        category = self.category_var.get()
        description = self.desc_entry.get()
        extra = self.extra_var.get()

        try:
            date = datetime.strptime(self.date_entry.get(), "%Y-%m-%d")
        except ValueError:
            self.error_label.config(text="Invalid date format")
            return

        # Create transaction object
        if self.type_var.get() == "income":
            transaction = Income(
                amount=amount,
                category=category,
                source=extra,
                description=description,
                date=date,
                user_id=self.user.id
            )
        else:
            transaction = Expense(
                amount=amount,
                category=category,
                payment_method=extra,
                description=description,
                date=date,
                user_id=self.user.id
            )

        # Check if editing or adding new
        if self.editing_transaction:
            # Update existing
            transaction.id = self.editing_transaction.id
            self.db_manager.update_transaction(transaction)
            messagebox.showinfo("Success", "Transaction updated!")
            self._cancel_edit()
        else:
            # Add new
            self.db_manager.add_transaction(transaction)
            messagebox.showinfo("Success", "Transaction added!")
            self._clear_form()

        # Refresh list
        self._load_transactions()

        # Notify callback
        if self.on_transaction_added:
            self.on_transaction_added()

    def _edit_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a transaction to edit")
            return

        # Get transaction ID from selected row
        item = self.tree.item(selected[0])
        transaction_id = item["values"][0]

        # Find the transaction in database
        transactions = self.db_manager.get_transactions_for_user(self.user.id)
        transaction = None
        for t in transactions:
            if t.id == transaction_id:
                transaction = t
                break

        if not transaction:
            messagebox.showerror("Error", "Transaction not found")
            return

        # Store reference to editing transaction
        self.editing_transaction = transaction

        # Update form title
        self.form_frame.config(text="Edit Transaction")

        # Change button text
        self.submit_btn.config(text="Save Changes")

        # Show cancel button
        self.cancel_btn.pack(fill="x")

        # Disable type change while editing (can't change income to expense)
        self.expense_radio.config(state="disabled")
        self.income_radio.config(state="disabled")

        # Fill form with transaction data
        self.type_var.set(transaction.transaction_type)
        self._on_type_change()

        # Clear and fill fields
        self.amount_entry.delete(0, tk.END)
        self.amount_entry.insert(0, str(transaction.amount))

        self.category_var.set(transaction.category)

        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, transaction.date.strftime("%Y-%m-%d"))

        if transaction.transaction_type == "income":
            self.extra_var.set(transaction.source)
        else:
            self.extra_var.set(transaction.payment_method)

        self.desc_entry.delete(0, tk.END)
        self.desc_entry.insert(0, transaction.description)

        self.error_label.config(text="")

    def _cancel_edit(self):
        self.editing_transaction = None

        # Reset form title
        self.form_frame.config(text="Add Transaction")

        # Reset button text
        self.submit_btn.config(text="Add Transaction")

        # Hide cancel button
        self.cancel_btn.pack_forget()

        # Re-enable type selection
        self.expense_radio.config(state="normal")
        self.income_radio.config(state="normal")

        # Clear form
        self._clear_form()

    def _clear_form(self):
        self.amount_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.error_label.config(text="")
        self.type_var.set("expense")
        self._on_type_change()

    def _delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a transaction to delete")
            return

        if messagebox.askyesno("Confirm", "Are you sure you want to delete this transaction?"):
            item = self.tree.item(selected[0])
            transaction_id = item["values"][0]
            self.db_manager.delete_transaction(transaction_id)
            self._load_transactions()

            # Cancel edit if deleting the one being edited
            if self.editing_transaction and self.editing_transaction.id == transaction_id:
                self._cancel_edit()

            if self.on_transaction_added:
                self.on_transaction_added()