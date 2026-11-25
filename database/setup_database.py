from database.user_db import UserDB
from database.incident_db import IncidentDB
from database.resource_db import ResourceDB
from database.notification_db import NotificationDB
from database.department_db import DepartmentDB


def initialize_database():
    UserDB().create_users_table()
    incidents = IncidentDB()
    incidents.create_incidents_table()
    incidents.ensure_ai_columns()
    ResourceDB().create_resources_table()
    NotificationDB().create_notifications_table()
    department = DepartmentDB()
    department.create_departments_table()
    department.insert_default_departments()
