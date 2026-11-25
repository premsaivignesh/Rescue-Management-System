import sqlite3

class Database:
    def __init__(self):
        self.connection = sqlite3.connect("rescue_management.db")
        self.cursor = self.connection.cursor()

    def close(self):
        self.connection.close()