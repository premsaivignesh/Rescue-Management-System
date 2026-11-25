import os
from PIL import Image
from datetime import datetime
import customtkinter as ctk
from tkinter import filedialog, messagebox
from ai.decision_engine import DecisionEngine
from ai_ml.predictions.combined_predictor import RescueAI
import json
from utils.notifications import notify_required_departments

from database.incident_db import IncidentDB
from utils.session import Session


class ReportIncident:

    def __init__(self, parent, dashboard):

        self.parent = parent
        self.dashboard = dashboard
        self.db = IncidentDB()
        self.ai = DecisionEngine()
        self.rescue_ai = RescueAI()

        self.image_path = ""
        self.video_path = ""

        self.last_incident = None

        self.create_ui()

# ========================================
# REPORT UI
# ========================================

    def create_ui(self):

        title = ctk.CTkLabel(
            self.parent,
            text="Report Incident",
            font=("Arial", 28, "bold")
        )
        title.pack(pady=20)

        self.type_menu = ctk.CTkOptionMenu(
            self.parent,
            values=[
                "Road Accident",
                "Fire",
                "Flood",
                "Building Collapse",
                "Medical Emergency",
                "Other"
            ]
        )
        self.type_menu.pack(pady=10)

        self.description = ctk.CTkTextbox(
            self.parent,
            width=500,
            height=120
        )
        self.description.pack(pady=10)

        self.address = ctk.CTkEntry(
            self.parent,
            width=500,
            placeholder_text="Enter Incident Address"
        )
        self.address.pack(pady=10)

# ========================================
# IMAGE
# ========================================

        ctk.CTkLabel(
            self.parent,
            text="Image"
        ).pack()

        ctk.CTkButton(
            self.parent,
            text="📷 Upload Image",
            command=self.upload_image
        ).pack(pady=5)

        self.image_preview = ctk.CTkLabel(
            self.parent,
            text=""
        )
        self.image_preview.pack(pady=(2, 0))

        self.image_label = ctk.CTkLabel(
            self.parent,
            text="No Image Selected",
            font=("Arial",14)
        )
        self.image_label.pack(pady=(0, 2))

        button_frame = ctk.CTkFrame(
            self.parent,
            fg_color="transparent"
        )
        button_frame.pack(pady=(0, 8))

        self.preview_btn = ctk.CTkButton(
            button_frame,
            text="Preview",
            width=90,
            command=self.preview_image
        )

        self.remove_image_btn = ctk.CTkButton(
            button_frame,
            text="🗑 Remove",
            width=90,
            command=self.remove_image
        )

        self.preview_btn.pack(side="left", padx=5)
        self.remove_image_btn.pack(side="left", padx=5)

        self.preview_btn.pack_forget()
        self.remove_image_btn.pack_forget()

# ========================================
# VIDEO
# ========================================

        ctk.CTkLabel(
            self.parent,
            text="Video"
        ).pack(pady=(8, 0))

        ctk.CTkButton(
            self.parent,
            text="🎥 Upload Video",
            command=self.upload_video
        ).pack(pady=5)

        self.video_label = ctk.CTkLabel(
            self.parent,
            text="No Video Selected"
        )
        self.video_label.pack()

        self.remove_video_btn = ctk.CTkButton(
            self.parent,
            text="🗑 Remove Video",
            command=self.remove_video
        )
        self.remove_video_btn.pack(pady=5)
        self.remove_video_btn.pack_forget()

# ========================================
# BUTTONS
# ========================================

        self.submit_btn = ctk.CTkButton(
            self.parent,
            text="🚨 Submit Incident",
            width=220,
            command=self.submit
        )
        self.submit_btn.pack(pady=20)

        self.undo_btn = ctk.CTkButton(
            self.parent,
            text="Undo Last Incident",
            width=220,
            command=self.undo_incident
        )
        self.undo_btn.pack()
        self.undo_btn.pack_forget()

# ========================================
# STATUS PANEL
# ========================================

        self.status_frame = ctk.CTkFrame(
            self.parent,
            width=600,
            corner_radius=10
        )

        self.status_title = ctk.CTkLabel(
            self.status_frame,
            text="",
            font=("Arial",22,"bold")
        )

        self.status_title.pack(pady=(15,10))

        self.status_info = ctk.CTkLabel(
            self.status_frame,
            text="",
            justify="left",
            font=("Arial",15)
        )

        self.status_info.pack(pady=(0,20))

        self.status_frame.pack_forget()

