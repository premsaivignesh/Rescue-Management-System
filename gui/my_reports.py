import os
import json
import customtkinter as ctk

from tkinter import messagebox
from database.incident_db import IncidentDB
from utils.session import Session


class MyReports:

    def __init__(self,parent,active_only=False):

        self.parent = parent
        self.db = IncidentDB()
        self.open_card = None
        self.active_only = active_only
        self.create_ui()

# ========================================
# UI
# ========================================

    def create_ui(self):

        title = ctk.CTkLabel(
            self.parent,
            text="My Reports",
            font=("Arial",28,"bold")
        )

        title.pack(pady=20)

        self.search = ctk.CTkEntry(
            self.parent,
            width=300,
            placeholder_text="Search Incident ID"
        )

        self.search.pack(pady=10)

        ctk.CTkButton(
            self.parent,
            text="Search",
            command=self.search_reports
        ).pack()

        self.report_frame = ctk.CTkScrollableFrame(
            self.parent,
            width=900,
            height=500
        )

        self.report_frame.pack(
            fill="both",
            expand=True,
            pady=20
        )

        self.load_reports()

# ========================================
# LOAD REPORTS
# ========================================

    def load_reports(self):

        for widget in self.report_frame.winfo_children():
            widget.destroy()

        if self.active_only:
            reports = self.db.get_active_incidents(
                Session.user_id
            )
        else:
            reports = self.db.get_user_incidents(
                Session.user_id
            )

        if len(reports)==0:

            ctk.CTkLabel(
                self.report_frame,
                text="No Reports Found",
                font=("Arial",20)
            ).pack(pady=40)

            return

        for report in reports:

            self.create_card(report)

# ========================================
# SEARCH REPORTS
# ========================================

    def search_reports(self):

        keyword = self.search.get().strip()

        for widget in self.report_frame.winfo_children():
            widget.destroy()

        if keyword == "":
            self.load_reports()
            return

        reports = self.db.search_incidents(
            Session.user_id,
            keyword
        )

        if len(reports) == 0:

            ctk.CTkLabel(
                self.report_frame,
                text="No Reports Found",
                font=("Arial",18)
            ).pack(pady=30)

            return

        for report in reports:

            self.create_card(report)

# ========================================
# REPORT CARD
# ========================================

    def create_card(self,report):

        card = ctk.CTkFrame(
            self.report_frame, corner_radius=14, border_width=1,
            border_color="#39452D", fg_color="#1B2117"
        )

        card.pack(fill="x", padx=12, pady=9)

        ctk.CTkLabel(
            card,
            text=f"🚨 {report[2]}",
            font=("Arial",16,"bold")
        ).pack(anchor="w",padx=15,pady=(10,0))

        ctk.CTkLabel(
            card,
            text=f"🆔 {report[0]}"
        ).pack(anchor="w",padx=15)

        status = report[10]

        ctk.CTkLabel(
            card,
            text=f"📅 {report[17]}"
        ).pack(anchor="w", padx=15)

        if str(status).lower() in ("active", "accepted", "in progress"):
            status = f"🟢 {status}"
        elif str(status).lower() in ("pending", "waiting", "ai processing"):
            status = f"🟡 {status}"
        elif str(status).lower() in ("closed", "completed"):
            status = f"✅ {status}"

        ctk.CTkLabel(
            card,
            text=f"Status : {status}"
        ).pack(anchor="w", padx=15)

        button_frame = ctk.CTkFrame(
            card,
            fg_color="transparent"
        )

        button_frame.pack(anchor="w", padx=15, pady=10)

        details = ctk.CTkFrame(card, corner_radius=12)
        details.pack(fill="x", padx=15, pady=(0,10))
        details.pack_forget()

        card.details_frame = details
        card.details_visible = False

        # Edit Frame
        edit_frame = ctk.CTkFrame(
            card,
            corner_radius=12
        )
        edit_frame.pack(
            fill="x",
            padx=20,
            pady=(0,15)
        )
        edit_frame.pack_forget()

        card.edit_frame = edit_frame
        card.edit_visible = False

        view_btn = ctk.CTkButton(
            button_frame,
            text="▼ View Details",
            width=130,
            command=lambda c=card, r=report: self.toggle_details(c, r)
        )
        view_btn.pack(side="left", padx=5)
        card.view_button = view_btn

        if report[10] == "Waiting":

            edit_btn = ctk.CTkButton(
                button_frame,
                text="✏ Edit",
                width=90,
                command=lambda c=card, r=report: self.toggle_edit(c, r)
            )
            edit_btn.pack(side="left", padx=5)
            card.edit_button = edit_btn

            ctk.CTkButton(
                button_frame,
                text="🗑 Delete",
                width=90,
                command=lambda r=report: self.delete_report(r)
            ).pack(side="left", padx=5)

