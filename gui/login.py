import customtkinter as ctk
from tkinter import messagebox
from database.user_db import UserDB
from utils.session import Session

class LoginPage:

    def __init__(self, app):
        self.app = app
        self.create_widgets()
        self.user_db = UserDB()

# ========================================
# LOGIN UI
# ========================================

    def create_widgets(self):

        self.frame = ctk.CTkFrame(self.app, width=450, height=500)
        self.frame.place(relx=0.5, rely=0.5, anchor="center")

        title = ctk.CTkLabel(
            self.frame,
            text="Login",
            font=("Arial", 28, "bold")
        )
        title.pack(pady=(30,20))

        self.email_entry = ctk.CTkEntry(
            self.frame,
            width=300,
            placeholder_text="Email"
        )
        self.email_entry.pack(pady=15)

        self.password_entry = ctk.CTkEntry(
            self.frame,
            width=300,
            placeholder_text="Password",
            show="*"
        )
        self.password_entry.pack(pady=15)

        login_button = ctk.CTkButton(
            self.frame,
            text="Login",
            width=300,
            command=self.login
        )
        login_button.pack(pady=20)

        department_button = ctk.CTkButton(
            self.frame,
            text="🚓 Department Login",
            width=300,
            command=self.open_department_login
        )
        department_button.pack(pady=(10,10))

        register_button = ctk.CTkButton(
            self.frame,
            text="Register",
            width=300,
            command=self.open_register
        )
        register_button.pack()

# ========================================
# LOGIN
# ========================================

    def login(self):

        email = self.email_entry.get().strip()
        password = self.password_entry.get()

        if email == "" or password == "":
            messagebox.showerror("Error", "Enter Email and Password")
            return

        user = self.user_db.login_user(email, password)

        if user:
            Session.user_id = user[0]
            Session.full_name = user[1]
            Session.email = user[2]
            Session.phone = user[3]
            Session.role = user[5]
            Session.user_type = "Citizen"

            self.frame.destroy()

            from gui.dashboard import Dashboard

            Dashboard(self.app)
        else:
            messagebox.showerror(
                "Login Failed",
                "Invalid Email or Password"
            )

# ========================================
# OPEN REGISTER PAGE
# ========================================

    def open_register(self):
        self.frame.destroy()

        from gui.register import RegisterPage
        RegisterPage(self.app)

# ========================================
# OPEN DEPARTMENT LOGIN
# ========================================

    def open_department_login(self):
        self.frame.destroy()
        from gui.department_login import DepartmentLogin

        DepartmentLogin(self.app)