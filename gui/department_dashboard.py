import customtkinter as ctk
from database.incident_db import IncidentDB
from database.notification_db import NotificationDB
from utils.session import Session
from tkinter import messagebox
from PIL import Image
import os
from dsa.priority_queue import PriorityQueue
from gui.analytics_view import build_analytics, PALETTE

from utils.loading_overlay import run_loading
class DepartmentDashboard:

# ========================================
# INITIALIZE
# ========================================

    def __init__(self, app, department):

        self.app = app
        self.department = department
        self.db = IncidentDB()
        self.notification_db = NotificationDB()
        self.priority_queue = PriorityQueue()
        self.current_page = "Dashboard"
        self.selected_incident = None
        self.app.configure(fg_color=PALETTE["bg"])

        for widget in self.app.winfo_children():
            widget.destroy()

        self.create_sidebar()
        self.create_content()
        self.show_dashboard()

# ========================================
# SIDEBAR
# ========================================

    def create_sidebar(self):

        self.sidebar = ctk.CTkFrame(self.app, width=235, corner_radius=0, fg_color=PALETTE["panel"])
        self.sidebar.pack(side="left", fill="y")

        icons = {
            "Police":"🚓",
            "Ambulance":"🚑",
            "Fire":"🚒",
            "Traffic Police":"🚦"
        }

        icon = icons.get(Session.department_name, "🏢")

        ctk.CTkLabel(
            self.sidebar,
            text=f"{icon}  {Session.department_name}",
            font=("Segoe UI", 22, "bold"),
            text_color=PALETTE["light"]
        ).pack(fill="x", padx=14, pady=(28, 30))

        ctk.CTkFrame(self.sidebar, height=2, fg_color=PALETTE["border"], corner_radius=2).pack(fill="x", padx=18, pady=(0, 14))

        menu = {
            "🏠 Dashboard":self.show_dashboard,
            "📋 Incidents":self.show_incidents,
            "🔔 Notifications":self.show_notifications,
            "📊 Analytics":self.show_analytics,
            "👤 Profile":self.show_profile,
            "🚪 Logout":self.logout
        }

        for text,command in menu.items():

            ctk.CTkButton(
                self.sidebar,
                text=text,
                width=198, height=45, corner_radius=10,
                fg_color=PALETTE["olive"], hover_color=PALETTE["green"],
                text_color=PALETTE["light"], font=("Segoe UI", 13, "bold"), command=command,
                border_width=1, border_color=PALETTE["border"], anchor="w"
            ).pack(padx=14, pady=6)

