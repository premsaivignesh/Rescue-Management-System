import customtkinter as ctk
from utils.session import Session
from database.incident_db import IncidentDB
from database.notification_db import NotificationDB
from gui.analytics_view import build_analytics, PALETTE

from utils.loading_overlay import run_loading
class Dashboard:

    def __init__(self, app):
        self.app = app
        self.incident_db = IncidentDB()
        self.notification_db = NotificationDB()

        for widget in self.app.winfo_children():
            widget.destroy()

        self.create_sidebar()
        self.create_content_frame()
        self.show_dashboard()

# ========================================
# SIDEBAR
# ========================================

    def create_sidebar(self):

        self.sidebar = ctk.CTkFrame(
            self.app, width=235, corner_radius=0, fg_color=PALETTE["panel"]
        )
        self.sidebar.pack(side="left", fill="y")

        title = ctk.CTkLabel(
            self.sidebar,
            text="🚑 Rescue System",
            font=("Segoe UI", 22, "bold"), text_color=PALETTE["light"]
        )
        title.pack(pady=25)

        menu = {
            "🏠 Dashboard": self.show_dashboard,
            "🚨 Report Incident": self.show_report,
            "📄 My Reports": self.show_reports,
            "📊 Analytics": self.show_analytics,
            "👤 Profile": self.show_profile,
            "🚪 Logout": self.logout
        }

        for text, command in menu.items():

            button = ctk.CTkButton(
                self.sidebar,
                text=text,
                width=195, height=43, corner_radius=10,
                fg_color=PALETTE["olive"], hover_color=PALETTE["green"],
                text_color=PALETTE["light"], font=("Segoe UI", 13), command=command
            )

            button.pack(pady=8)

# ========================================
# CONTENT FRAME
# ========================================

    def create_content_frame(self):

        self.content = ctk.CTkFrame(self.app, fg_color=PALETTE["bg"], corner_radius=0)
        self.content.pack(side="right", fill="both", expand=True)

# ========================================
# CLEAR CONTENT
# ========================================

    def clear_content(self):

        for widget in self.content.winfo_children():
            widget.destroy()

