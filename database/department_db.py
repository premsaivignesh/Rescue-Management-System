from database.database import Database


class DepartmentDB(Database):

# ========================================
# DEPARTMENTS TABLE
# ========================================

    def create_departments_table(self):

        self.cursor.execute("""

        CREATE TABLE IF NOT EXISTS departments(

            department_id INTEGER PRIMARY KEY AUTOINCREMENT,

            department_name TEXT,

            username TEXT UNIQUE,

            password TEXT,

            latitude REAL,

            longitude REAL,

            contact TEXT,

            availability TEXT

        )

        """)

        self.connection.commit()

# ========================================
# DEFAULT DEPARTMENTS
# ========================================

    def insert_default_departments(self):

        departments = [

            (
                "Police",
                "police",
                "police123",
                0,
                0,
                "100",
                "Available"
            ),

            (
                "Ambulance",
                "ambulance",
                "ambulance123",
                0,
                0,
                "108",
                "Available"
            ),

            (
                "Fire",
                "fire",
                "fire123",
                0,
                0,
                "101",
                "Available"
            ),

            (
                "Traffic Police",
                "traffic",
                "traffic123",
                0,
                0,
                "103",
                "Available"
            )

        ]

        for department in departments:

            self.cursor.execute("""

            INSERT OR IGNORE INTO departments(

                department_name,

                username,

                password,

                latitude,

                longitude,

                contact,

                availability

            )

            VALUES(?,?,?,?,?,?,?)

            """,department)

        self.connection.commit()

# ========================================
# LOGIN
# ========================================

    def login(self, username, password):

        self.cursor.execute("""

        SELECT *

        FROM departments

        WHERE username=?

        AND password=?

        """,(username,password))

        return self.cursor.fetchone()