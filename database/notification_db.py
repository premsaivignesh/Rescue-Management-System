from database.database import Database


class NotificationDB(Database):
    """SQLite notifications for citizen and department accounts."""

    def create_notifications_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS notifications(
                notification_id INTEGER PRIMARY KEY AUTOINCREMENT,
                incident_id TEXT,
                receiver_id INTEGER,
                title TEXT,
                message TEXT,
                notification_type TEXT,
                is_read INTEGER DEFAULT 0,
                status TEXT,
                sent_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                receiver_type TEXT DEFAULT 'Citizen'
            )
        """)
        # Migrate databases created before recipient types were separated.
        existing = {row[1] for row in self.cursor.execute(
            "PRAGMA table_info(notifications)"
        ).fetchall()}
        if "receiver_type" not in existing:
            self.cursor.execute(
                "ALTER TABLE notifications ADD COLUMN receiver_type TEXT DEFAULT 'Citizen'"
            )
        self.connection.commit()

    def add_notification(
        self, incident_id, receiver_id, title, message, notification_type,
        status="Unread", receiver_type="Citizen"
    ):
        self.cursor.execute("""
            INSERT INTO notifications(
                incident_id, receiver_id, title, message,
                notification_type, status, receiver_type
            ) VALUES(?,?,?,?,?,?,?)
        """, (
            incident_id, receiver_id, title, message,
            notification_type, status, receiver_type
        ))
        self.connection.commit()

    def get_notifications(self, receiver_id, receiver_type="Citizen"):
        self.cursor.execute("""
            SELECT * FROM notifications
            WHERE receiver_id=? AND receiver_type=?
            ORDER BY sent_time DESC, notification_id DESC
        """, (receiver_id, receiver_type))
        return self.cursor.fetchall()

    def unread_count(self, receiver_id, receiver_type="Citizen"):
        self.cursor.execute("""
            SELECT COUNT(*) FROM notifications
            WHERE receiver_id=? AND receiver_type=? AND is_read=0
        """, (receiver_id, receiver_type))
        return self.cursor.fetchone()[0]

    def mark_all_read(self, receiver_id, receiver_type="Citizen"):
        self.cursor.execute("""
            UPDATE notifications SET is_read=1
            WHERE receiver_id=? AND receiver_type=?
        """, (receiver_id, receiver_type))
        self.connection.commit()
