# ╔══════════════════════════════════════════════════════╗
# ║          Modern Dark Alarm Clock — by Vaibhav        ║
# ╚══════════════════════════════════════════════════════╝

import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import time
import threading
import winsound
import math

# ─────────────────── Colour Palette ───────────────────
BG         = "#0D0D0D"
SURFACE    = "#161616"
CARD       = "#1E1E2E"
ACCENT     = "#7C3AED"          # violet
ACCENT2    = "#A78BFA"
SUCCESS    = "#10B981"
WARNING    = "#F59E0B"
DANGER     = "#EF4444"
TEXT       = "#F1F5F9"
TEXT_DIM   = "#94A3B8"
BORDER     = "#2D2D44"


# ─────────────────── Helper ────────────────────────────
def hex_interpolate(c1: str, c2: str, t: float) -> str:
    """Linearly interpolate between two hex colours."""
    r1, g1, b1 = int(c1[1:3], 16), int(c1[3:5], 16), int(c1[5:7], 16)
    r2, g2, b2 = int(c2[1:3], 16), int(c2[3:5], 16), int(c2[5:7], 16)
    r = int(r1 + (r2 - r1) * t)
    g = int(g1 + (g2 - g1) * t)
    b = int(b1 + (b2 - b1) * t)
    return f"#{r:02x}{g:02x}{b:02x}"