# ========================================
# CONTENT FRAME
# ========================================

    def create_content(self):

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

        self.current_page = "Dashboard"
        
        self.clear_content()

        top_frame = ctk.CTkFrame(
            self.content,
            fg_color="transparent"
        )

        top_frame = ctk.CTkFrame(self.content, fg_color=PALETTE["panel"], corner_radius=12, border_width=1, border_color=PALETTE["border"])
        top_frame.pack(fill="x", padx=24, pady=(18, 0))

        ctk.CTkButton(
            top_frame,
            text="↻  Refresh dashboard",
            width=160, height=36, corner_radius=9,
            fg_color=PALETTE["olive"], hover_color=PALETTE["green"], text_color=PALETTE["light"],
            command=lambda: run_loading(self.app, self.refresh_dashboard)
        ).pack(side="right", padx=12, pady=10)

        ctk.CTkLabel(
            self.content,
            text=f"🚓 {Session.department_name} Dashboard  ·  Unread notifications: {self.notification_db.unread_count(Session.department_id, 'Department')}",
            font=("Segoe UI", 27, "bold"), text_color=PALETTE["light"]
        ).pack(pady=(20, 10))

        self.update_statistics()

        card_frame = ctk.CTkFrame(self.content, fg_color=PALETTE["panel"], corner_radius=16, border_width=1, border_color=PALETTE["border"])
        card_frame.pack(pady=12, padx=24)

        self.create_stat_card(
            card_frame,
            "Total",
            self.total_count,
            self.show_incidents
        )

        self.create_stat_card(
            card_frame,
            "Waiting",
            self.waiting_count,
            self.show_waiting
        )

        self.create_stat_card(
            card_frame,
            "Accepted",
            self.accepted_count,
            self.show_accepted
        )

        self.create_stat_card(
            card_frame,
            "Completed",
            self.completed_count,
            self.show_completed
        )

        search_row = ctk.CTkFrame(self.content, fg_color=PALETTE["panel"], corner_radius=12, border_width=1, border_color=PALETTE["border"])
        search_row.pack(fill="x", padx=24, pady=(8, 2))
        ctk.CTkLabel(search_row, text="Find an incident", text_color=PALETTE["light"], font=("Segoe UI", 13, "bold")).pack(side="left", padx=(14, 8), pady=10)
        self.home_search = ctk.CTkEntry(search_row, placeholder_text="Enter incident ID", width=280, height=36)
        self.home_search.pack(side="left", padx=6, pady=8)
        self.home_search.bind("<Return>", lambda _event: self.search_home_incident())
        ctk.CTkButton(search_row, text="Search incident →", width=140, height=36, fg_color=PALETTE["olive"], hover_color=PALETTE["green"], command=self.search_home_incident).pack(side="left", padx=6, pady=8)

        ctk.CTkLabel(
            self.content,
            text="Recent Incidents",
            font=("Segoe UI", 21, "bold"), text_color=PALETTE["light"]
        ).pack(anchor="w", padx=30, pady=(18, 6))

        recent = self.db.get_department_incidents(
            Session.department_name
        )

        frame = ctk.CTkScrollableFrame(self.content, height=320, fg_color=PALETTE["panel"], corner_radius=14, border_width=1, border_color=PALETTE["border"])

        frame.pack(
            fill="both", expand=True, padx=24, pady=(4, 18)
        )
        count = 0

        for report in recent:

            self.create_dashboard_card(
                frame,
                report
            )
            count += 1

            if count == 5:
                break

        if count == 0:
            ctk.CTkLabel(
                frame,
                text="No Incidents"
            ).pack(pady=50)

# ========================================
# STATISTICS
# ========================================

    def update_statistics(self):

        reports = self.db.get_department_incidents(
            Session.department_name
        )
        self.total_count = len(reports)

        self.waiting_count = 0
        self.accepted_count = 0
        self.completed_count = 0

        for report in reports:

            if report[10] == "Waiting":
                self.waiting_count += 1

            elif report[10] == "Accepted":
                self.accepted_count += 1

            elif report[10] == "Completed":
                self.completed_count += 1

# ========================================
# STAT CARD
# ========================================

    def create_stat_card(self,parent,title,count,command):

        card = ctk.CTkButton(
            parent, width=170, height=108, text="", command=command,
            fg_color=PALETTE["olive"], hover_color=PALETTE["green"],
            border_width=1, border_color=PALETTE["border"], corner_radius=13
        )

        card.pack(side="left", padx=10)

        ctk.CTkLabel(
            card,
            text=title,
            font=("Segoe UI", 14, "bold"), text_color=PALETTE["light"]
        ).place(relx=0.5, rely=0.33, anchor="center")

        ctk.CTkLabel(
            card,
            text=str(count),
            font=("Segoe UI", 29, "bold"), text_color=PALETTE["light"]
        ).place(relx=0.5, rely=0.70, anchor="center")

# ========================================
# DASHBOARD CARD
# ========================================

    def create_dashboard_card(self,parent,report):

        card = ctk.CTkFrame(parent, fg_color=PALETTE["panel2"], corner_radius=12, border_width=1, border_color=PALETTE["border"])

        card.pack(fill="x", padx=10, pady=7)

        ctk.CTkLabel(
            card,
            text=f"{report[0]}",
            font=("Segoe UI", 16, "bold"), text_color=PALETTE["light"]
        ).pack(anchor="w", padx=15, pady=(12, 2))

        ctk.CTkLabel(
            card,
            text=f"{report[2]}"
        ).pack(anchor="w", padx=15, pady=2)

        ctk.CTkLabel(
            card, text=f"Status  ·  {report[10]}",
            text_color=PALETTE["muted"], font=("Segoe UI", 12)
        ).pack(anchor="w", padx=15, pady=(0, 2))

        ctk.CTkButton(
            card,
            text="Open incident  →", width=130, height=34, corner_radius=8,
            fg_color=PALETTE["olive"], hover_color=PALETTE["green"], text_color=PALETTE["light"],
            command=lambda r=report:self.open_incident(r)
        ).pack(anchor="e", padx=15, pady=(4, 12))