# ========================================
# DASHBOARD
# ========================================

    def show_dashboard(self):
        self.clear_content()
        self.content.configure(fg_color=PALETTE["bg"])
        hero = ctk.CTkFrame(self.content, fg_color=PALETTE["panel"], corner_radius=18, border_width=1, border_color=PALETTE["border"])
        hero.pack(fill="x", padx=28, pady=(28, 18))
        ctk.CTkLabel(hero, text=f"Good to see you, {Session.full_name}", font=("Segoe UI", 29, "bold"), text_color=PALETTE["light"]).pack(anchor="w", padx=25, pady=(22, 4))
        ctk.CTkLabel(hero, text="Your community response overview", font=("Segoe UI", 14), text_color=PALETTE["muted"]).pack(anchor="w", padx=26, pady=(0, 22))

        total_incidents = self.incident_db.get_total_incidents()
        try:
            own_reports = self.incident_db.get_user_incidents(Session.user_id) or []
            active_count = sum(1 for report in own_reports if str(report[10] or "").lower() not in ("completed", "closed"))
        except Exception:
            active_count = 0
        unread = self.notification_db.unread_count(Session.user_id, "Citizen")
        cards = ctk.CTkFrame(self.content, fg_color="transparent")
        cards.pack(fill="x", padx=22, pady=(0, 14))
        self.create_card(cards, "TOTAL INCIDENTS", str(total_incidents), self.show_reports)
        self.create_card(cards, "YOUR ACTIVE CASES", str(active_count), self.show_active_cases)
        self.create_card(cards, "UNREAD NOTIFICATIONS", str(unread), self.show_notifications)

        lower = ctk.CTkFrame(self.content, fg_color="transparent")
        lower.pack(fill="both", expand=True, padx=28, pady=(4, 24))
        recent = ctk.CTkFrame(lower, fg_color=PALETTE["panel"], corner_radius=16, border_width=1, border_color=PALETTE["border"])
        recent.pack(side="left", fill="both", expand=True, padx=(0, 8))
        ctk.CTkLabel(recent, text="Your recent reports", font=("Segoe UI", 18, "bold"), text_color=PALETTE["light"]).pack(anchor="w", padx=18, pady=(16, 8))
        try:
            reports = self.incident_db.get_user_incidents(Session.user_id) or []
        except Exception:
            reports = []
        if not reports:
            ctk.CTkLabel(recent, text="No reports yet. Use Report Incident to get started.", text_color=PALETTE["muted"]).pack(anchor="w", padx=18, pady=18)
        else:
            for report in reports[:4]:
                row = ctk.CTkFrame(recent, fg_color=PALETTE["panel2"], corner_radius=10, border_width=1, border_color=PALETTE["border"])
                row.pack(fill="x", padx=14, pady=6)
                info = ctk.CTkFrame(row, fg_color="transparent")
                info.pack(side="left", fill="x", expand=True, padx=12, pady=8)
                ctk.CTkLabel(info, text=f"{report[0]}  •  {report[2]}", font=("Segoe UI", 12, "bold"), text_color=PALETTE["light"]).pack(anchor="w")
                ctk.CTkLabel(info, text=f"Status: {report[10]}", text_color=PALETTE["muted"]).pack(anchor="w", pady=(3, 0))
                ctk.CTkButton(row, text="Open →", width=95, height=32, corner_radius=8,
                              fg_color=PALETTE["olive"], hover_color=PALETTE["green"],
                              command=lambda incident_id=report[0]: self.open_recent_report(incident_id)).pack(side="right", padx=12, pady=8)
        shortcuts = ctk.CTkFrame(lower, fg_color=PALETTE["panel"], corner_radius=16, border_width=1, border_color=PALETTE["border"], width=260)
        shortcuts.pack(side="right", fill="y", padx=(8, 0))
        ctk.CTkLabel(shortcuts, text="Quick actions", font=("Segoe UI", 18, "bold"), text_color=PALETTE["light"]).pack(anchor="w", padx=18, pady=(16, 10))
        for label, action in [("＋  Report an incident", self.show_report), ("▤  Track my reports", self.show_reports), ("◉  View notifications", self.show_notifications), ("▥  View analytics", self.show_analytics)]:
            ctk.CTkButton(shortcuts, text=label, command=action, height=40, corner_radius=9, fg_color=PALETTE["olive"], hover_color=PALETTE["green"], text_color=PALETTE["light"]).pack(fill="x", padx=14, pady=6)

    def create_card(self, parent, title, value, command=None):

        frame = ctk.CTkFrame(parent, width=190, height=112, corner_radius=14, fg_color=PALETTE["panel"], border_width=1, border_color=PALETTE["border"])
        frame.pack(side="left", padx=10)

        title_label = ctk.CTkLabel(frame, text=title, font=("Segoe UI",11,"bold"), text_color=PALETTE["muted"])
        title_label.pack(pady=(18,5))
        
        value_label = ctk.CTkLabel(frame, text=value, font=("Segoe UI",27,"bold"), text_color=PALETTE["light"])
        value_label.pack()

        if command:

            frame.bind("<Button-1>", lambda e: command())

            title_label.bind("<Button-1>", lambda e: command())

            value_label.bind("<Button-1>", lambda e: command())