class ModernAlarmClock:
    def __init__(self, root: tk.Tk):
        self.root = root
        # State — must come before _build_ui
        self.alarms: list[dict] = []
        self._alarm_thread: threading.Thread | None = None
        self._running = True
        self._ring_anim_id: str | None = None
        self._pulse_phase = 0.0

        self._setup_window()
        self._build_ui()

        # Start live clock loop
        self._tick()

    # ── Window ────────────────────────────────────────────
    def _setup_window(self):
        self.root.title("Alarm Clock")
        self.root.geometry("520x680")
        self.root.minsize(480, 620)
        self.root.configure(bg=BG)
        self.root.resizable(True, True)

        # Centre on screen
        self.root.update_idletasks()
        w, h = 520, 680
        x = (self.root.winfo_screenwidth()  - w) // 2
        y = (self.root.winfo_screenheight() - h) // 2
        self.root.geometry(f"{w}x{h}+{x}+{y}")

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    # ── UI ────────────────────────────────────────────────
    def _build_ui(self):
        # ── Header bar ──
        header = tk.Frame(self.root, bg=SURFACE, height=56)
        header.pack(fill=tk.X, side=tk.TOP)
        header.pack_propagate(False)

        tk.Label(
            header, text="⏰  Alarm Clock",
            font=("Segoe UI", 16, "bold"),
            bg=SURFACE, fg=TEXT
        ).pack(side=tk.LEFT, padx=20, pady=10)

        self.status_dot = tk.Label(header, text="●", font=("Segoe UI", 12),
                                   bg=SURFACE, fg=TEXT_DIM)
        self.status_dot.pack(side=tk.RIGHT, padx=20)

        self.status_lbl = tk.Label(header, text="No alarm set",
                                   font=("Segoe UI", 9),
                                   bg=SURFACE, fg=TEXT_DIM)
        self.status_lbl.pack(side=tk.RIGHT, padx=4)

        # ── Clock canvas ──
        clock_frame = tk.Frame(self.root, bg=BG, pady=10)
        clock_frame.pack(fill=tk.X)

        self.clock_canvas = tk.Canvas(
            clock_frame, width=260, height=260,
            bg=BG, highlightthickness=0
        )
        self.clock_canvas.pack(anchor=tk.CENTER)
        self._draw_clock_face()

        # ── Digital time ──
        self.digital_var = tk.StringVar(value="--:--:--")
        self.digital_lbl = tk.Label(
            self.root, textvariable=self.digital_var,
            font=("Segoe UI", 36, "bold"),
            bg=BG, fg=TEXT
        )
        self.digital_lbl.pack(pady=(0, 4))

        self.date_var = tk.StringVar(value="")
        tk.Label(self.root, textvariable=self.date_var,
                 font=("Segoe UI", 11), bg=BG, fg=TEXT_DIM).pack(pady=(0, 12))

        # ── Separator ──
        ttk.Separator(self.root, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=24)

        # ── Set alarm card ──
        card = tk.Frame(self.root, bg=CARD, padx=20, pady=16)
        card.pack(fill=tk.X, padx=24, pady=16)
        self._build_set_alarm(card)

        # ── Alarm list ──
        list_frame = tk.Frame(self.root, bg=BG, padx=24)
        list_frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(list_frame, text="SCHEDULED ALARMS",
                 font=("Segoe UI", 8, "bold"),
                 bg=BG, fg=TEXT_DIM).pack(anchor=tk.W, pady=(0, 6))

        # Scrollable list area
        scroll_canvas = tk.Canvas(list_frame, bg=BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL,
                                  command=scroll_canvas.yview)
        self.alarm_list_frame = tk.Frame(scroll_canvas, bg=BG)
        self.alarm_list_frame.bind(
            "<Configure>",
            lambda e: scroll_canvas.configure(
                scrollregion=scroll_canvas.bbox("all"))
        )
        scroll_canvas.create_window((0, 0), window=self.alarm_list_frame,
                                    anchor=tk.NW)
        scroll_canvas.configure(yscrollcommand=scrollbar.set)
        scroll_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self._update_alarm_list()

    def _build_set_alarm(self, parent: tk.Frame):
        tk.Label(parent, text="Set New Alarm",
                 font=("Segoe UI", 12, "bold"),
                 bg=CARD, fg=TEXT).pack(anchor=tk.W)
        tk.Label(parent, text="Choose hour, minute and second",
                 font=("Segoe UI", 9), bg=CARD, fg=TEXT_DIM).pack(anchor=tk.W, pady=(2, 10))

        picker_row = tk.Frame(parent, bg=CARD)
        picker_row.pack(fill=tk.X)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Dark.TSpinbox",
                         fieldbackground=SURFACE, background=SURFACE,
                         foreground=TEXT, bordercolor=BORDER,
                         arrowcolor=ACCENT2, insertcolor=TEXT,
                         relief="flat", padding=4)
        style.configure("Dark.TCombobox",
                         fieldbackground=SURFACE, background=SURFACE,
                         foreground=TEXT, bordercolor=BORDER,
                         arrowcolor=ACCENT2, selectbackground=ACCENT,
                         selectforeground=TEXT)

        # Hour spinner
        self._add_spinner(picker_row, "HH", 0, 23, "hour")
        tk.Label(picker_row, text=":", font=("Segoe UI", 22, "bold"),
                 bg=CARD, fg=ACCENT2).pack(side=tk.LEFT, padx=2)
        self._add_spinner(picker_row, "MM", 0, 59, "minute")
        tk.Label(picker_row, text=":", font=("Segoe UI", 22, "bold"),
                 bg=CARD, fg=ACCENT2).pack(side=tk.LEFT, padx=2)
        self._add_spinner(picker_row, "SS", 0, 59, "second")

        # Label entry
        label_row = tk.Frame(parent, bg=CARD)
        label_row.pack(fill=tk.X, pady=(10, 0))
        tk.Label(label_row, text="Label (optional)",
                 font=("Segoe UI", 9), bg=CARD, fg=TEXT_DIM).pack(anchor=tk.W)
        self.alarm_label_var = tk.StringVar(value="")
        label_entry = tk.Entry(label_row, textvariable=self.alarm_label_var,
                               font=("Segoe UI", 11),
                               bg=SURFACE, fg=TEXT, insertbackground=TEXT,
                               relief="flat", bd=0)
        label_entry.pack(fill=tk.X, ipady=6, pady=(4, 0))
        tk.Frame(label_row, bg=BORDER, height=1).pack(fill=tk.X)

        # Set alarm button
        btn = tk.Button(parent, text="＋  Add Alarm",
                        font=("Segoe UI", 11, "bold"),
                        bg=ACCENT, fg=TEXT, relief="flat",
                        activebackground=ACCENT2, activeforeground=TEXT,
                        cursor="hand2", padx=16, pady=8,
                        command=self._add_alarm)
        btn.pack(fill=tk.X, pady=(14, 0))
        self._bind_hover(btn, ACCENT, ACCENT2)

    def _add_spinner(self, parent, placeholder, from_, to, attr):
        frame = tk.Frame(parent, bg=SURFACE, padx=4, pady=4)
        frame.pack(side=tk.LEFT, padx=4)
        var = tk.StringVar(value=f"{from_:02d}")
        setattr(self, f"{attr}_var", var)
        spin = tk.Spinbox(frame, from_=from_, to=to, textvariable=var,
                          width=3,
                          font=("Segoe UI", 22, "bold"),
                          bg=SURFACE, fg=TEXT,
                          buttonbackground=SURFACE,
                          insertbackground=TEXT,
                          relief="flat",
                          justify=tk.CENTER,
                          format="%02.0f",
                          wrap=True)
        spin.pack()

    # ── Clock face ────────────────────────────────────────
    def _draw_clock_face(self):
        cx, cy, r = 130, 130, 115
        # Outer glow rings
        for i, alpha in enumerate([0.06, 0.12, 0.22]):
            rr = r + 14 - i * 5
            col = hex_interpolate(BG, ACCENT, alpha)
            self.clock_canvas.create_oval(
                cx - rr, cy - rr, cx + rr, cy + rr,
                outline=col, width=2
            )
        # Face
        self.clock_canvas.create_oval(
            cx - r, cy - r, cx + r, cy + r,
            fill=CARD, outline=BORDER, width=2
        )
        # Hour ticks
        for i in range(60):
            angle = math.radians(i * 6 - 90)
            if i % 5 == 0:
                r1, r2, w, col = r - 14, r - 4, 2, TEXT
            else:
                r1, r2, w, col = r - 8, r - 4, 1, TEXT_DIM
            x1 = cx + r1 * math.cos(angle)
            y1 = cy + r1 * math.sin(angle)
            x2 = cx + r2 * math.cos(angle)
            y2 = cy + r2 * math.sin(angle)
            self.clock_canvas.create_line(x1, y1, x2, y2,
                                          fill=col, width=w)
        # Centre dot
        self.clock_canvas.create_oval(cx - 5, cy - 5, cx + 5, cy + 5,
                                      fill=ACCENT, outline="")

        # Hands – stored as tags for fast redraw
        self.clock_canvas.create_line(cx, cy, cx, cy, fill=TEXT_DIM,
                                      width=4, capstyle=tk.ROUND,
                                      tags="hour_hand")
        self.clock_canvas.create_line(cx, cy, cx, cy, fill=TEXT,
                                      width=2, capstyle=tk.ROUND,
                                      tags="min_hand")
        self.clock_canvas.create_line(cx, cy, cx, cy, fill=ACCENT,
                                      width=1, capstyle=tk.ROUND,
                                      tags="sec_hand")

    def _update_clock_hands(self, h, m, s):
        cx, cy, r = 130, 130, 115
        def hand(tag, angle_deg, length, width, color):
            a = math.radians(angle_deg - 90)
            x = cx + length * math.cos(a)
            y = cy + length * math.sin(a)
            self.clock_canvas.coords(tag, cx, cy, x, y)
            self.clock_canvas.itemconfig(tag, fill=color, width=width)

        # Smooth second hand
        sec_angle  = (s / 60) * 360
        min_angle  = (m / 60) * 360 + (s / 60) * 6
        hour_angle = ((h % 12) / 12) * 360 + (m / 60) * 30

        hand("sec_hand",  sec_angle,  r - 18, 1, ACCENT)
        hand("min_hand",  min_angle,  r - 22, 2, TEXT)
        hand("hour_hand", hour_angle, r - 44, 4, TEXT_DIM)

        # Centre dot on top
        self.clock_canvas.tag_raise("hour_hand")
        self.clock_canvas.tag_raise("min_hand")
        self.clock_canvas.tag_raise("sec_hand")

    # ── Live tick ─────────────────────────────────────────
    def _tick(self):
        if not self._running:
            return
        now = datetime.datetime.now()
        h, m, s = now.hour, now.minute, now.second

        self.digital_var.set(now.strftime("%H:%M:%S"))
        self.date_var.set(now.strftime("%A, %d %B %Y"))
        self._update_clock_hands(h, m, s)

        # Pulse status dot
        self._pulse_phase = (self._pulse_phase + 0.08) % (2 * math.pi)
        brightness = 0.55 + 0.45 * math.sin(self._pulse_phase)
        dot_col = hex_interpolate(TEXT_DIM, SUCCESS, brightness) \
                  if self.alarms else TEXT_DIM
        self.status_dot.config(fg=dot_col)

        self.root.after(200, self._tick)   # 200 ms = smooth + light

    # ── Alarm management ──────────────────────────────────
    def _add_alarm(self):
        try:
            h = int(self.hour_var.get())
            m = int(self.minute_var.get())
            s = int(self.second_var.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numbers.")
            return

        if not (0 <= h <= 23 and 0 <= m <= 59 and 0 <= s <= 59):
            messagebox.showerror("Invalid Time",
                                 "Hour: 0-23, Minute/Second: 0-59")
            return

        time_str  = f"{h:02d}:{m:02d}:{s:02d}"
        label_str = self.alarm_label_var.get().strip() or time_str

        alarm = {"time": time_str, "label": label_str,
                 "active": True, "id": id(object())}
        self.alarms.append(alarm)
        self.alarm_label_var.set("")
        self._update_alarm_list()
        self._update_status()
        self._ensure_alarm_thread()

    def _remove_alarm(self, alarm_id):
        self.alarms = [a for a in self.alarms if a["id"] != alarm_id]
        self._update_alarm_list()
        self._update_status()

    def _toggle_alarm(self, alarm_id):
        for a in self.alarms:
            if a["id"] == alarm_id:
                a["active"] = not a["active"]
        self._update_alarm_list()
        self._update_status()

    def _update_alarm_list(self):
        for w in self.alarm_list_frame.winfo_children():
            w.destroy()

        if not self.alarms:
            tk.Label(self.alarm_list_frame,
                     text="No alarms scheduled yet.",
                     font=("Segoe UI", 10), bg=BG, fg=TEXT_DIM
                     ).pack(pady=10)
            return

        for alarm in self.alarms:
            self._build_alarm_row(alarm)

    def _build_alarm_row(self, alarm: dict):
        row = tk.Frame(self.alarm_list_frame, bg=CARD, padx=12, pady=10)
        row.pack(fill=tk.X, pady=4)

        # Colour indicator
        ind_col = SUCCESS if alarm["active"] else TEXT_DIM
        ind = tk.Label(row, text="●", font=("Segoe UI", 10),
                       bg=CARD, fg=ind_col)
        ind.pack(side=tk.LEFT, padx=(0, 8))

        # Info
        info = tk.Frame(row, bg=CARD)
        info.pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Label(info, text=alarm["time"],
                 font=("Segoe UI", 14, "bold"),
                 bg=CARD, fg=TEXT).pack(anchor=tk.W)
        tk.Label(info, text=alarm["label"],
                 font=("Segoe UI", 9), bg=CARD, fg=TEXT_DIM).pack(anchor=tk.W)

        # Buttons
        btn_frame = tk.Frame(row, bg=CARD)
        btn_frame.pack(side=tk.RIGHT)

        toggle_col = SUCCESS if alarm["active"] else TEXT_DIM
        toggle_txt = "ON" if alarm["active"] else "OFF"
        t_btn = tk.Button(btn_frame, text=toggle_txt,
                          font=("Segoe UI", 8, "bold"),
                          bg=toggle_col, fg=BG, relief="flat",
                          padx=8, pady=3, cursor="hand2",
                          command=lambda aid=alarm["id"]: self._toggle_alarm(aid))
        t_btn.pack(side=tk.LEFT, padx=(0, 6))

        d_btn = tk.Button(btn_frame, text="✕",
                          font=("Segoe UI", 10),
                          bg=DANGER, fg=TEXT, relief="flat",
                          padx=8, pady=3, cursor="hand2",
                          command=lambda aid=alarm["id"]: self._remove_alarm(aid))
        d_btn.pack(side=tk.LEFT)

    def _update_status(self):
        active = [a for a in self.alarms if a["active"]]
        if not active:
            self.status_lbl.config(text="No alarm set")
        elif len(active) == 1:
            self.status_lbl.config(text=f"Alarm at {active[0]['time']}")
        else:
            self.status_lbl.config(text=f"{len(active)} alarms active")

    # ── Alarm thread ──────────────────────────────────────
    def _ensure_alarm_thread(self):
        if self._alarm_thread and self._alarm_thread.is_alive():
            return
        self._alarm_thread = threading.Thread(
            target=self._alarm_loop, daemon=True)
        self._alarm_thread.start()

    def _alarm_loop(self):
        triggered: set = set()
        while self._running and self.alarms:
            now_str = datetime.datetime.now().strftime("%H:%M:%S")
            for alarm in list(self.alarms):
                if (alarm["active"] and
                        alarm["time"] == now_str and
                        alarm["id"] not in triggered):
                    triggered.add(alarm["id"])
                    self.root.after(0, self._trigger_alarm, alarm)
            time.sleep(0.5)

    def _trigger_alarm(self, alarm: dict):
        self._ring_animation(3)
        try:
            winsound.PlaySound("sound.wav", winsound.SND_ASYNC | winsound.SND_NOSTOP)
        except Exception:
            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
        messagebox.showinfo(
            "⏰  Alarm!",
            f"Time to wake up!\n\n{alarm['label']}  —  {alarm['time']}"
        )

    def _ring_animation(self, flashes: int):
        """Flash the digital clock label for visual feedback."""
        def toggle(n, on):
            if n <= 0:
                self.digital_lbl.config(fg=TEXT)
                return
            col = ACCENT if on else DANGER
            self.digital_lbl.config(fg=col)
            self.root.after(250, toggle, n - (1 if not on else 0), not on)
        toggle(flashes * 2, True)

    # ── Utilities ─────────────────────────────────────────
    def _bind_hover(self, widget, normal, hover):
        widget.bind("<Enter>", lambda e: widget.config(bg=hover))
        widget.bind("<Leave>", lambda e: widget.config(bg=normal))

    def _on_close(self):
        self._running = False
        self.root.destroy()


# ─────────────────── Entry ─────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    app = ModernAlarmClock(root)
    root.mainloop()