# ========================================
# OPEN INCIDENT
# ========================================

    def search_home_incident(self):
        from tkinter import messagebox
        keyword = self.home_search.get().strip()
        if not keyword:
            messagebox.showinfo("Search incident", "Enter an incident ID to search.")
            return
        self.db.cursor.execute("SELECT * FROM incidents WHERE incident_id LIKE ? ORDER BY report_time DESC", (f"%{keyword}%",))
        rows = self.db.cursor.fetchall()
        if not rows:
            messagebox.showinfo("No match", "No incident matches that ID.")
            return
        self.selected_incident = rows[0][0]
        status = str(rows[0][10] or "Waiting")
        if status == "Accepted": self.show_accepted()
        elif status == "Completed": self.show_completed()
        else: self.show_waiting()

    def open_incident(self, report):

        self.selected_incident = report[0]

        if report[10] == "Waiting":
            self.show_waiting()

        elif report[10] == "Accepted":
            self.show_accepted()

        elif report[10] == "Completed":
            self.show_completed()

# ========================================
# INCIDENT PAGE
# ========================================

    def show_incidents(self):
        self.show_waiting()

# ========================================
# NOTIFICATIONS
# ========================================

    def show_notifications(self):
        self.current_page = "Notifications"
        self.clear_content()
        ctk.CTkLabel(
            self.content, text="Department Notifications",
            font=("Segoe UI", 28, "bold"), text_color=PALETTE["light"]
        ).pack(anchor="w", padx=28, pady=(25, 10))

        actions = ctk.CTkFrame(self.content, fg_color=PALETTE["panel"], corner_radius=12, border_width=1, border_color=PALETTE["border"])
        actions.pack(fill="x", padx=24, pady=(0, 10))
        ctk.CTkButton(
            actions, text="✓  Mark all as read", width=160, height=36, corner_radius=9,
            fg_color=PALETTE["olive"], hover_color=PALETTE["green"], text_color=PALETTE["light"],
            command=self.mark_notifications_read
        ).pack(side="right", padx=10, pady=8)
        ctk.CTkButton(
            actions, text="↻  Refresh", width=115, height=36, corner_radius=9,
            fg_color=PALETTE["olive"], hover_color=PALETTE["green"], text_color=PALETTE["light"],
            command=lambda: run_loading(self.app, self.show_notifications)
        ).pack(side="right", padx=5, pady=8)

        listing = ctk.CTkScrollableFrame(self.content, fg_color=PALETTE["panel"], corner_radius=14, border_width=1, border_color=PALETTE["border"])
        listing.pack(fill="both", expand=True, padx=24, pady=(0, 18))
        notifications = self.notification_db.get_notifications(
            Session.department_id, "Department"
        )
        if not notifications:
            ctk.CTkLabel(
                listing, text="No department notifications yet.",
                font=("Arial", 18)
            ).pack(pady=40)
            return

        for item in notifications:
            card = ctk.CTkFrame(listing, fg_color=PALETTE["panel2"], corner_radius=12, border_width=1, border_color=PALETTE["border"])
            card.pack(fill="x", padx=10, pady=7)
            state = "Read" if item[6] else "NEW"
            ctk.CTkLabel(
                card, text=f"{state} · {item[3] or 'Notification'}",
                font=("Segoe UI", 16, "bold"), text_color=PALETTE["light"]
            ).pack(anchor="w", padx=15, pady=(12, 4))
            ctk.CTkLabel(
                card, text=f"Incident: {item[1] or 'N/A'}  |  {item[8] or ''}",
                font=("Segoe UI", 12), text_color=PALETTE["muted"]
            ).pack(anchor="w", padx=15)
            ctk.CTkLabel(
                card, text=item[4] or "", wraplength=850, justify="left",
                text_color=PALETTE["light"], font=("Segoe UI", 13)
            ).pack(anchor="w", padx=15, pady=(7, 14))

    def mark_notifications_read(self):
        self.notification_db.mark_all_read(Session.department_id, "Department")
        self.show_notifications()

