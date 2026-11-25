from database.database import Database


class UserDB(Database):

# ========================================
# USERS TABLE
# ========================================

    def create_users_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS users(
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            latitude REAL,
            longitude REAL
        )
        """
        self.cursor.execute(query)
        self.connection.commit()

# ========================================
# USER FUNCTIONS
# ========================================

    def register_user(self, full_name, email, phone, password, role):
        query = """
        INSERT INTO users(full_name,email,phone,password,role)
        VALUES(?,?,?,?,?)
        """
        self.cursor.execute(query, (full_name, email, phone, password, role))
        self.connection.commit()

    def login_user(self, email, password):
        query = """
        SELECT * FROM users
        WHERE email=? AND password=?
        """
        self.cursor.execute(query, (email, password))
        return self.cursor.fetchone()

    def get_all_users(self):
        self.cursor.execute("SELECT * FROM users")
        return self.cursor.fetchall()
    def update_user_profile(self, user_id, full_name, email, phone):
        self.cursor.execute(
            "UPDATE users SET full_name=?, email=?, phone=? WHERE user_id=?",
            (full_name, email, phone, user_id)
        )
        self.connection.commit()
