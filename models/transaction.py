from datetime import datetime

class Transaction:
    def __init__(self, amount, category, description="", date=None, transaction_id=None, user_id=None):
        if amount <= 0:
            raise ValueError("Amount must be greater than zero")

        self.id = transaction_id
        self.user_id = user_id
        self.amount = round(amount, 2)
        self.category = category
        self.description = description
        self.date = date if date else datetime.now()

    def __str__(self):
        return f"{self.transaction_type}: ${self.amount:.2f} - {self.category}"

# shown as a positive numebr when indicating income
class Income(Transaction):
    def __init__(self, amount, category, source="", description="", date=None, transaction_id=None, user_id=None):
        super().__init__(amount, category, description, date, transaction_id, user_id)
        self.source = source
        self.transaction_type = "income"

    def get_signed_amount(self):
        return self.amount

    def get_display_info(self):
        return {
            "type": "Income",
            "amount": f"+${self.amount:.2f}",
            "color": "green",
            "category": self.category,
            "date": self.date.strftime("%Y-%m-%d"),
            "description": self.description
        }

# shown as a negative number when indicating expense
class Expense(Transaction):
    PAYMENT_METHODS = ["Cash", "Credit Card", "Debit Card", "Bank Transfer", "Other"]

    def __init__(self, amount, category, payment_method="Cash", description="", date=None, transaction_id=None,
                 user_id=None):
        super().__init__(amount, category, description, date, transaction_id, user_id)
        self.payment_method = payment_method
        self.transaction_type = "expense"

    def get_signed_amount(self):
        return -self.amount

    def get_display_info(self):
        return {
            "type": "Expense",
            "amount": f"-${self.amount:.2f}",
            "color": "red",
            "category": self.category,
            "date": self.date.strftime("%Y-%m-%d"),
            "description": self.description
        }