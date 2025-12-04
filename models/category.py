class Category:

    DEFAULT_EXPENSE_CATEGORIES = [
        ("Food & Dining", ""),
        ("Transportation", ""),
        ("Shopping", ""),
        ("Entertainment", ""),
        ("Bills & Utilities", ""),
        ("Healthcare", ""),
        ("Other", "")
    ]

    DEFAULT_INCOME_CATEGORIES = [
        ("Salary", ""),
        ("Freelance", ""),
        ("Investments", ""),
        ("Gifts", ""),
        ("Other", "")
    ]

    def __init__(self, name, category_type, icon="", category_id=None):
        self.id = category_id
        self.name = name
        self.category_type = category_type
        self.icon = icon

    def __str__(self):
        if self.icon:
            return f"{self.icon} {self.name}"
        return self.name