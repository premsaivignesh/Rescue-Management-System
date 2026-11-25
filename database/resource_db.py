from database.database import Database


class ResourceDB(Database):

# ========================================
# RESOURCES TABLE
# ========================================

    def create_resources_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS resources(
            resource_id INTEGER PRIMARY KEY AUTOINCREMENT,
            resource_name TEXT,
            resource_type TEXT,
            latitude REAL,
            longitude REAL,
            availability TEXT
        )
        """
        self.cursor.execute(query)
        self.connection.commit()

# ========================================
# RESOURCE FUNCTIONS
# ========================================

    def add_resource(self, values):
        query = """
        INSERT INTO resources(
        resource_name,
        resource_type,
        latitude,
        longitude,
        availability)
        VALUES(?,?,?,?,?)
        """
        self.cursor.execute(query, values)
        self.connection.commit()

    def get_available_resources(self):
        self.cursor.execute(
            "SELECT * FROM resources WHERE availability='Available'"
        )
        return self.cursor.fetchall()