# ========================================
# PROFILE
# ========================================

    def show_analytics(self):
        build_analytics(self.content, self.db, title=f"{Session.department_name} Analytics")

    def show_profile(self):

        self.current_page = "Profile"
        self.clear_content()

        ctk.CTkLabel(
            self.content,
            text="Department Profile",
            font=("Segoe UI", 28, "bold"), text_color=PALETTE["light"]
        ).pack(anchor="w", padx=30, pady=(28, 22))

        ctk.CTkLabel(
            self.content,
            text=f"Department : {Session.department_name}",
            font=("Segoe UI", 17), text_color=PALETTE["light"]
        ).pack(anchor="w", padx=38, pady=10)

        ctk.CTkLabel(
            self.content,
            text=f"Username : {Session.department_username}",
            font=("Segoe UI", 17), text_color=PALETTE["light"]
        ).pack(anchor="w", padx=38, pady=10)

        ctk.CTkLabel(
            self.content,
            text="Department Type : Emergency Response Unit",
            font=("Segoe UI", 17), text_color=PALETTE["light"]
        ).pack(anchor="w", padx=38, pady=10)

# ========================================
# LOGOUT
# ========================================

    def logout(self):

        for widget in self.app.winfo_children():
            widget.destroy()

        from gui.department_login import DepartmentLogin
        DepartmentLogin(self.app)

# ========================================
# WAITING
# ========================================

    def show_waiting(self):

        self.current_page = "Waiting"
        self.load_incidents("Waiting")

# ========================================
# ACCEPTED
# ========================================

    def show_accepted(self):

        self.current_page = "Accepted"
        self.load_incidents("Accepted")

# ========================================
# COMPLETED
# ========================================

    def show_completed(self):

        self.current_page = "Completed"
        self.load_incidents("Completed")

# ========================================
# LOAD INCIDENTS
# ========================================

    def load_incidents(self, status):

        self.clear_content()

        ctk.CTkLabel(
            self.content,
            text=f"{status} Incidents",
            font=("Segoe UI", 28, "bold"), text_color=PALETTE["light"]
        ).pack(anchor="w", padx=28, pady=(24, 12))

        top_frame = ctk.CTkFrame(self.content, fg_color=PALETTE["panel"], corner_radius=12, border_width=1, border_color=PALETTE["border"])
        top_frame.pack(fill="x", padx=24, pady=5)

        ctk.CTkButton(
            top_frame,
            text="Waiting",
            command=self.show_waiting,
            width=120
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            top_frame,
            text="Accepted",
            command=self.show_accepted,
            width=120
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            top_frame,
            text="Completed",
            command=self.show_completed,
            width=120
        ).pack(side="left", padx=5)

        self.report_frame = ctk.CTkScrollableFrame(
            self.content,
            width=900, height=520, fg_color=PALETTE["panel"], corner_radius=14,
            border_width=1, border_color=PALETTE["border"]
        )

        self.report_frame.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=10
        )

        reports = self.db.get_department_incidents(
            Session.department_name
        )

        self.priority_queue = PriorityQueue()

        for report in reports:

            if report[10] == status:

                self.priority_queue.insert(report)

        found = False

        while self.priority_queue.size() > 0:

            found = True

            report = self.priority_queue.extract_max()

            self.create_card(report)

        if not found:

            ctk.CTkLabel(
                self.report_frame,
                text=f"No {status} Incidents",
                font=("Arial",22)
            ).pack(pady=50)