# ========================================
# MENU FUNCTIONS
# ========================================

    def show_report(self):

        self.clear_content()
        from gui.report_incident import ReportIncident
        ReportIncident(self.content,self)

    def show_reports(self):

        self.clear_content()
        from gui.my_reports import MyReports
        self.reports_view = MyReports(self.content)

    def open_recent_report(self, incident_id):
        self.show_reports()
        # MyReports uses its normal search flow, so this opens the selected case
        # without creating a second, inconsistent incident-detail implementation.
        try:
            self.reports_view.search.insert(0, incident_id)
            self.reports_view.search_reports()
        except Exception:
            pass

    def show_profile(self):
        import json, os
        from pathlib import Path
        from tkinter import filedialog, messagebox
        from PIL import Image
        from database.user_db import UserDB
        self.clear_content()
        root = Path(__file__).resolve().parents[1]
        profile_dir = root / "user_profiles"
        profile_dir.mkdir(exist_ok=True)
        profile_file = profile_dir / f"citizen_{Session.user_id}.json"
        try:
            saved = json.loads(profile_file.read_text(encoding="utf-8")) if profile_file.exists() else {}
        except Exception:
            saved = {}
        self.profile_photo_path = saved.get("photo", "")
        ctk.CTkLabel(self.content, text="Your Profile", font=("Segoe UI", 29, "bold"), text_color=PALETTE["light"]).pack(anchor="w", padx=28, pady=(24, 4))
        ctk.CTkLabel(self.content, text="Manage your contact details and personal identity", font=("Segoe UI", 13), text_color=PALETTE["muted"]).pack(anchor="w", padx=30, pady=(0, 16))
        layout = ctk.CTkFrame(self.content, fg_color=PALETTE["panel"], corner_radius=18, border_width=1, border_color=PALETTE["border"])
        layout.pack(fill="both", expand=True, padx=28, pady=(0, 25))
        photo_col = ctk.CTkFrame(layout, fg_color=PALETTE["panel2"], corner_radius=14, width=240)
        photo_col.pack(side="left", fill="y", padx=18, pady=18)
        photo_label = ctk.CTkLabel(photo_col, text="👤\nProfile photo", width=180, height=180, fg_color=PALETTE["panel"], corner_radius=90, text_color=PALETTE["muted"])
        photo_label.pack(padx=20, pady=(22, 12))
        def choose_photo():
            path = filedialog.askopenfilename(filetypes=[("Images", "*.png *.jpg *.jpeg *.webp")])
            if not path: return
            self.profile_photo_path = path
            try:
                image = Image.open(path); image.thumbnail((180, 180))
                photo = ctk.CTkImage(light_image=image, dark_image=image, size=(180, 180))
                photo_label.configure(image=photo, text=""); photo_label.image = photo
            except Exception as exc: messagebox.showerror("Profile photo", str(exc))
        if self.profile_photo_path and os.path.exists(self.profile_photo_path):
            try:
                image = Image.open(self.profile_photo_path); image.thumbnail((180,180))
                photo = ctk.CTkImage(light_image=image, dark_image=image, size=(180,180))
                photo_label.configure(image=photo, text=""); photo_label.image = photo
            except Exception: pass
        ctk.CTkButton(photo_col, text="Upload / Change Photo", command=choose_photo, fg_color=PALETTE["olive"], hover_color=PALETTE["green"]).pack(fill="x", padx=18, pady=8)
        ctk.CTkLabel(photo_col, text=f"Account role · {Session.role or 'Citizen'}", text_color=PALETTE["muted"]).pack(pady=(8,18))
        form = ctk.CTkFrame(layout, fg_color="transparent")
        form.pack(side="left", fill="both", expand=True, padx=(6,22), pady=22)
        fields = {}
        for label, key, value in [("Full name", "name", Session.full_name or ""), ("Email address", "email", Session.email or ""), ("Phone number", "phone", Session.phone or "")]:
            ctk.CTkLabel(form, text=label, font=("Segoe UI", 13, "bold"), text_color=PALETTE["light"]).pack(anchor="w", pady=(8,4))
            entry = ctk.CTkEntry(form, height=40, placeholder_text=label)
            entry.pack(fill="x", pady=(0,6)); entry.insert(0, value)
            fields[key] = entry
        ctk.CTkLabel(form, text=f"User ID: {Session.user_id}   •   Account type: {Session.role or 'Citizen'}", text_color=PALETTE["muted"]).pack(anchor="w", pady=(14,10))
        def save_profile():
            name, email, phone = fields['name'].get().strip(), fields['email'].get().strip(), fields['phone'].get().strip()
            if not name or not email or not phone:
                messagebox.showwarning("Missing information", "Please fill in your name, email and phone number."); return
            try:
                UserDB().update_user_profile(Session.user_id, name, email, phone)
                Session.full_name, Session.email, Session.phone = name, email, phone
                profile_file.write_text(json.dumps({"photo": self.profile_photo_path}, indent=2), encoding="utf-8")
                messagebox.showinfo("Profile saved", "Your profile information was updated.")
            except Exception as exc:
                messagebox.showerror("Could not save profile", f"Check that the email and phone are not already used.\n{exc}")
        ctk.CTkButton(form, text="Save Profile Changes", height=42, command=save_profile, fg_color=PALETTE["olive"], hover_color=PALETTE["green"]).pack(anchor="w", pady=(16,6))
        ctk.CTkLabel(form, text="Your photo path is stored locally on this computer; the photo is not uploaded to a server.", text_color=PALETTE["muted"], wraplength=650, justify="left").pack(anchor="w", pady=8)