# ========================================
# IMAGE FUNCTIONS
# ========================================

    def upload_image(self):

        path = filedialog.askopenfilename(
            filetypes=[
                ("Images","*.jpg *.jpeg *.png")
            ]
        )

        if path:
            self.image_path = path
            self.image_label.configure(
                text="✔ " + os.path.basename(path)
            )

            image = Image.open(path)
            image.thumbnail((120,120))

            thumbnail = ctk.CTkImage(
                light_image=image,
                dark_image=image,
                size=image.size
            )

            self.image_preview.configure(
                image=thumbnail,
                text=""
            )

            self.image_preview.image = thumbnail
            self.preview_btn.pack(side="left", padx=5)
            self.remove_image_btn.pack(side="left", padx=5)

    def remove_image(self):

        self.image_path = ""
        self.image_preview.configure(
            image=None,
            text=""
        )

        self.image_label.configure(
            text="No Image Selected"
        )

        self.preview_btn.pack_forget()
        self.remove_image_btn.pack_forget()

# ========================================
# IMAGE PREVIEW
# ========================================

    def preview_image(self):

        if self.image_path == "":
            return

        window = ctk.CTkToplevel(self.parent)
        window.title("Image Preview")
        window.geometry("700x600")
        image = Image.open(self.image_path)
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
        label.pack(pady=20)

# ========================================
# VIDEO FUNCTIONS
# ========================================

    def upload_video(self):

        path = filedialog.askopenfilename(
            filetypes=[
                ("Videos","*.mp4 *.avi *.mov")
            ]
        )

        if path == "":
            return

        size = os.path.getsize(path)
        size_mb = size / (1024 * 1024)

        if size_mb > 200:

            messagebox.showerror(
                "Video Too Large",
                "Please select a video smaller than 200 MB."
            )

            return

        self.video_path = path

        size = os.path.getsize(self.video_path)
        size_mb = size / (1024 * 1024)

        self.video_label.configure(
            text=f"✔ {os.path.basename(self.video_path)} ({size_mb:.2f} MB)"
        )

        self.remove_video_btn.pack(pady=5)

# ========================================
# REMOVE VIDEO
# ========================================

    def remove_video(self):

        self.video_path = ""

        self.video_label.configure(
            text="No Video Selected"
        )

        self.remove_video_btn.pack_forget()

# ========================================
# INCIDENT ID
# ========================================

    def generate_incident_id(self):

        today = datetime.now().strftime("%Y%m%d")

        last = self.db.get_last_incident_id()

        if last is None:
            return f"RMS-{today}-0001"

        last_id = last[0]

        try:

            last_date = last_id.split("-")[1]

            last_number = int(last_id.split("-")[2])

        except:

            return f"RMS-{today}-0001"

        if last_date == today:
            last_number += 1
        else:
            last_number = 1

        return f"RMS-{today}-{last_number:04d}"

# ========================================
# SUBMIT INCIDENT
# ========================================

    def submit(self):

        incident_type = self.type_menu.get()
        description = self.description.get("1.0", "end").strip()
        address = self.address.get().strip()

        if len(description) < 15:
            messagebox.showerror("Description", "Description must contain at least 15 characters.")
            return

        if len(address) < 10:
            messagebox.showerror("Address", "Please enter a valid address.")
            return

        if self.image_path == "" and self.video_path == "":
            messagebox.showerror("Evidence Required", "Upload at least one Image or Video")
            return

        incident_id = self.generate_incident_id()
        self.last_incident = {
            "incident_id": incident_id, "incident_type": incident_type,
            "description": description, "address": address,
            "image_path": self.image_path, "video_path": self.video_path
        }

        self.db.add_incident(
            incident_id, Session.user_id, incident_type, description, address,
            self.image_path, self.video_path, 0, 0, "Pending", "Waiting",
            0, 0, 0, 0, "Pending", 0, "AI Processing"
        )

        try:
            result = self.rescue_ai.analyze_incident(
                description=description, incident_type_hint=incident_type,
                image_path=self.image_path or None, video_path=self.video_path or None
            )
            text = result["text"]
            resources = result["resources"]
            evidence = result["evidence"]
            summary = (f"{text['incident_type']} | {text['severity']} | "
                       f"Genuine={result['spam']['label']} | "
                       f"Priority={result['priority']}/100 | Department={result['department']}")

            self.db.update_multimodal_ai_result(
                incident_id, json.dumps(result, default=str),
                text["incident_type"], float(text["incident_type_confidence"]),
                text["severity"], float(text["severity_confidence"]),
                result["spam"]["label"], float(result["spam"]["confidence"]),
                evidence["people_estimated"], evidence["vehicle_count"],
                evidence["motorcycle_count"], evidence["overall_reliability"],
                resources["ambulance"], resources["police"], resources["fire"],
                result["department"], result["priority"], result["status"], summary
            )
            notify_required_departments(incident_id, resources, text["severity"], result["priority"])
            self.show_status_panel(incident_id, result)
            self.undo_btn.pack(pady=10)
            self.dashboard.refresh_dashboard()

        except Exception as exc:
            fallback = self.ai.analyze(incident_type, description)
            self.db.update_ai_result(
                incident_id, fallback["severity"], fallback["people"], fallback["ambulance"],
                fallback["police"], fallback["fire"], fallback["department"],
                fallback["priority"], "Fallback Rules: AI unavailable"
            )
            fallback["ai_error"] = str(exc)
            self.show_status_panel(incident_id, fallback)
            self.undo_btn.pack(pady=10)
            self.dashboard.refresh_dashboard()