# ========================================
# TOGGLE DETAILS
# ========================================

    def toggle_details(self, card, report):
    
        if card.details_visible:
            card.details_frame.pack_forget()
            card.details_visible = False
            card.view_button.configure(
                text="▼ View Details"
            )
            self.open_card = None
            return

        if self.open_card is not None and self.open_card != card:
            try:
                self.open_card.details_frame.pack_forget()
                self.open_card.details_visible = False
                self.open_card.view_button.configure(
                    text="▼ View Details"
                )
            except:
                pass

        for widget in card.details_frame.winfo_children():
            widget.destroy()

        ctk.CTkLabel(
            card.details_frame,
            text="📋 Incident Description",
            font=("Arial",16,"bold")
        ).pack(anchor="w", padx=10, pady=(10,0))

        ctk.CTkLabel(
            card.details_frame,
            text=report[3],
            wraplength=700,
            justify="left"
        ).pack(anchor="w", padx=10)

        ctk.CTkLabel(
            card.details_frame,
            text="📍 Address",
            font=("Arial",16,"bold")
        ).pack(anchor="w", padx=10, pady=(10,0))

        ctk.CTkLabel(
            card.details_frame,
            text=report[4]
        ).pack(anchor="w", padx=10)

        ctk.CTkLabel(
            card.details_frame,
            text="🤖 AI Status",
            font=("Arial",16,"bold")
        ).pack(anchor="w", padx=10, pady=(10,0))

        ctk.CTkLabel(
            card.details_frame,
            text=report[16]
        ).pack(anchor="w", padx=10)

        ctk.CTkLabel(
            card.details_frame,
            text="🚑 Assigned Department",
            font=("Arial",16,"bold")
        ).pack(anchor="w", padx=10, pady=(10,0))

        ctk.CTkLabel(
            card.details_frame,
            text=report[15]
        ).pack(anchor="w", padx=10)

        ctk.CTkLabel(
            card.details_frame,
            text="📂 Evidence",
            font=("Arial",16,"bold")
        ).pack(anchor="w", padx=10, pady=(15,5))

        image_name = "No Image"

        if report[5]:
            image_name = os.path.basename(report[5])

        video_name = "No Video"

        if report[6]:
            video_name = os.path.basename(report[6])

        image_frame = ctk.CTkFrame(
            card.details_frame,
            fg_color="transparent"
        )

        image_frame.pack(anchor="w", padx=10)
        ctk.CTkLabel(
            image_frame,
            text=f"📷 {image_name}"
        ).pack(side="left")
        if report[5]:
            ctk.CTkButton(
                image_frame,
                text="Preview",
                width=80,
                command=lambda p=report[5]: self.preview_image(p)
            ).pack(side="left", padx=10)

        video_frame = ctk.CTkFrame(
            card.details_frame,
            fg_color="transparent"
        )
        video_frame.pack(anchor="w", padx=10)
        ctk.CTkLabel(
            video_frame,
            text=f"🎥 {video_name}"
        ).pack(side="left")
        if report[6]:
            ctk.CTkButton(
                video_frame,
                text="Play",
                width=80,
                command=lambda p=report[6]: self.play_video(p)
            ).pack(side="left", padx=10)

        ctk.CTkFrame(
            card.details_frame,
            height=2
        ).pack(fill="x", pady=10)

        ctk.CTkLabel(
            card.details_frame,
            text="🤖 AI Analysis",
            font=("Arial",17,"bold")
        ).pack(anchor="w", padx=10, pady=(10,5))

        # Read the actual multimodal model output saved by the incident pipeline.
        # SELECT * keeps the original database column order; AI JSON is queried separately.
        ai_row = self.db.get_ai_details(report[0])
        ai = {}
        if ai_row and len(ai_row) > 9 and ai_row[9]:
            try:
                ai = json.loads(ai_row[9])
            except (ValueError, TypeError):
                ai = {}
        text_result = ai.get("text") or {}
        evidence = ai.get("evidence") or {}
        resources = ai.get("resources") or {}
        severity = report[9] or "Not available"
        people = report[11] if report[11] is not None else evidence.get("people_estimated", "Not available")
        ambulance = report[12] or 0
        police = report[13] or 0
        fire = report[14] or 0
        department = report[15] or "Not assigned"
        priority = report[16] if isinstance(report[16], (int, float)) else 0
        # ai_status is column 17 in the original table; report[16] is priority_score.
        ai_status = report[17] or "AI result unavailable"
        ai_details = [
            ("Severity", severity),
            ("Incident type confidence", f"{float(ai_row[1] or 0)*100:.1f}%" if ai_row else "Not available"),
            ("Severity confidence", f"{float(ai_row[2] or 0)*100:.1f}%" if ai_row else "Not available"),
            ("Spam check", ai_row[3] or "Not available" if ai_row else "Not available"),
            ("Estimated people (fused estimate)", people),
            ("Ambulances predicted", resources.get("ambulance", ambulance)),
            ("Police units predicted", resources.get("police", police)),
            ("Fire engines predicted", resources.get("fire", fire)),
            ("Assigned department", department),
            ("Priority score", f"{priority}/100"),
            ("AI review", ai_status),
            ("AI summary", ai_row[8] if ai_row and ai_row[8] else "Analysis summary was not saved for this older report."),
        ]
        for label, value in ai_details:
            ctk.CTkLabel(card.details_frame, text=f"{label}: {value}",
                         text_color="#DDE8C5", anchor="w", justify="left",
                         wraplength=760).pack(anchor="w", padx=20, pady=3)

        # Per-report dashboard: resource donut + model confidence profile, with zoom/pan controls.
        chart_box = ctk.CTkFrame(card.details_frame, fg_color="#252D1E", corner_radius=10,
                                 border_width=1, border_color="#39452D")
        chart_box.pack(fill="x", padx=12, pady=(10, 12))
        ctk.CTkLabel(chart_box, text="Incident ML Evidence · report-specific visualisation",
                     font=("Segoe UI", 15, "bold"), text_color="#DDE8C5").pack(anchor="w", padx=12, pady=(10, 2))
        try:
            from matplotlib.figure import Figure
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
            fig = Figure(figsize=(10.2, 3.2), dpi=90, facecolor="#252D1E")
            ax1, ax2 = fig.subplots(1, 2)
            ax1.set_facecolor("#252D1E")
            vals = [int(resources.get("ambulance", ambulance) or 0), int(resources.get("police", police) or 0), int(resources.get("fire", fire) or 0)]
            if sum(vals):
                wedges, _ = ax1.pie(vals, startangle=90, colors=["#B8C985", "#68783B", "#78934A"], wedgeprops={"width": .42, "edgecolor": "#252D1E"})
                ax1.legend(wedges, [f"Ambulance · {vals[0]}", f"Police · {vals[1]}", f"Fire engine · {vals[2]}"], loc="lower center", bbox_to_anchor=(.5, -.15), ncol=1, fontsize=8, frameon=False, labelcolor="#DDE8C5")
            else: ax1.text(.5,.5,"No resources predicted",ha="center",va="center",color="#AAB69A")
            ax1.set_title("Resource demand · donut", color="#DDE8C5", fontsize=10, fontweight="bold")
            ai_conf = float(ai_row[1] or 0) * 100 if ai_row else 0
            sev_conf = float(ai_row[2] or 0) * 100 if ai_row else 0
            spam_conf = float(ai_row[4] or 0) * 100 if ai_row else 0
            visual_conf = float(ai_row[5] or 0) * 100 if ai_row else 0
            ax2.set_facecolor("#252D1E")
            labs = ["Type", "Severity", "Authenticity", "Visual reliability"]
            confs = [ai_conf, sev_conf, spam_conf, visual_conf]
            bars = ax2.barh(labs[::-1], confs[::-1], color=["#43532D", "#78934A", "#68783B", "#B8C985"])
            ax2.set_xlim(0,100); ax2.set_xlabel("Confidence / reliability (%)", color="#AAB69A", fontsize=8)
            ax2.set_title(f"Model confidence profile · Priority {priority}/100", color="#DDE8C5", fontsize=10, fontweight="bold")
            ax2.tick_params(colors="#AAB69A", labelsize=8)
            ax2.bar_label(bars, fmt="%.0f%%", padding=2, color="#DDE8C5", fontsize=8)
            for ax in (ax1, ax2):
                for spine in ax.spines.values(): spine.set_color("#39452D")
            fig.tight_layout(pad=1.8)
            canvas = FigureCanvasTkAgg(fig, master=chart_box); canvas.draw()
            canvas.get_tk_widget().pack(fill="x", expand=True, padx=8, pady=(0, 2))
            toolbar = NavigationToolbar2Tk(canvas, chart_box, pack_toolbar=False); toolbar.update(); toolbar.pack(fill="x", padx=8, pady=(0, 6))
        except Exception as exc:
            ctk.CTkLabel(chart_box, text=f"Per-incident charts unavailable: {exc}", text_color="#AAB69A").pack(anchor="w", padx=12, pady=8)

        card.details_frame.pack(
            fill="x",
            padx=15,
            pady=(0,10)
        )

        card.details_visible = True
        self.open_card = card

        card.view_button.configure(
            text="▲ Hide Details"
        )

