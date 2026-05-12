import math
import random
import time
import tkinter as tk
from collections import deque
from tkinter import ttk


class ECGDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("ECG Signal Command Center")
        self.root.geometry("1180x720")
        self.root.minsize(980, 620)
        self.root.configure(bg="#07111f")

        self.running = True
        self.sample_index = 0
        self.bpm = 74
        self.oxygen = 98
        self.signal_quality = 94
        self.gain = tk.DoubleVar(value=1.0)
        self.speed = tk.DoubleVar(value=1.0)
        self.lead = tk.StringVar(value="Lead II")
        self.rhythm = tk.StringVar(value="Normal Sinus Rhythm")
        self.samples = deque([0.0] * 650, maxlen=650)

        self.colors = {
            "bg": "#07111f",
            "panel": "#0d1b2f",
            "panel_2": "#10243d",
            "line": "#29ff87",
            "line_glow": "#156f4a",
            "muted": "#7f93ad",
            "text": "#e8f1ff",
            "accent": "#38bdf8",
            "warning": "#fbbf24",
            "danger": "#fb7185",
        }

        self._configure_styles()
        self._build_layout()
        self._tick()

    def _configure_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "TCombobox",
            fieldbackground=self.colors["panel_2"],
            background=self.colors["panel_2"],
            foreground=self.colors["text"],
            arrowcolor=self.colors["accent"],
            bordercolor=self.colors["panel_2"],
        )
        style.map("TCombobox", fieldbackground=[("readonly", self.colors["panel_2"])])

    def _build_layout(self):
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)

        header = tk.Frame(self.root, bg=self.colors["bg"], padx=24, pady=18)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(0, weight=1)

        tk.Label(
            header,
            text="ECG SIGNAL COMMAND CENTER",
            bg=self.colors["bg"],
            fg=self.colors["text"],
            font=("Segoe UI", 24, "bold"),
        ).grid(row=0, column=0, sticky="w")
        tk.Label(
            header,
            text="Live waveform simulation • cardiac telemetry • rhythm monitoring",
            bg=self.colors["bg"],
            fg=self.colors["muted"],
            font=("Segoe UI", 11),
        ).grid(row=1, column=0, sticky="w", pady=(4, 0))

        status = tk.Frame(header, bg="#09251d", padx=16, pady=8, highlightthickness=1, highlightbackground="#14532d")
        status.grid(row=0, column=1, rowspan=2, sticky="e")
        self.status_dot = tk.Canvas(status, width=12, height=12, bg="#09251d", highlightthickness=0)
        self.status_dot.grid(row=0, column=0, padx=(0, 8))
        self.status_dot.create_oval(2, 2, 10, 10, fill=self.colors["line"], outline="")
        self.status_label = tk.Label(
            status,
            text="MONITORING",
            bg="#09251d",
            fg=self.colors["line"],
            font=("Segoe UI", 10, "bold"),
        )
        self.status_label.grid(row=0, column=1)

        body = tk.Frame(self.root, bg=self.colors["bg"], padx=24, pady=24)
        body.grid(row=1, column=0, sticky="nsew")
        body.grid_columnconfigure(0, weight=1)
        body.grid_columnconfigure(1, weight=0)
        body.grid_rowconfigure(0, weight=1)

        waveform_panel = self._panel(body)
        waveform_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 18))
        waveform_panel.grid_columnconfigure(0, weight=1)
        waveform_panel.grid_rowconfigure(1, weight=1)

        wave_head = tk.Frame(waveform_panel, bg=self.colors["panel"], padx=18, pady=16)
        wave_head.grid(row=0, column=0, sticky="ew")
        wave_head.grid_columnconfigure(0, weight=1)
        self.lead_label = tk.Label(
            wave_head,
            text="Lead II • 25 mm/s • 10 mm/mV",
            bg=self.colors["panel"],
            fg=self.colors["text"],
            font=("Segoe UI", 15, "bold"),
        )
        self.lead_label.grid(row=0, column=0, sticky="w")
        self.clock_label = tk.Label(
            wave_head,
            text="--:--:--",
            bg=self.colors["panel"],
            fg=self.colors["muted"],
            font=("Consolas", 13),
        )
        self.clock_label.grid(row=0, column=1, sticky="e")

        self.canvas = tk.Canvas(waveform_panel, bg="#06101c", highlightthickness=0)
        self.canvas.grid(row=1, column=0, sticky="nsew", padx=18, pady=(0, 18))
        self.canvas.bind("<Configure>", lambda _event: self._draw_waveform())

        sidebar = tk.Frame(body, bg=self.colors["bg"], width=320)
        sidebar.grid(row=0, column=1, sticky="ns")
        sidebar.grid_propagate(False)

        self.metric_cards = {}
        self._metric_card(sidebar, "HEART RATE", "bpm", "bpm", self.colors["line"]).pack(fill="x", pady=(0, 14))
        self._metric_card(sidebar, "SPO2", "oxygen", "%", self.colors["accent"]).pack(fill="x", pady=(0, 14))
        self._metric_card(sidebar, "SIGNAL QUALITY", "quality", "%", self.colors["warning"]).pack(fill="x", pady=(0, 14))

        controls = self._panel(sidebar, padx=18, pady=18)
        controls.pack(fill="x", pady=(4, 0))
        tk.Label(
            controls,
            text="Controls",
            bg=self.colors["panel"],
            fg=self.colors["text"],
            font=("Segoe UI", 15, "bold"),
        ).pack(anchor="w")
        self._control_label(controls, "Lead").pack(anchor="w", pady=(16, 6))
        lead_box = ttk.Combobox(
            controls,
            textvariable=self.lead,
            values=("Lead I", "Lead II", "Lead III", "aVR", "aVL", "aVF", "V1", "V2", "V3", "V4", "V5", "V6"),
            state="readonly",
        )
        lead_box.pack(fill="x")
        lead_box.bind("<<ComboboxSelected>>", lambda _event: self._update_labels())

        self._control_label(controls, "Gain").pack(anchor="w", pady=(18, 6))
        self._slider(controls, self.gain, 0.5, 1.8).pack(fill="x")

        self._control_label(controls, "Sweep Speed").pack(anchor="w", pady=(18, 6))
        self._slider(controls, self.speed, 0.6, 1.8).pack(fill="x")

        button_row = tk.Frame(controls, bg=self.colors["panel"])
        button_row.pack(fill="x", pady=(20, 0))
        self.pause_button = tk.Button(
            button_row,
            text="Pause",
            command=self._toggle_running,
            bg=self.colors["accent"],
            fg="#04111f",
            activebackground="#7dd3fc",
            activeforeground="#04111f",
            relief="flat",
            padx=16,
            pady=10,
            font=("Segoe UI", 10, "bold"),
        )
        self.pause_button.pack(side="left", fill="x", expand=True, padx=(0, 8))
        tk.Button(
            button_row,
            text="Reset",
            command=self._reset,
            bg=self.colors["panel_2"],
            fg=self.colors["text"],
            activebackground="#1e3a5f",
            activeforeground=self.colors["text"],
            relief="flat",
            padx=16,
            pady=10,
            font=("Segoe UI", 10, "bold"),
        ).pack(side="left", fill="x", expand=True)

        rhythm_panel = self._panel(sidebar, padx=18, pady=18)
        rhythm_panel.pack(fill="both", expand=True, pady=(14, 0))
        tk.Label(
            rhythm_panel,
            text="AI Rhythm Readout",
            bg=self.colors["panel"],
            fg=self.colors["text"],
            font=("Segoe UI", 15, "bold"),
        ).pack(anchor="w")
        tk.Label(
            rhythm_panel,
            textvariable=self.rhythm,
            bg=self.colors["panel"],
            fg=self.colors["line"],
            wraplength=260,
            justify="left",
            font=("Segoe UI", 18, "bold"),
        ).pack(anchor="w", pady=(16, 8))
        tk.Label(
            rhythm_panel,
            text="Synthetic demo signal. Not for clinical diagnosis.",
            bg=self.colors["panel"],
            fg=self.colors["muted"],
            wraplength=260,
            justify="left",
            font=("Segoe UI", 10),
        ).pack(anchor="w")

    def _panel(self, parent, padx=0, pady=0):
        return tk.Frame(
            parent,
            bg=self.colors["panel"],
            padx=padx,
            pady=pady,
            highlightthickness=1,
            highlightbackground="#1f3556",
        )

    def _metric_card(self, parent, title, key, unit, color):
        card = self._panel(parent, padx=18, pady=16)
        tk.Label(card, text=title, bg=self.colors["panel"], fg=self.colors["muted"], font=("Segoe UI", 10, "bold")).pack(anchor="w")
        row = tk.Frame(card, bg=self.colors["panel"])
        row.pack(fill="x", pady=(8, 0))
        value = tk.Label(row, text="--", bg=self.colors["panel"], fg=color, font=("Segoe UI", 35, "bold"))
        value.pack(side="left")
        tk.Label(row, text=unit, bg=self.colors["panel"], fg=self.colors["muted"], font=("Segoe UI", 13, "bold")).pack(side="left", padx=(8, 0), pady=(18, 0))
        self.metric_cards[key] = value
        return card

    def _control_label(self, parent, text):
        return tk.Label(parent, text=text, bg=self.colors["panel"], fg=self.colors["muted"], font=("Segoe UI", 10, "bold"))

    def _slider(self, parent, variable, start, end):
        return tk.Scale(
            parent,
            from_=start,
            to=end,
            resolution=0.05,
            orient="horizontal",
            variable=variable,
            showvalue=False,
            bg=self.colors["panel"],
            fg=self.colors["text"],
            troughcolor="#07111f",
            activebackground=self.colors["accent"],
            highlightthickness=0,
            relief="flat",
        )

    def _synthetic_ecg(self, t):
        beat = t % 1.0
        baseline = 0.035 * math.sin(2 * math.pi * t * 0.33)
        p_wave = 0.13 * math.exp(-((beat - 0.18) / 0.035) ** 2)
        q_wave = -0.22 * math.exp(-((beat - 0.36) / 0.012) ** 2)
        r_wave = 1.18 * math.exp(-((beat - 0.39) / 0.010) ** 2)
        s_wave = -0.38 * math.exp(-((beat - 0.425) / 0.015) ** 2)
        t_wave = 0.34 * math.exp(-((beat - 0.66) / 0.075) ** 2)
        noise = random.uniform(-0.018, 0.018)
        return baseline + p_wave + q_wave + r_wave + s_wave + t_wave + noise

    def _tick(self):
        if self.running:
            for _ in range(max(2, int(5 * self.speed.get()))):
                t = self.sample_index / 92.0
                self.samples.append(self._synthetic_ecg(t))
                self.sample_index += 1

            drift = math.sin(time.time() * 0.9)
            self.bpm = int(74 + drift * 5 + random.uniform(-1.8, 1.8))
            self.oxygen = max(95, min(100, int(98 + math.sin(time.time() * 0.35) * 1.3)))
            self.signal_quality = max(88, min(99, int(94 + math.sin(time.time() * 0.55) * 4 + random.uniform(-1, 1))))
            self._update_labels()
            self._draw_waveform()

        self.root.after(32, self._tick)

    def _update_labels(self):
        self.metric_cards["bpm"].configure(text=str(self.bpm))
        self.metric_cards["oxygen"].configure(text=str(self.oxygen))
        self.metric_cards["quality"].configure(text=str(self.signal_quality))
        self.lead_label.configure(text=f"{self.lead.get()} • 25 mm/s • {self.gain.get():.2f}x gain")
        self.clock_label.configure(text=time.strftime("%H:%M:%S"))

        if self.bpm > 100:
            self.rhythm.set("Sinus Tachycardia Watch")
        elif self.bpm < 60:
            self.rhythm.set("Sinus Bradycardia Watch")
        elif self.signal_quality < 90:
            self.rhythm.set("Signal Noise Detected")
        else:
            self.rhythm.set("Normal Sinus Rhythm")

    def _draw_grid(self, width, height):
        small = 18
        large = small * 5
        for x in range(0, width, small):
            color = "#10233a" if x % large else "#1f3f5f"
            self.canvas.create_line(x, 0, x, height, fill=color)
        for y in range(0, height, small):
            color = "#10233a" if y % large else "#1f3f5f"
            self.canvas.create_line(0, y, width, y, fill=color)

    def _draw_waveform(self):
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        if width < 20 or height < 20:
            return

        self.canvas.delete("all")
        self._draw_grid(width, height)

        center = height * 0.52
        amplitude = height * 0.24 * self.gain.get()
        values = list(self.samples)
        step = width / max(1, len(values) - 1)
        points = []
        for index, value in enumerate(values):
            points.extend((index * step, center - value * amplitude))

        if len(points) >= 4:
            self.canvas.create_line(points, fill=self.colors["line_glow"], width=8, smooth=True, splinesteps=18)
            self.canvas.create_line(points, fill=self.colors["line"], width=3, smooth=True, splinesteps=18)

        scan_x = (self.sample_index * 5) % max(width, 1)
        self.canvas.create_line(scan_x, 0, scan_x, height, fill="#d9fff0", width=2)
        self.canvas.create_text(16, 18, text="LIVE", fill=self.colors["line"], anchor="w", font=("Segoe UI", 11, "bold"))

    def _toggle_running(self):
        self.running = not self.running
        self.pause_button.configure(text="Pause" if self.running else "Resume")
        state = "MONITORING" if self.running else "PAUSED"
        color = self.colors["line"] if self.running else self.colors["warning"]
        self.status_label.configure(text=state, fg=color)
        self.status_dot.delete("all")
        self.status_dot.create_oval(2, 2, 10, 10, fill=color, outline="")

    def _reset(self):
        self.sample_index = 0
        self.samples = deque([0.0] * 650, maxlen=650)
        self._draw_waveform()


if __name__ == "__main__":
    app_root = tk.Tk()
    ECGDashboard(app_root)
    app_root.mainloop()
