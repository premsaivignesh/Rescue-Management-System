"""Interactive olive-theme operational analytics for the desktop rescue app."""
import customtkinter as ctk
from collections import Counter

PALETTE = {
    "bg": "#10130D", "panel": "#1B2117", "panel2": "#252D1E",
    "olive": "#68783B", "green": "#78934A", "light": "#DDE8C5",
    "muted": "#AAB69A", "border": "#39452D", "danger": "#D97757",
    "lime": "#B8C985", "deep": "#43532D"
}


def build_analytics(parent, incident_db, user_id=None, title="Operational Analytics"):
    """Database-driven analytics with mixed chart types and Matplotlib zoom/pan toolbar."""
    for widget in parent.winfo_children():
        widget.destroy()
    parent.configure(fg_color=PALETTE["bg"])
    header = ctk.CTkFrame(parent, fg_color="transparent")
    header.pack(fill="x", padx=26, pady=(20, 8))
    ctk.CTkLabel(header, text=title, font=("Segoe UI", 28, "bold"), text_color=PALETTE["light"]).pack(anchor="w")
    ctk.CTkLabel(header, text="Live incident intelligence • operational demand • severity and response performance", font=("Segoe UI", 13), text_color=PALETTE["muted"]).pack(anchor="w", pady=(3, 0))
    query = "SELECT incident_type,severity,status,priority_score,ambulance_required,police_required,fire_engine_required,report_time,department_assigned,ai_incident_confidence,ai_severity_confidence,spam_result,spam_confidence,visual_reliability FROM incidents"
    params = ()
    if user_id is not None:
        query += " WHERE user_id=?"
        params = (user_id,)
    try:
        incident_db.cursor.execute(query, params)
        rows = incident_db.cursor.fetchall()
    except Exception as exc:
        ctk.CTkLabel(parent, text=f"Analytics could not be loaded: {exc}", text_color=PALETTE["danger"]).pack(padx=26, pady=20)
        return
    total = len(rows)
    active = sum(str(r[2] or "").lower() not in ("completed", "closed") for r in rows)
    critical = sum(str(r[1] or "").lower() == "critical" for r in rows)
    high = sum(str(r[1] or "").lower() == "high" for r in rows)
    ambulances, police, fire = (sum(int(r[i] or 0) for r in rows) for i in (4, 5, 6))
    cards = ctk.CTkFrame(parent, fg_color="transparent")
    cards.pack(fill="x", padx=20, pady=5)
    metrics = [("TOTAL INCIDENTS", total), ("ACTIVE CASES", active), ("HIGH / CRITICAL", high + critical), ("AMBULANCE UNITS", ambulances), ("POLICE UNITS", police), ("FIRE ENGINES", fire)]
    for label, value in metrics:
        card = ctk.CTkFrame(cards, fg_color=PALETTE["panel"], corner_radius=13, border_width=1, border_color=PALETTE["border"])
        card.pack(side="left", fill="both", expand=True, padx=4, pady=4)
        ctk.CTkLabel(card, text=label, font=("Segoe UI", 10, "bold"), text_color=PALETTE["muted"]).pack(anchor="w", padx=10, pady=(12, 4))
        ctk.CTkLabel(card, text=str(value), font=("Segoe UI", 24, "bold"), text_color=PALETTE["light"]).pack(anchor="w", padx=10, pady=(0, 10))
    host = ctk.CTkScrollableFrame(parent, fg_color=PALETTE["panel"], corner_radius=15, border_width=1, border_color=PALETTE["border"])
    host.pack(fill="both", expand=True, padx=26, pady=(10, 20))
    try:
        from matplotlib.figure import Figure
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
        types = Counter(str(r[0] or "Unspecified") for r in rows)
        severity = Counter(str(r[1] or "Pending") for r in rows)
        status = Counter(str(r[2] or "Unknown") for r in rows)
        departments = Counter(str(r[8] or "Unassigned") for r in rows)
        priorities = [float(r[3] or 0) for r in rows]
        confidence = [float(r[9] or 0) * 100 for r in rows if r[9] is not None]
        spam = Counter(str(r[11] or "Not evaluated") for r in rows)
        fig = Figure(figsize=(13, 9), dpi=95, facecolor=PALETTE["panel"])
        axs = [fig.add_subplot(321), fig.add_subplot(322), fig.add_subplot(323), fig.add_subplot(324), fig.add_subplot(325), fig.add_subplot(326)]
        def style(ax, heading):
            ax.set_facecolor(PALETTE["panel2"])
            ax.set_title(heading, color=PALETTE["light"], fontsize=11, fontweight="bold", pad=10)
            ax.tick_params(colors=PALETTE["muted"], labelsize=8)
            for spine in ax.spines.values(): spine.set_color(PALETTE["border"])
            ax.grid(axis="y", alpha=.16, color=PALETTE["muted"])
            ax.set_axisbelow(True)
        # Donut: severity composition
        labels, vals = list(severity.keys()) or ["No data"], list(severity.values()) or [1]
        wedges, _ = axs[0].pie(vals, labels=None, startangle=90, wedgeprops={"width": .38, "edgecolor": PALETTE["panel"]}, colors=[PALETTE["green"], PALETTE["olive"], PALETTE["lime"], PALETTE["deep"], "#87906A"])
        axs[0].legend(wedges, labels, loc="lower center", bbox_to_anchor=(.5, -.18), ncol=2, fontsize=8, frameon=False, labelcolor=PALETTE["light"])
        axs[0].set_title("Severity Mix · Donut", color=PALETTE["light"], fontsize=11, fontweight="bold")
        # Horizontal ranked incident types
        style(axs[1], "Incident Categories · Ranked")
        items = types.most_common()
        axs[1].barh([x[0] for x in items][::-1], [x[1] for x in items][::-1], color=PALETTE["green"])
        # workflow stack-like horizontal status view
        style(axs[2], "Response Workflow · Status")
        sl, sv = list(status.keys()) or ["No data"], list(status.values()) or [0]
        axs[2].bar(sl, sv, color=[PALETTE["olive"], PALETTE["lime"], PALETTE["green"], PALETTE["deep"]])
        axs[2].tick_params(axis="x", rotation=18)
        # resource demand pie
        style(axs[3], "Resource Allocation · Share")
        resource_values = [ambulances, police, fire]
        if sum(resource_values):
            axs[3].pie(resource_values, labels=["Ambulance", "Police", "Fire"], autopct="%1.0f%%", startangle=90, colors=[PALETTE["lime"], PALETTE["olive"], PALETTE["green"]], textprops={"color": PALETTE["light"], "fontsize": 8})
        else:
            axs[3].text(.5, .5, "No resource demand yet", ha="center", va="center", color=PALETTE["muted"])
        axs[3].set_title("Resource Allocation · Share", color=PALETTE["light"], fontsize=11, fontweight="bold")
        # priority distribution histogram
        style(axs[4], "Priority Score · Distribution")
        if priorities:
            axs[4].hist(priorities, bins=[0, 20, 40, 60, 80, 101], color=PALETTE["green"], edgecolor=PALETTE["light"], alpha=.9)
            axs[4].set_xlabel("Priority score / 100", color=PALETTE["muted"], fontsize=8)
        else: axs[4].text(.5, .5, "No priority scores", transform=axs[4].transAxes, ha="center", color=PALETTE["muted"])
        # AI model confidence distribution
        style(axs[5], "AI Type Confidence · Distribution")
        if confidence:
            axs[5].boxplot(confidence, vert=True, patch_artist=True, boxprops={"facecolor": PALETTE["olive"], "color": PALETTE["lime"]}, medianprops={"color": PALETTE["light"]}, whiskerprops={"color": PALETTE["muted"]}, capprops={"color": PALETTE["muted"]})
            axs[5].set_ylabel("Confidence (%)", color=PALETTE["muted"], fontsize=8)
            axs[5].set_xticks([1], ["Classifier"])
            axs[5].set_ylim(0, 100)
        else: axs[5].text(.5, .5, "No saved confidence values", transform=axs[5].transAxes, ha="center", color=PALETTE["muted"])
        fig.tight_layout(pad=2.2)
        canvas = FigureCanvasTkAgg(fig, master=host)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=(10, 0))
        toolbar = NavigationToolbar2Tk(canvas, host, pack_toolbar=False)
        toolbar.update()
        toolbar.pack(fill="x", padx=10, pady=(0, 8))
        ctk.CTkLabel(host, text=f"Dataset: {total} stored incidents  •  {active} active  •  predicted units: {ambulances} ambulance / {police} police / {fire} fire engine. Use the chart toolbar to zoom, pan, and reset.", text_color=PALETTE["muted"], wraplength=1100, justify="left").pack(anchor="w", padx=14, pady=(0, 14))
    except Exception as exc:
        ctk.CTkLabel(host, text=f"Interactive charts unavailable: {exc}\nInstall matplotlib in the active rescue_env.", text_color=PALETTE["danger"]).pack(padx=20, pady=30)