# ========================================
# IMAGE PREVIEW
# ========================================

    def preview_image(self, path):
        from PIL import Image
        window = ctk.CTkToplevel(self.parent)
        window.title("Image Preview")
        window.geometry("700x600")
        image = Image.open(path)
        image.thumbnail((650,550))

        preview = ctk.CTkImage(
            light_image=image,
            dark_image=image,
            size=image.size
        )

        label = ctk.CTkLabel(
            window,
            image=preview,
            text=""
        )

        label.image = preview
        label.pack(expand=True,pady=20)

# ========================================
# PLAY VIDEO
# ========================================

    def play_video(self, path):
        import os
        os.startfile(path)

# ========================================
# TOGGLE EDIT
# ========================================

    def toggle_edit(self, card, report):

        if report[10] != "Waiting":

            messagebox.showwarning(
                "Edit Disabled",
                "This incident can no longer be edited."
            )
            return

        if card.details_visible:
            card.details_frame.pack_forget()
            card.details_visible = False
            card.view_button.configure(
                text="▼ View Details"
            )

        if card.edit_visible:
            card.edit_frame.pack_forget()
            card.edit_visible = False
            card.edit_button.configure(
                text="✏ Edit"
            )
            return
        for widget in card.edit_frame.winfo_children():
            widget.destroy()

        ctk.CTkLabel(
            card.edit_frame,
            text="✏ Edit Incident",
            font=("Arial",18,"bold")
        ).pack(pady=10)

        ctk.CTkLabel(
            card.edit_frame,
            text="Incident Type",
            font=("Arial",15,"bold")
        ).pack(anchor="w", padx=20)

        type_box = ctk.CTkComboBox(
            card.edit_frame,
            values=[
                "Road Accident",
                "Fire",
                "Medical",
                "Flood",
                "Earthquake",
                "Other"
            ],
            width=250
        )
        type_box.pack(pady=5)
        type_box.set(report[2])
        card.type_box = type_box

        ctk.CTkLabel(
            card.edit_frame,
            text="Description",
            font=("Arial",15,"bold")
        ).pack(anchor="w", padx=20, pady=(10,0))

        description = ctk.CTkTextbox(
            card.edit_frame,
            width=500,
            height=100
        )
        description.pack(pady=10)
        description.insert("1.0", report[3])
        card.description_box = description

        ctk.CTkLabel(
            card.edit_frame,
            text="Address",
            font=("Arial",15,"bold")
        ).pack(anchor="w", padx=20, pady=(10,0))

        address = ctk.CTkEntry(
            card.edit_frame,
            width=500
        )
        address.pack(pady=10)
        address.insert(0, report[4])
        card.address_box = address

        card.edit_frame.pack(
            fill="x",
            padx=20,
            pady=(0,15)
        )

        card.edit_visible = True
        card.edit_button.configure(
            text="❌ Cancel"
        )

        button_frame = ctk.CTkFrame(
            card.edit_frame,
            fg_color="transparent"
        )

        button_frame.pack(pady=15)

        ctk.CTkButton(
            button_frame,
            text="💾 Save Changes",
            width=140,
            command=lambda:self.save_changes(card,report)
        ).pack(side="left",padx=10)

        ctk.CTkButton(
            button_frame,
            text="Cancel",
            width=100,
            command=lambda:self.toggle_edit(card,report)
        ).pack(side="left")

