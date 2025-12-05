import os
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk

from models import User
from utils import validate_username, validate_email, validate_password


class LoginFrame(ttk.Frame):
    def __init__(self, parent, db_manager, on_login_success):
        super().__init__(parent)

        self.db_manager = db_manager
        self.on_login_success = on_login_success
        self.is_register_mode = False
        self.images = {}
        self._setup_ui()

    def _load_image(self, filename, size=(100, 100)):
        try:
            image_path = os.path.join("images", filename)
            image = Image.open(image_path)
            image = image.resize(size, Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            self.images[filename] = photo
            return photo
        except Exception as e:
            # Print for debugging; fail silently in UI
            print(f"Could not load image {filename}: {e}")
            return None

    def _setup_ui(self):
        container = ttk.Frame(self, padding="40")
        container.pack(expand=True)

        budgie_image = self._load_image("budgie.png", size=(100, 100))
        if budgie_image:
            image_label = ttk.Label(container, image=budgie_image)
            image_label.pack(pady=(0, 15))

        ttk.Label(
            container,
            text="Smart Budgie",
            font=("Helvetica", 24, "bold")
        ).pack(pady=(0, 30))

        self.form_frame = ttk.Frame(container)
        self.form_frame.pack()

        ttk.Label(self.form_frame, text="Username:").pack(anchor="w")
        self.username_entry = ttk.Entry(self.form_frame, width=30)
        self.username_entry.pack(pady=(5, 15))

        self.email_label = ttk.Label(self.form_frame, text="Email:")
        self.email_entry = ttk.Entry(self.form_frame, width=30)

        self.password_label = ttk.Label(self.form_frame, text="Password:")
        self.password_label.pack(anchor="w")
        self.password_entry = ttk.Entry(self.form_frame, width=30, show="*")
        self.password_entry.pack(pady=(5, 15))

        self.confirm_label = ttk.Label(self.form_frame, text="Confirm Password:")
        self.confirm_entry = ttk.Entry(self.form_frame, width=30, show="*")

        self.error_label = ttk.Label(container, text="", foreground="red")
        self.error_label.pack(pady=10)

        self.submit_btn = ttk.Button(container, text="Sign In", command=self._handle_submit)
        self.submit_btn.pack(fill="x", pady=(0, 10))

        self.toggle_btn = ttk.Button(container, text="Create an account", command=self._toggle_mode)
        self.toggle_btn.pack(fill="x")
        self.username_entry.focus()

    def _toggle_mode(self):
        self.is_register_mode = not self.is_register_mode
        self.error_label.config(text="")

        if self.is_register_mode:
            self.submit_btn.config(text="Create Account")
            self.toggle_btn.config(text="Already have an account? Sign in")

            self.password_label.pack_forget()
            self.password_entry.pack_forget()

            self.email_label.pack(anchor="w")
            self.email_entry.pack(pady=(5, 15))

            self.password_label.pack(anchor="w")
            self.password_entry.pack(pady=(5, 15))

            self.confirm_label.pack(anchor="w")
            self.confirm_entry.pack(pady=(5, 15))
        else:
            self.submit_btn.config(text="Sign In")
            self.toggle_btn.config(text="Create an account")

            self.email_label.pack_forget()
            self.email_entry.pack_forget()
            self.confirm_label.pack_forget()
            self.confirm_entry.pack_forget()

        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)
        self.confirm_entry.delete(0, tk.END)
        self.username_entry.focus()

    def _handle_submit(self):
        if self.is_register_mode:
            self._handle_register()
        else:
            self._handle_login()

    def _handle_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()

        if not username or not password:
            self.error_label.config(text="Please enter username and password")
            return

        user = self.db_manager.get_user_by_username(username)

        if user is None:
            self.error_label.config(text="User not found")
            return

        if not user.verify_password(password):
            self.error_label.config(text="Incorrect password")
            return

        self.on_login_success(user)

    def _handle_register(self):
        username = self.username_entry.get().strip()
        email = self.email_entry.get().strip()
        password = self.password_entry.get()
        confirm = self.confirm_entry.get()

        valid, error = validate_username(username)
        if not valid:
            self.error_label.config(text=error)
            return

        valid, error = validate_email(email)
        if not valid:
            self.error_label.config(text=error)
            return

        valid, error = validate_password(password)
        if not valid:
            self.error_label.config(text=error)
            return

        if password != confirm:
            self.error_label.config(text="Passwords do not match")
            return

        if self.db_manager.username_exists(username):
            self.error_label.config(text="Username is already taken")
            return

        if self.db_manager.email_exists(email):
            self.error_label.config(text="Email is already registered")
            return

        try:
            user = User(username=username, email=email, password=password)
            self.db_manager.create_user(user)
            messagebox.showinfo("Success", "Account created! You can now sign in.")
            self._toggle_mode()
            self.username_entry.delete(0, tk.END)
            self.username_entry.insert(0, username)
        except Exception as e:
            self.error_label.config(text=f"Error: {str(e)}")