# ========================================
# INCIDENT CARD
# ========================================

    def create_card(self, report):

        card = ctk.CTkFrame(self.report_frame, fg_color=PALETTE["panel2"], corner_radius=13, border_width=1, border_color=PALETTE["border"])

        card.pack(
            fill="x",
            padx=10,
            pady=8
        )

        ctk.CTkLabel(
            card,
            text=f"Incident ID : {report[0]}",
            font=("Segoe UI", 17, "bold"), text_color=PALETTE["light"]
        ).pack(anchor="w", padx=15, pady=(12, 3))

        ctk.CTkLabel(
            card,
            text=f"Incident Type : {report[2]}"
        ).pack(anchor="w", padx=15)

        ctk.CTkLabel(
            card,
            text=f"Status : {report[10]}"
        ).pack(anchor="w", padx=15)

        ctk.CTkLabel(
            card,
            text=f"Reported : {report[17]}"
        ).pack(anchor="w", padx=15)

        button_frame = ctk.CTkFrame(
            card,
            fg_color="transparent"
        )

        button_frame.pack(pady=10)

        details = ctk.CTkFrame(card, fg_color=PALETTE["panel"], corner_radius=10, border_width=1, border_color=PALETTE["border"])

        details.pack(
            fill="x",
            padx=15,
            pady=(0,10)
        )

        details.pack_forget()

        card.details_frame = details
        card.details_visible = False

        view_btn = ctk.CTkButton(
            button_frame,
            text="▼ View Details",
            width=120
        )

        view_btn.pack(side="left", padx=5)

        view_btn.configure(
            command=lambda c=card,r=report,b=view_btn:
            self.toggle_details(c,r,b)
        )

        card.view_button = view_btn

        if report[10] == "Waiting":

            ctk.CTkButton(
                button_frame,
                text="Accept",
                width=100,
                command=lambda r=report:
                self.accept_incident(r)
            ).pack(side="left", padx=5)

        elif report[10] == "Accepted":

            ctk.CTkButton(
                button_frame,
                text="Complete",
                width=100,
                command=lambda r=report:
                self.complete_incident(r)
            ).pack(side="left", padx=5)

        ctk.CTkButton(
            button_frame, text="Delete", width=86, fg_color="#754438", hover_color="#9B5140",
            command=lambda r=report: self.delete_incident_confirm(r)
        ).pack(side="left", padx=5)

        return card

    def delete_incident_confirm(self, report):
        from tkinter import messagebox
        incident_id = report[0]
        if not messagebox.askyesno("Confirm deletion", f"Delete incident {incident_id}?\n\nThis permanently removes the incident record. This action cannot be undone."):
            return
        try:
            self.db.delete_incident(incident_id)
            messagebox.showinfo("Incident deleted", f"Incident {incident_id} was deleted.")
            if self.current_page == "Dashboard": self.show_dashboard()
            elif report[10] == "Accepted": self.show_accepted()
            elif report[10] == "Completed": self.show_completed()
            else: self.show_waiting()
        except Exception as exc:
            messagebox.showerror("Delete failed", str(exc))

# ========================================
# TOGGLE DETAILS
# ========================================

    def toggle_details(self, card, report, button):

        if card.details_visible:
            card.details_frame.pack_forget()
            button.configure(text="▼ View Details")
            
            card.details_visible = False
            return

        for widget in card.details_frame.winfo_children():
            widget.destroy()

        button.configure(
            text="▲ Hide Details"
        )

        self.create_details(card.details_frame, report)

        card.details_frame.pack(
            fill="x",
            padx=15,
            pady=(0,10)
        )
        card.details_visible = True