# ========================================
# SAVE CHANGES
# ========================================

    def save_changes(self, card, report):

        if report[10] != "Waiting":
            messagebox.showwarning(
                "Edit Disabled",
                "This incident has already been accepted by the department and cannot be edited."
            )
            return

        incident_type = card.type_box.get()
        description = card.description_box.get(
            "1.0",
            "end"
        ).strip()
        address = card.address_box.get().strip()
        
        from tkinter import messagebox
        if description == "":
            messagebox.showerror(
                "Error",
                "Description cannot be empty."
            )
            return
        if address == "":
            messagebox.showerror(
                "Error",
                "Address cannot be empty."
            )
            return

        self.db.update_incident(
            report[0],
            incident_type,
            description,
            address
        )
        messagebox.showinfo("Success", "Incident updated successfully.")

        self.load_reports()

        card.edit_visible = False
        self.open_card = None
        self.open_edit_card = None

# ========================================
# DELETE REPORT
# ========================================

    def delete_report(self, report):

        if report[10] != "Waiting":

            messagebox.showwarning(
                "Delete Disabled",
                "This incident has already been accepted by the department and cannot be deleted."
            )
            return

        answer = messagebox.askyesno(
            "Delete Incident",
        "Are you sure you want to delete this incident?"
        )

        if not answer:
            return

        self.db.delete_incident(report[0])
        messagebox.showinfo(
            "Deleted",
            "Incident deleted successfully."
        )

        self.open_card = None
        self.load_reports()