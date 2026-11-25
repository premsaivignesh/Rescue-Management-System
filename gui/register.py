import customtkinter as ctk
import re
from tkinter import messagebox
from database.user_db import UserDB


class RegisterPage:

    def __init__(self, app):
        self.app = app
        self.user_db = UserDB()
        self.create_widgets()

# ========================================
# REGISTER UI
# ========================================

    def create_widgets(self):

        self.frame = ctk.CTkFrame(self.app)
        self.frame.place(relx=0.5, rely=0.5, anchor="center")

        title = ctk.CTkLabel(
            self.frame,
            text="Create Account",
            font=("Arial", 28, "bold")
        )
        title.pack(pady=15)

        self.name_entry = ctk.CTkEntry(
            self.frame,
            width=320,
            placeholder_text="Full Name"
        )
        self.name_entry.pack(pady=5)

        self.email_entry = ctk.CTkEntry(
            self.frame,
            width=320,
            placeholder_text="Email"
        )
        self.email_entry.pack(pady=5)

        self.phone_entry = ctk.CTkEntry(
            self.frame,
            width=320,
            placeholder_text="Phone Number"
        )
        self.phone_entry.pack(pady=5)

        self.password_entry = ctk.CTkEntry(
            self.frame,
            width=320,
            placeholder_text="Password",
            show="*"
        )
        self.password_entry.pack(pady=5)

        self.confirm_entry = ctk.CTkEntry(
            self.frame,
            width=320,
            placeholder_text="Confirm Password",
            show="*"
        )
        self.confirm_entry.pack(pady=5)

        self.role_menu = ctk.CTkOptionMenu(
            self.frame,
            values=[
                "Citizen",
                "Police",
                "Ambulance",
                "Fire Department",
                "Traffic Police",
                "Admin"
            ]
        )
        self.role_menu.pack(pady=10)

        register_button = ctk.CTkButton(
            self.frame,
            text="Register",
            width=320,
            command=self.register_user
        )
        register_button.pack(pady=15)

        back_button = ctk.CTkButton(
            self.frame,
            text="Back to Login",
            width=320,
            fg_color="gray",
            command=self.back_to_login
        )
        back_button.pack(pady=(10, 20))

# ========================================
# BACK TO LOGIN
# ========================================

    def back_to_login(self):
        self.frame.destroy()

        from gui.login import LoginPage
        LoginPage(self.app)

# ========================================
# REGISTER USER
# ========================================

    def register_user(self):

        full_name = self.name_entry.get().strip()
        email = self.email_entry.get().strip()
        phone = self.phone_entry.get().strip()
        password = self.password_entry.get()
        confirm = self.confirm_entry.get()
        role = self.role_menu.get()

        if "" in [full_name, email, phone, password, confirm]:
            messagebox.showerror("Error", "All fields are required")
            return

        if not re.fullmatch(r"[A-Za-z0-9._%+-]+@gmail\.com", email):
            messagebox.showerror("Error", "Enter a valid Gmail address")
            return

        if not phone.isdigit() or len(phone) != 10:
            messagebox.showerror("Error", "Phone number must contain exactly 10 digits")
            return

        if not full_name.replace(" ", "").isalpha():
            messagebox.showerror("Error", "Name should contain only alphabets")
            return

        if len(password) < 8:
            messagebox.showerror("Error", "Password must be at least 8 characters")
            return

        if not re.search(r"[A-Z]", password):
            messagebox.showerror("Error", "Password must contain one uppercase letter")
            return

        if not re.search(r"[a-z]", password):
            messagebox.showerror("Error", "Password must contain one lowercase letter")
            return

        if not re.search(r"[0-9]", password):
            messagebox.showerror("Error", "Password must contain one number")
            return

        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            messagebox.showerror("Error", "Password must contain one special character")
            return

        if password != confirm:
            messagebox.showerror("Error", "Passwords do not match")
            return

        try:
            self.user_db.register_user(
                full_name,
                email,
                phone,
                password,
                role
            )

            messagebox.showinfo("Success", "Registration Successful")

        except Exception:
            messagebox.showerror("Error", "Email or Phone Number already exists")