# ========================================
# ACTIVE CASES
# ========================================

    def show_active_cases(self):

        self.clear_content()
        from gui.my_reports import MyReports
        MyReports(
            self.content,
            active_only=True
        )

# ========================================
# NOTIFICATIONS
# ========================================

    def show_notifications(self):
        self.clear_content()
        ctk.CTkLabel(
            self.content, text="Notifications", font=("Arial", 28, "bold")
        ).pack(pady=(25, 10))

        actions = ctk.CTkFrame(self.content, fg_color="transparent")
        actions.pack(fill="x", padx=20, pady=(0, 10))
        ctk.CTkButton(
            actions, text="Mark all as read", width=150,
            command=self.mark_notifications_read
        ).pack(side="right", padx=5)
        ctk.CTkButton(
            actions, text="Refresh", width=100,
            command=lambda: run_loading(self.app, self.show_notifications)
        ).pack(side="right", padx=5)

        listing = ctk.CTkScrollableFrame(self.content)
        listing.pack(fill="both", expand=True, padx=20, pady=10)
        notifications = self.notification_db.get_notifications(
            Session.user_id, "Citizen"
        )
        if not notifications:
            ctk.CTkLabel(
                listing, text="You have no notifications yet.",
                font=("Arial", 18)
            ).pack(pady=40)
            return

        for item in notifications:
            # Columns: id, incident_id, receiver_id, title, message,
            # type, is_read, status, sent_time, receiver_type.
            card = ctk.CTkFrame(listing)
            card.pack(fill="x", padx=8, pady=7)
            state = "Read" if item[6] else "NEW"
            ctk.CTkLabel(
                card, text=f"{state} · {item[3] or 'Notification'}",
                font=("Arial", 16, "bold")
            ).pack(anchor="w", padx=15, pady=(10, 3))
            ctk.CTkLabel(
                card, text=f"Incident: {item[1] or 'N/A'}  |  {item[8] or ''}",
                font=("Arial", 12)
            ).pack(anchor="w", padx=15)
            ctk.CTkLabel(
                card, text=item[4] or "", wraplength=750, justify="left"
            ).pack(anchor="w", padx=15, pady=(5, 12))

    def mark_notifications_read(self):
        self.notification_db.mark_all_read(Session.user_id, "Citizen")
        self.show_notifications()

# ========================================
# ANALYTICS
# ========================================

    def show_analytics(self):
        build_analytics(self.content, self.incident_db, user_id=Session.user_id, title="Your Incident Analytics")

# ========================================
# REFRESH DASHBOARD
# ========================================

    def refresh_dashboard(self):
        self.show_dashboard()

# ========================================
# LOGOUT
# ========================================

    def logout(self):

        for widget in self.app.winfo_children():
            widget.destroy()

        from gui.login import LoginPage
        LoginPage(self.app)