# ========================================
# CREATE DETAILS
# ========================================

    def create_details(self, parent, report):

        ctk.CTkLabel(
            parent,
            text="📝 Description",
            font=("Arial",16,"bold")
        ).pack(anchor="w", padx=15, pady=(12,0))

        ctk.CTkLabel(
            parent,
            text=report[3],
            wraplength=750,
            justify="left"
        ).pack(anchor="w", padx=15)

        ctk.CTkLabel(
            parent,
            text="📍 Address",
            font=("Arial",16,"bold")
        ).pack(anchor="w", padx=15, pady=(12,0))

        ctk.CTkLabel(
            parent,
            text=report[4]
        ).pack(anchor="w", padx=15)

        ctk.CTkLabel(
            parent,
            text="⚠ Severity",
            font=("Arial",16,"bold")
        ).pack(anchor="w", padx=15, pady=(12,0))

        ctk.CTkLabel(
            parent,
            text=report[9]
        ).pack(anchor="w", padx=15)

        ctk.CTkLabel(
            parent,
            text="🤖 AI Status",
            font=("Arial",16,"bold")
        ).pack(anchor="w", padx=15, pady=(12,0))

        ctk.CTkLabel(
            parent,
            text=report[17]
        ).pack(anchor="w", padx=15)

        ctk.CTkLabel(
            parent,
            text="🏢 Department",
            font=("Arial",16,"bold")
        ).pack(anchor="w", padx=15, pady=(12,0))

        ctk.CTkLabel(
            parent,
            text=report[15]
        ).pack(anchor="w", padx=15)

        ctk.CTkLabel(
            parent,
            text="👥 Estimated People",
            font=("Arial",16,"bold")
        ).pack(anchor="w", padx=15, pady=(12,0))

        ctk.CTkLabel(
            parent,
            text=str(report[11])
        ).pack(anchor="w", padx=15)

        ctk.CTkLabel(
            parent,
            text="🚑 Ambulances Required",
            font=("Arial",16,"bold")
        ).pack(anchor="w", padx=15, pady=(12,0))

        ctk.CTkLabel(
            parent,
            text=str(report[12])
        ).pack(anchor="w", padx=15)

        ctk.CTkLabel(
            parent,
            text="🚓 Police Required",
            font=("Arial",16,"bold")
        ).pack(anchor="w", padx=15, pady=(12,0))

        ctk.CTkLabel(
            parent,
            text=str(report[13])
        ).pack(anchor="w", padx=15)

        ctk.CTkLabel(
            parent,
            text="🚒 Fire Engines Required",
            font=("Arial",16,"bold")
        ).pack(anchor="w", padx=15, pady=(12,0))

        ctk.CTkLabel(
            parent,
            text=str(report[14])
        ).pack(anchor="w", padx=15)
        ai_details = self.db.get_ai_details(report[0])
        if ai_details and ai_details[0]:
            labels = [
                ("🤖 ML Incident Type", f"{ai_details[0]} ({float(ai_details[1] or 0):.0%})"),
                ("⚠ ML Severity Confidence", f"{float(ai_details[2] or 0):.0%}"),
                ("🛡 Report Authenticity", f"{ai_details[3] or 'Unknown'} ({float(ai_details[4] or 0):.0%})"),
                ("👁 Visual Reliability", f"{float(ai_details[5] or 0):.0%}"),
                ("🚗 Vehicles Detected", str(ai_details[6] or 0)),
                ("🏍 Motorcycles Detected", str(ai_details[7] or 0)),
                ("🧠 AI Summary", ai_details[8] or "Not available"),
            ]
            for label, value in labels:
                ctk.CTkLabel(parent, text=label, font=("Arial",16,"bold")).pack(anchor="w", padx=15, pady=(8,0))
                ctk.CTkLabel(parent, text=value, wraplength=750, justify="left").pack(anchor="w", padx=15)

        # Incident-specific ML visualisations: resource composition + confidence/priority.
        visual_panel = ctk.CTkFrame(parent, fg_color=PALETTE["panel2"], corner_radius=12, border_width=1, border_color=PALETTE["border"])
        visual_panel.pack(fill="x", padx=12, pady=(14, 10))
        ctk.CTkLabel(visual_panel, text="Incident Intelligence · model evidence and resource allocation", font=("Segoe UI", 15, "bold"), text_color=PALETTE["light"]).pack(anchor="w", padx=12, pady=(10, 2))
        try:
            from matplotlib.figure import Figure
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
            ai_row = self.db.get_ai_details(report[0])
            ai_conf = float(ai_row[1] or 0) * 100 if ai_row else 0
            sev_conf = float(ai_row[2] or 0) * 100 if ai_row else 0
            authenticity = float(ai_row[4] or 0) * 100 if ai_row else 0
            visual_conf = float(ai_row[5] or 0) * 100 if ai_row else 0
            fig = Figure(figsize=(10.2, 3.1), dpi=90, facecolor=PALETTE["panel2"])
            ax1, ax2 = fig.subplots(1, 2)
            ax1.set_facecolor(PALETTE["panel2"])
            resource_vals = [int(report[12] or 0), int(report[13] or 0), int(report[14] or 0)]
            if sum(resource_vals):
                wedges, _ = ax1.pie(resource_vals, startangle=90, colors=[PALETTE["lime"], PALETTE["olive"], PALETTE["green"]], wedgeprops={"width": .42, "edgecolor": PALETTE["panel2"]})
                ax1.legend(wedges, [f"Ambulance · {resource_vals[0]}", f"Police · {resource_vals[1]}", f"Fire · {resource_vals[2]}"], loc="lower center", bbox_to_anchor=(.5, -.13), ncol=1, fontsize=8, frameon=False, labelcolor=PALETTE["light"])
            else: ax1.text(.5,.5,"No predicted resources",ha="center",va="center",color=PALETTE["muted"])
            ax1.set_title("Predicted resource mix", color=PALETTE["light"], fontsize=10, fontweight="bold")
            ax2.set_facecolor(PALETTE["panel2"])
            conf_labels = ["Type", "Severity", "Authenticity", "Visual"]
            conf_vals = [ai_conf, sev_conf, authenticity, visual_conf]
            bars = ax2.barh(conf_labels[::-1], conf_vals[::-1], color=[PALETTE["deep"], PALETTE["green"], PALETTE["olive"], PALETTE["lime"]])
            ax2.set_xlim(0, 100); ax2.set_xlabel("Model confidence / reliability (%)", color=PALETTE["muted"], fontsize=8)
            ax2.set_title(f"AI confidence profile · Priority {report[16] or 0}/100", color=PALETTE["light"], fontsize=10, fontweight="bold")
            ax2.tick_params(colors=PALETTE["muted"], labelsize=8)
            for ax in (ax1, ax2):
                for spine in ax.spines.values(): spine.set_color(PALETTE["border"])
            ax2.bar_label(bars, fmt="%.0f%%", padding=2, color=PALETTE["light"], fontsize=8)
            fig.tight_layout(pad=1.8)
            canvas = FigureCanvasTkAgg(fig, master=visual_panel); canvas.draw()
            canvas.get_tk_widget().pack(fill="x", expand=True, padx=8, pady=(0, 2))
            toolbar = NavigationToolbar2Tk(canvas, visual_panel, pack_toolbar=False); toolbar.update(); toolbar.pack(fill="x", padx=8, pady=(0, 6))
        except Exception as exc:
            ctk.CTkLabel(visual_panel, text=f"Incident visualisation unavailable: {exc}", text_color=PALETTE["muted"]).pack(anchor="w", padx=12, pady=8)

