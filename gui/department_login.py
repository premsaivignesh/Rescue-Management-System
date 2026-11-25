import customtkinter as ctk
from database.department_db import DepartmentDB
from utils.session import Session

class DepartmentLogin:

    def __init__(self, app):
        self.app = app
        self.db = DepartmentDB()
        for widget in self.app.winfo_children():
            widget.destroy()
        self.create_ui()

# ========================================
# UI
# ========================================

    def create_ui(self):
        title = ctk.CTkLabel(
            self.app,
            text="Department Login",
            font=("Arial",30,"bold")
        )
        title.pack(pady=40)
        
        self.username = ctk.CTkEntry(
            self.app,
            width=300,
            placeholder_text="Username"
        )
        self.username.pack(pady=10)
        
        self.password = ctk.CTkEntry(
            self.app,
            width=300,
            show="*",
            placeholder_text="Password"
        )
        self.password.pack(pady=10)

        ctk.CTkButton(
            self.app,
            text="Login",
            width=220,
            command=self.login
        ).pack(pady=20)

        ctk.CTkButton(
            self.app,
            text="← Back",
            width=220,
            command=self.back
        ).pack()

        self.message = ctk.CTkLabel(
            self.app,
            text=""
        )
        self.message.pack(pady=15)

# ========================================
# LOGIN
# ========================================

    def login(self):
        user = self.db.login(
            self.username.get(),
            self.password.get()
        )

        if user:
            Session.user_type = "Department"

            Session.department_id = user[0]

            Session.department_name = user[1]

            Session.department_username = user[2]

            from gui.department_dashboard import DepartmentDashboard
            
            DepartmentDashboard(self.app, user)
        else:
            self.message.configure(
                text="Invalid Username or Password",
                text_color="red"
            )

# ========================================
# BACK
# ========================================

    def back(self):
        from gui.login import LoginPage

        LoginPage(self.app)