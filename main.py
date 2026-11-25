# om gam ganapataye namaha
#    success on the way
#         get redy 


import customtkinter as ctk
from database.database import Database
from database.setup_database import initialize_database
from gui.login import LoginPage

class RescueManagementSystem:

    def __init__(self):

        initialize_database()

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")

        self.app = ctk.CTk()

        self.app.title("AI Disaster & Emergency Rescue Management System")

        self.app.geometry("1400x850")
        self.app.minsize(1100, 700)
        self.app.configure(fg_color="#10130D")

        LoginPage(self.app)

        self.app.mainloop()

    def create_home_page(self):

        title = ctk.CTkLabel(
            self.app,
            text="AI Disaster & Emergency\nRescue Management System",
            font=("Arial",30,"bold")
        )

        title.pack(pady=(80,20))

        subtitle = ctk.CTkLabel(
            self.app,
            text="Intelligent Emergency Response System",
            font=("Arial",18)
        )

        subtitle.pack()

        start = ctk.CTkButton(
            self.app,
            text="Start Application",
            width=220,
            height=45,
            command=self.start_application
        )

        start.pack(pady=40)

    def start_application(self):
        print("Application Started")

if __name__ == "__main__":
    RescueManagementSystem()