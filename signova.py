import random
import time
import tkinter as tk
from tkinter import ttk
import threading

try:
    import pyttsx3

    TTS_AVAILABLE = True
    engine = pyttsx3.init()
except Exception:
    TTS_AVAILABLE = False
    engine = None

GESTURES = {
    "Привет": {
        "left": [0.75, 0.25, 0.30, 0.35, 0.40, 0.10, 0.80, 0.35, 8, -4, 2],
        "right": [0.75, 0.25, 0.30, 0.35, 0.40, -0.10, 0.80, 0.35, -8, 4, -2],
    },
    "Спасибо": {
        "left": [0.65, 0.35, 0.45, 0.50, 0.55, 0.35, 0.55, 0.55, 15, 5, 3],
        "right": [0.65, 0.35, 0.45, 0.50, 0.55, -0.35, 0.55, 0.55, -15, -5, -3],
    },
    "Да": {
        "left": [0.30, 0.25, 0.30, 0.30, 0.30, 0.00, 0.95, 0.15, 2, 18, 1],
        "right": [0.30, 0.25, 0.30, 0.30, 0.30, 0.00, 0.95, 0.15, -2, 18, -1],
    },
    "Нет": {
        "left": [0.35, 0.30, 0.35, 0.35, 0.35, 0.60, 0.20, 0.70, 25, 0, 10],
        "right": [0.35, 0.30, 0.35, 0.35, 0.35, -0.60, 0.20, 0.70, -25, 0, -10],
    },
}


def simulate_sensor_frame(gesture_name):
    """Generate one noisy frame resembling readings from two gloves."""
    profile = GESTURES[gesture_name]
    frame = []

    for hand in ("left", "right"):
        values = profile[hand]

        noisy = []
        for i, value in enumerate(values):
            noise = random.gauss(0, 0.025 if i < 8 else 1.5)
            noisy.append(value + noise)
        frame.extend(noisy)

    return frame


def distance(a, b):
    """Simple normalized distance used as a demo classifier."""
    total = 0.0
    for i, (x, y) in enumerate(zip(a, b)):
        scale = 0.15 if i < 8 else 10.0
        total += ((x - y) / scale) ** 2
    return total**0.5


def classify(frame):
    """Compare current sensor frame with stored gesture profiles."""
    best_name = None
    best_score = float("inf")

    for name, profile in GESTURES.items():
        reference = profile["left"] + profile["right"]
        score = distance(frame, reference)
        if score < best_score:
            best_score = score
            best_name = name

    confidence = max(0.0, min(99.9, 100.0 * (1.0 - best_score / 12.0)))
    return best_name, confidence


def speak(text):
    if not TTS_AVAILABLE:
        return
    try:
        engine.say(text)
        engine.runAndWait()
    except Exception:
        pass


class SignovaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SIGNOVA — Sensor Glove Demo")
        self.root.geometry("900x600")
        self.root.minsize(760, 500)

        self.running = False
        self.current_gesture = tk.StringVar(value="Привет")
        self.detected = tk.StringVar(value="Ожидание...")
        self.confidence = tk.StringVar(value="—")
        self.status = tk.StringVar(value="DEMO: датчики симулируются")

        self.build_ui()

    def build_ui(self):
        root = self.root
        root.configure(bg="#10151b")

        title = tk.Label(
            root,
            text="SIGNOVA",
            font=("Segoe UI", 30, "bold"),
            fg="#f2f5f7",
            bg="#10151b",
        )
        title.pack(pady=(24, 2))

        subtitle = tk.Label(
            root,
            text="Wearable Sign Language Recognition System",
            font=("Segoe UI", 11),
            fg="#9da8b2",
            bg="#10151b",
        )
        subtitle.pack()

        main = tk.Frame(root, bg="#10151b")
        main.pack(fill="both", expand=True, padx=35, pady=25)

        left = tk.Frame(main, bg="#182028", bd=0)
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))

        right = tk.Frame(main, bg="#182028")
        right.pack(side="right", fill="both", expand=True, padx=(10, 0))

        tk.Label(
            left,
            text="SIMULATED GESTURE",
            font=("Segoe UI", 11, "bold"),
            fg="#9da8b2",
            bg="#182028",
        ).pack(pady=(25, 8))

        combo = ttk.Combobox(
            left,
            textvariable=self.current_gesture,
            values=list(GESTURES.keys()),
            state="readonly",
            font=("Segoe UI", 14),
        )
        combo.pack(pady=5, padx=30, fill="x")

        tk.Label(
            left,
            text="This simulates sensor readings\nfrom BOTH gloves.",
            font=("Segoe UI", 11),
            fg="#cbd2d8",
            bg="#182028",
            justify="center",
        ).pack(pady=25)

        self.start_btn = tk.Button(
            left,
            text="▶  START RECOGNITION",
            command=self.start,
            font=("Segoe UI", 12, "bold"),
            relief="flat",
            padx=15,
            pady=12,
        )
        self.start_btn.pack(pady=8, padx=30, fill="x")

        stop_btn = tk.Button(
            left,
            text="■  STOP",
            command=self.stop,
            font=("Segoe UI", 11),
            relief="flat",
            padx=15,
            pady=9,
        )
        stop_btn.pack(pady=5, padx=30, fill="x")

        tk.Label(
            right,
            text="RECOGNIZED GESTURE",
            font=("Segoe UI", 11, "bold"),
            fg="#9da8b2",
            bg="#182028",
        ).pack(pady=(25, 5))

        tk.Label(
            right,
            textvariable=self.detected,
            font=("Segoe UI", 34, "bold"),
            fg="#f2f5f7",
            bg="#182028",
        ).pack(pady=(20, 8))

        tk.Label(
            right,
            textvariable=self.confidence,
            font=("Segoe UI", 14),
            fg="#aeb8c0",
            bg="#182028",
        ).pack()

        self.progress = ttk.Progressbar(
            right, orient="horizontal", mode="determinate", maximum=100
        )
        self.progress.pack(fill="x", padx=35, pady=25)

        tk.Label(
            right,
            text="OUTPUT",
            font=("Segoe UI", 10, "bold"),
            fg="#9da8b2",
            bg="#182028",
        ).pack()

        self.output = tk.Label(
            right,
            text="Text: —\nVoice: —",
            font=("Segoe UI", 13),
            fg="#d9e0e5",
            bg="#182028",
            justify="left",
        )
        self.output.pack(pady=12)

        tk.Label(
            root,
            textvariable=self.status,
            font=("Segoe UI", 10),
            fg="#77838e",
            bg="#10151b",
        ).pack(pady=(0, 20))

    def start(self):
        if self.running:
            return
        self.running = True
        self.status.set("Receiving simulated data from LEFT + RIGHT ESP32...")
        threading.Thread(target=self.loop, daemon=True).start()

    def stop(self):
        self.running = False
        self.status.set("Stopped.")

    def loop(self):
        while self.running:
            target = self.current_gesture.get()
            frame = simulate_sensor_frame(target)
            name, conf = classify(frame)

            self.root.after(0, self.update_result, name, conf)
            time.sleep(0.7)

    def update_result(self, name, conf):
        self.detected.set(name.upper())
        self.confidence.set(f"Estimated confidence: {conf:.1f}%")
        self.progress["value"] = conf
        self.output.config(
            text=f"Text: {name}\nVoice: {'available' if TTS_AVAILABLE else 'install pyttsx3'}"
        )

        # Speak only when a new gesture is detected.
        if not hasattr(self, "_last_spoken") or self._last_spoken != name:
            self._last_spoken = name
            if TTS_AVAILABLE:
                threading.Thread(target=speak, args=(name,), daemon=True).start()


if __name__ == "__main__":
    root = tk.Tk()
    app = SignovaApp(root)
    root.mainloop()
