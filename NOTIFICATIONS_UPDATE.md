# Notification integration update

This update connects the existing SQLite notifications to both CustomTkinter dashboards.

- Notifications now distinguish `Citizen` and `Department` recipients, preventing overlapping numeric IDs from exposing the wrong notifications.
- Citizen dashboard: the Notifications card shows the unread count; the Notifications page lists messages and supports refresh and mark-all-read.
- Department dashboard: adds a Notifications page, unread count, refresh, and mark-all-read.
- AI dispatch notifications always go to Police as the control center and go to Ambulance/Fire when the resource model requires them.
- When a department accepts or completes an incident, the reporting citizen receives a status notification.

Notifications are stored locally in SQLite. They are not remote push notifications; users see new entries when they refresh or reopen the page.
