"""User model for the budget application."""

import hashlib
from datetime import datetime


class User:
    """Represents a user in the system."""

    def __init__(self, username, email, password=None, password_hash=None, user_id=None):
        self.id = user_id
        self.username = username
        self.email = email
        self.created_at = datetime.now()

        # Store password as a hash (never plain text)
        if password_hash:
            self.password_hash = password_hash
        elif password:
            self.password_hash = self._hash_password(password)
        else:
            raise ValueError("Password is required")

    def _hash_password(self, password):
        """Convert password to a secure hash."""
        return hashlib.sha256(password.encode()).hexdigest()

    def verify_password(self, password):
        """Check if the provided password is correct."""
        return self._hash_password(password) == self.password_hash

    def __str__(self):
        return f"User: {self.username}"