# CLEAR FORM
# ========================================

    def clear_form(self):

        self.type_menu.set("Road Accident")

        self.description.delete("1.0", "end")

        self.address.delete(0, "end")

        self.image_path = ""

        self.image_preview.configure(
            image=None,
            text=""
        )
        self.video_path = ""

        self.image_label.configure(
            text="No Image Selected"
        )

        self.video_label.configure(
            text="No Video Selected"
        )

        self.remove_image_btn.pack_forget()
        self.remove_video_btn.pack_forget()

# ========================================
# UNDO INCIDENT
# ========================================

    def undo_incident(self):

        if self.last_incident is None:
            return

        self.db.delete_incident(
            self.last_incident["incident_id"]
        )

        self.type_menu.set(
            self.last_incident["incident_type"]
        )

        self.description.insert(
            "1.0",
            self.last_incident["description"]
        )

        self.address.insert(
            0,
            self.last_incident["address"]
        )

        self.image_path = self.last_incident["image_path"]
        self.video_path = self.last_incident["video_path"]

        if self.image_path != "":

            image = Image.open(self.image_path)

            image.thumbnail((120,120))

            thumbnail = ctk.CTkImage(
                light_image=image,
                dark_image=image,
                size=image.size
            )

            self.image_preview.configure(
                image=thumbnail,
                text=""
            )

            self.image_preview.image = thumbnail

            self.image_label.configure(
                text="✔ " + os.path.basename(self.image_path)
            )

            self.preview_btn.pack(side="left", padx=5)

            self.remove_image_btn.pack(side="left", padx=5)

        if self.video_path != "":

            size = os.path.getsize(self.video_path)
            size_mb = size / (1024 * 1024)

            self.video_label.configure(
                text=f"✔ {os.path.basename(self.video_path)} ({size_mb:.2f} MB)"
            )

            self.remove_video_btn.pack(pady=5)

        self.undo_btn.pack_forget()

        self.status_frame.pack_forget()
        self.last_incident = None

# ========================================
# STATUS PANEL
# ========================================

    def show_status_panel(self, incident_id, result):

        image = "Yes" if self.last_incident["image_path"] else "No"
        video = "Yes" if self.last_incident["video_path"] else "No"
        self.status_title.configure(text="✅ Incident Submitted & AI Assessed")

        if "text" in result:
            text = result["text"]
            evidence = result["evidence"]
            resources = result["resources"]
            info = f"""Incident ID
{incident_id}

AI Incident Type : {text['incident_type']} ({text['incident_type_confidence']:.0%})
AI Severity      : {text['severity']} ({text['severity_confidence']:.0%})
Report Check     : {result['spam']['label']} ({result['spam']['confidence']:.0%})
AI Reliability   : {evidence['overall_reliability']:.0%}

Priority Score   : {result['priority']}/100
Department       : {result['department']}
People Estimated : {evidence['people_estimated']}
Vehicles         : {evidence['vehicle_count']}
Motorcycles      : {evidence['motorcycle_count']}

🚑 Ambulance : {resources['ambulance']}
🚓 Police    : {resources['police']}
🚒 Fire      : {resources['fire']}

📷 Image : {image}
🎥 Video : {video}"""
        else:
            info = f"""Incident ID : {incident_id}

AI Status : {result['status']}
Department : {result['department']}
Severity : {result['severity']}
Priority : {result['priority']}/100
Estimated People : {result['people']}

🚑 Ambulance : {result['ambulance']}
🚓 Police : {result['police']}
🚒 Fire : {result['fire']}

📷 Image : {image}
🎥 Video : {video}"""

        self.status_info.configure(text=info)
        self.status_frame.pack(pady=20, fill="x", padx=30)