# ========================================
# IMAGE
# ========================================
        ctk.CTkLabel(
            parent,
            text="📷 Evidence",
            font=("Arial",16,"bold")
        ).pack(anchor="w", padx=15, pady=(12,5))

        if report[5] and os.path.exists(report[5]):

            try:
                image = Image.open(report[5])
                preview = ctk.CTkImage(
                    light_image=image,
                    dark_image=image,
                    size=(300,200)
                )

                image_label = ctk.CTkLabel(parent, image=preview, text="")
                image_label.image = preview
                image_label.pack(padx=15, pady=5)

            except Exception:
                ctk.CTkLabel(
                    parent,
                    text="Unable to load image."
                ).pack(anchor="w", padx=15)

        else:

            ctk.CTkLabel(
                parent,
                text="No Image Uploaded"
            ).pack(anchor="w", padx=15)
# ========================================
# VIDEO
# ========================================
        ctk.CTkLabel(
            parent,
            text="🎥 Video",
            font=("Arial",16,"bold")
        ).pack(anchor="w", padx=15, pady=(12,5))

        if report[6] and os.path.exists(report[6]):
            ctk.CTkButton(
                parent,
                text="▶ Open Video",
                command=lambda p=report[6]: os.startfile(p)
            ).pack(anchor="w", padx=15)

        else:
            ctk.CTkLabel(
                parent,
                text="No Video Uploaded"
            ).pack(anchor="w", padx=15)

# ========================================
# ACCEPT INCIDENT
# ========================================

    def accept_incident(self, report):

        confirm = messagebox.askyesno(
            "Accept Incident", 
            f"Accept Incident {report[0]} ?"
        )

        if not confirm:
            return

        self.db.update_incident_status(report[0], "Accepted")
        from utils.notifications import notify_incident_owner_status
        notify_incident_owner_status(report[0], "Accepted", Session.department_name)

        messagebox.showinfo("Success", "Incident Accepted.")

        self.refresh_dashboard()

# ========================================
# COMPLETE INCIDENT
# ========================================

    def complete_incident(self, report):

        confirm = messagebox.askyesno(
            "Complete Incident",
            f"Complete Incident {report[0]} ?"
        )

        if not confirm:
            return

        self.db.update_incident_status(report[0], "Completed")
        from utils.notifications import notify_incident_owner_status
        notify_incident_owner_status(report[0], "Completed", Session.department_name)

        messagebox.showinfo("Completed", "Incident Completed.")

        self.refresh_dashboard()

# ========================================
# REFRESH DASHBOARD
# ========================================

    def refresh_dashboard(self):

        self.update_statistics()

        if self.current_page == "Dashboard":
            self.show_dashboard()

        elif self.current_page == "Waiting":
            self.show_waiting()

        elif self.current_page == "Accepted":
            self.show_accepted()

        elif self.current_page == "Completed":
            self.show_completed()
