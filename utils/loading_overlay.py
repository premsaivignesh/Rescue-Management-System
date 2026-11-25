"""Short branded loading overlay for manual refresh actions in the desktop UI."""
import customtkinter as ctk

FRAMES = ("🚑   ◌", "🚑   ◔", "🚑   ◑", "🚑   ◕", "🚑   ●", "🚑   ◕", "🚑   ◑", "🚑   ◔")


def run_loading(parent, callback, duration_ms=3000):
    """Show a centered rescue-themed spinner for three seconds, then refresh."""
    overlay = ctk.CTkToplevel(parent)
    overlay.title("Refreshing")
    overlay.configure(fg_color="#10130D")
    overlay.transient(parent)
    overlay.resizable(False, False)
    width, height = 360, 220
    overlay.update_idletasks()
    x = parent.winfo_rootx() + max(0, (parent.winfo_width() - width) // 2)
    y = parent.winfo_rooty() + max(0, (parent.winfo_height() - height) // 2)
    overlay.geometry(f"{width}x{height}+{x}+{y}")
    try:
        overlay.grab_set()
    except Exception:
        pass
    card = ctk.CTkFrame(overlay, fg_color="#1B2117", corner_radius=18,
                        border_width=1, border_color="#68783B")
    card.pack(fill="both", expand=True, padx=12, pady=12)
    icon = ctk.CTkLabel(card, text=FRAMES[0], font=("Segoe UI Emoji", 36), text_color="#DDE8C5")
    icon.pack(pady=(22, 4))
    ctk.CTkLabel(card, text="Refreshing rescue operations", font=("Segoe UI", 15, "bold"),
                 text_color="#DDE8C5").pack(pady=2)
    ctk.CTkLabel(card, text="Updating incidents and notifications…", font=("Segoe UI", 11),
                 text_color="#AAB69A").pack(pady=(0, 14))
    state = {"frame": 0, "elapsed": 0}
    def animate():
        if not overlay.winfo_exists():
            return
        state["frame"] = (state["frame"] + 1) % len(FRAMES)
        state["elapsed"] += 120
        icon.configure(text=FRAMES[state["frame"]])
        if state["elapsed"] < duration_ms:
            overlay.after(120, animate)
        else:
            try:
                overlay.grab_release()
                overlay.destroy()
            except Exception:
                pass
            callback()
    overlay.after(120, animate)
