from database.database import Database


class IncidentDB(Database):

# ========================================
# INCIDENT TABLE
# ========================================

    def create_incidents_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS incidents(
            incident_id TEXT PRIMARY KEY,
            user_id INTEGER,
            incident_type TEXT,
            description TEXT,
            address TEXT,
            image_path TEXT,
            video_path TEXT,
            latitude REAL,
            longitude REAL,
            severity TEXT,
            status TEXT,
            people_estimated INTEGER,
            ambulance_required INTEGER,
            police_required INTEGER,
            fire_engine_required INTEGER,
            department_assigned TEXT,
            priority_score INTEGER DEFAULT 0,
            ai_status TEXT,
            report_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        self.cursor.execute(query)
        self.connection.commit()

    def ensure_ai_columns(self):
        """Migrate older databases without changing existing column order."""
        existing = {row[1] for row in self.cursor.execute("PRAGMA table_info(incidents)").fetchall()}
        columns = {
            "ai_incident_type": "TEXT",
            "ai_incident_confidence": "REAL DEFAULT 0",
            "ai_severity_confidence": "REAL DEFAULT 0",
            "spam_result": "TEXT",
            "spam_confidence": "REAL DEFAULT 0",
            "visual_reliability": "REAL DEFAULT 0",
            "vehicle_count": "INTEGER DEFAULT 0",
            "motorcycle_count": "INTEGER DEFAULT 0",
            "ai_summary": "TEXT",
            "ai_result_json": "TEXT",
        }
        for name, spec in columns.items():
            if name not in existing:
                self.cursor.execute(f"ALTER TABLE incidents ADD COLUMN {name} {spec}")
        self.connection.commit()

    def update_multimodal_ai_result(self, incident_id, result_json, incident_type, incident_confidence, severity, severity_confidence, spam_result, spam_confidence, people, vehicles, motorcycles, visual_reliability, ambulance, police, fire, department, priority, ai_status, summary):
        self.cursor.execute("""
            UPDATE incidents SET severity=?, people_estimated=?, ambulance_required=?, police_required=?,
                fire_engine_required=?, department_assigned=?, priority_score=?, ai_status=?,
                ai_incident_type=?, ai_incident_confidence=?, ai_severity_confidence=?, spam_result=?,
                spam_confidence=?, visual_reliability=?, vehicle_count=?, motorcycle_count=?,
                ai_summary=?, ai_result_json=? WHERE incident_id=?
        """, (severity, people, ambulance, police, fire, department, priority, ai_status,
              incident_type, incident_confidence, severity_confidence, spam_result, spam_confidence,
              visual_reliability, vehicles, motorcycles, summary, result_json, incident_id))
        self.connection.commit()

    def get_ai_details(self, incident_id):
        self.cursor.execute("""
            SELECT ai_incident_type, ai_incident_confidence, ai_severity_confidence, spam_result,
                   spam_confidence, visual_reliability, vehicle_count, motorcycle_count, ai_summary, ai_result_json
            FROM incidents WHERE incident_id=?
        """, (incident_id,))
        return self.cursor.fetchone()

# ========================================
# INCIDENT FUNCTIONS
# ========================================

    def add_incident(
        self,
        incident_id,
        user_id,
        incident_type,
        description,
        address,
        image_path,
        video_path,
        latitude,
        longitude,
        severity,
        status,
        people_estimated,
        ambulance_required,
        police_required,
        fire_engine_required,
        department_assigned,
        priority_score,
        ai_status
    ):
        query = """
        INSERT INTO incidents(
            incident_id,
            user_id,
            incident_type,
            description,
            address,
            image_path,
            video_path,
            latitude,
            longitude,
            severity,
            status,
            people_estimated,
            ambulance_required,
            police_required,
            fire_engine_required,
            department_assigned,
            priority_score,
            ai_status
        )
        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """
        self.cursor.execute(
            query,
            (
                incident_id,
                user_id,
                incident_type,
                description,
                address,
                image_path,
                video_path,
                latitude,
                longitude,
                severity,
                status,
                people_estimated,
                ambulance_required,
                police_required,
                fire_engine_required,
                department_assigned,
                priority_score,
                ai_status
            )
        )
        self.connection.commit()

    def get_total_incidents(self):
        self.cursor.execute("SELECT COUNT(*) FROM incidents")
        return self.cursor.fetchone()[0]
    
    def get_last_incident_id(self):
        self.cursor.execute("""
            SELECT incident_id
            FROM incidents
            ORDER BY report_time DESC
            LIMIT 1
        """)
        return self.cursor.fetchone()

    def get_all_incidents(self):
        self.cursor.execute("SELECT * FROM incidents ORDER BY report_time DESC")
        return self.cursor.fetchall()

    def get_user_incidents(self, user_id):
        self.cursor.execute(
            "SELECT * FROM incidents WHERE user_id=? ORDER BY report_time DESC",
            (user_id,)
        )
        return self.cursor.fetchall()

    def get_incident(self, incident_id):
        self.cursor.execute(
            "SELECT * FROM incidents WHERE incident_id=?",
            (incident_id,)
        )
        return self.cursor.fetchone()

    def update_incident_status(self, incident_id, status):
        self.cursor.execute(
            "UPDATE incidents SET status=? WHERE incident_id=?",
            (status, incident_id)
        )
        self.connection.commit()

    def update_ai_result(
        self,
        incident_id,
        severity,
        people_estimated,
        ambulance_required,
        police_required,
        fire_engine_required,
        department_assigned,
        priority_score,
        ai_status
    ):
        self.cursor.execute(
            """
            UPDATE incidents
            SET
                severity=?,
                people_estimated=?,
                ambulance_required=?,
                police_required=?,
                fire_engine_required=?,
                department_assigned=?,
                priority_score=?,
                ai_status=?
            WHERE incident_id=?
            """,
            (
                severity,
                people_estimated,
                ambulance_required,
                police_required,
                fire_engine_required,
                department_assigned,
                priority_score,
                ai_status,
                incident_id
            )
        )
        self.connection.commit()

    def delete_incident(self, incident_id):
        self.cursor.execute(
            "DELETE FROM incidents WHERE incident_id=?",
            (incident_id,)
        )
        self.connection.commit()

# ========================================
# SEARCH INCIDENT
# ========================================

    def search_incidents(self,user_id,keyword):

        self.cursor.execute("""
            SELECT *
            FROM incidents
            WHERE user_id=?
            AND incident_id LIKE ?
            ORDER BY report_time DESC
        """,(user_id,f"%{keyword}%"))

        return self.cursor.fetchall()
    
# ========================================
# UPDATE INCIDENT
# ========================================

    def update_incident(
        self,
        incident_id,
        incident_type,
        description,
        address
    ):

        self.cursor.execute("""
            UPDATE incidents
            SET
                incident_type=?,
                description=?,
                address=?
            WHERE incident_id=?
        """,(
            incident_type,
            description,
            address,
            incident_id
        ))

        self.connection.commit()

# ========================================
# ACTIVE INCIDENTS
# ========================================

    def get_active_incidents(self, user_id):

        self.cursor.execute("""
            SELECT *
            FROM incidents
            WHERE user_id=?
            AND status!='Completed'
            ORDER BY report_time DESC
        """,(user_id,))

        return self.cursor.fetchall()
    
# ========================================
# GET DEPARTMENT INCIDENTS
# ========================================

    def get_department_incidents(self, department_name):

        # Police is the control center.
        # Police should receive every incident.

        if department_name.lower() == "police":

            self.cursor.execute("""
                SELECT *
                FROM incidents
                ORDER BY report_time DESC
            """)

        # Ambulance receives incidents where at least one ambulance is required.

        elif department_name.lower() == "ambulance":

            self.cursor.execute("""
                SELECT *
                FROM incidents
                WHERE ambulance_required > 0
                ORDER BY report_time DESC
            """)

        # Fire receives incidents where at least one fire engine is required.

        elif department_name.lower() == "fire":

            self.cursor.execute("""
                SELECT *
                FROM incidents
                WHERE fire_engine_required > 0
                ORDER BY report_time DESC
            """)

        else:

            self.cursor.execute("""
                SELECT *
                FROM incidents
                WHERE 1=0
            """)

        return self.cursor.fetchall()