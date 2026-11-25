from database.notification_db import NotificationDB
from database.department_db import DepartmentDB


def notify_required_departments(incident_id, resources, severity, priority):
    """Create local SQLite notifications for departments required by the AI result."""
    db = NotificationDB()
    departments = DepartmentDB()
    rows = departments.cursor.execute(
        "SELECT department_id, department_name FROM departments"
    ).fetchall()
    # Police is the control center and receives every incident.
    required = ['Police']
    if resources.get('ambulance', 0) > 0:
        required.append('Ambulance')
    if resources.get('fire', 0) > 0:
        required.append('Fire')

    for department_id, name in rows:
        if name in required:
            message = (
                f"{severity} priority incident. Priority score {priority}/100. "
                f"Required resources: ambulance={resources.get('ambulance',0)}, "
                f"police={resources.get('police',0)}, fire={resources.get('fire',0)}."
            )
            db.add_notification(
                incident_id, department_id, 'New AI-Assessed Incident',
                message, 'AI_DISPATCH', receiver_type='Department'
            )


def notify_incident_owner_status(incident_id, status, department_name):
    """Notify the citizen who reported an incident when its status changes."""
    from database.incident_db import IncidentDB

    incidents = IncidentDB()
    incident = incidents.get_incident(incident_id)
    if not incident or incident[1] is None:
        return

    user_id = incident[1]
    notifications = NotificationDB()
    title = f"Incident {status}"
    message = (
        f"Your incident {incident_id} was marked {status} by "
        f"{department_name}."
    )
    notifications.add_notification(
        incident_id, user_id, title, message, 'INCIDENT_STATUS',
        receiver_type='Citizen'
    )
