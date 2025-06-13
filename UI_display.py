import tkinter as tk
import json

class GolfUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Golf Simulator")
        self.label = tk.Label(root, text="Waiting for ball...", font=("Arial", 24))
        self.label.pack(pady=20)
        self.speed_label = tk.Label(root, text="Speed: N/A", font=("Arial", 18))
        self.speed_label.pack(pady=10)
        self.impact_label = tk.Label(root, text="Impact: N/A", font=("Arial", 18))
        self.impact_label.pack(pady=10)

    def update(self, data):
        if "detected" in data and data["detected"]:
            self.label.config(text="Hit the ball!")
        if "speed" in data and data["speed"]:
            self.speed_label.config(text=f"Speed: {data['speed']:.2f} m/s")
        if "impact_position" in data and data["impact_position"]:
            x, y = data["impact_position"]
            self.impact_label.config(text=f"Impact: ({x}, {y})")

if __name__ == "__main__":
    root = tk.Tk()
    app = GolfUI(root)
    test_data = {"detected": True, "speed": 20.5, "impact_position": (100, 200)}
    app.update(test_data)
    root.mainloop()