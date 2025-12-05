import re

def validate_username(username):
    if not username:
        return False, "Username is required"

    if len(username) < 3:
        return False, "Username must be at least 3 characters"

    if len(username) > 20:
        return False, "Username must be at most 20 characters"

    if not username[0].isalpha():
        return False, "Username must start with a letter"

    if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', username):
        return False, "Username can only contain letters, numbers, and underscores"

    return True, ""


def validate_email(email):
    if not email:
        return False, "Email is required"

    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    if not re.match(pattern, email):
        return False, "Please enter a valid email address"

    return True, ""


def validate_password(password):
    if not password:
        return False, "Password is required"

    if len(password) < 6:
        return False, "Password must be at least 6 characters"

    return True, ""


def validate_amount(amount_str):
    if not amount_str:
        return False, "Amount is required", 0.0

    # Clean up the input
    cleaned = amount_str.strip().replace("$", "").replace(",", "")

    try:
        amount = float(cleaned)
    except ValueError:
        return False, "Please enter a valid number", 0.0

    if amount <= 0:
        return False, "Amount must be greater than zero", 0.0

    return True, "", round(amount, 2)