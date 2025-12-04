import hashlib
from datetime import datetime

class User:
    def __init__(self, username, email, password=None, password_hash=None, user_id=None):
        self.id = user_id
        self.username = username
        self.email = email
        self.created_at = datetime.now()

        # Store password as a hash (for security yay)
        if password_hash:
            self.password_hash = password_hash
        elif password:
            self.password_hash = self._hash_password(password)
        else:
            raise ValueError("Password is required")

    def _hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def verify_password(self, password):
        return self._hash_password(password) == self.password_hash

    def __str__(self):
        return f"User: {self.username}"