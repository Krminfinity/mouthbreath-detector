import cv2
import mediapipe as mp
import numpy as np
import threading
import time
from win10toast import ToastNotifier
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# --- 設定値 ---
MAR_THRESHOLD_HIGH = 0.002
MAR_THRESHOLD_LOW = 0.001
NOTIFY_DURATION = 1   # 口開き連続秒数（1秒以上で通知）
COOLDOWN_SEC = 300   # 通知クールダウン
FRAME_RATE = 10      # fps

# --- 状態管理 ---
class StateMachine:
    def __init__(self):
        self.state = 'unknown'
        self.prev_state = 'unknown'
    def update(self, mar, now):
        self.prev_state = self.state
        if mar >= MAR_THRESHOLD_HIGH:
            self.state = 'mouth'
        elif mar <= MAR_THRESHOLD_LOW:
            self.state = 'nasal'
        else:
            self.state = 'unknown'
        return self.state
    def should_notify(self, now):
        # mouth判定に遷移した瞬間に通知
        return self.state == 'mouth' and self.prev_state != 'mouth'

# --- MAR算出 ---
mp_face = mp.solutions.face_mesh
UPPER_LIP_IDX = 13
LOWER_LIP_IDX = 14
FACE_TOP = 10
FACE_BOTTOM = 152

def calc_mar(landmarks, image_shape):
    h, w = image_shape[:2]
    upper = landmarks[UPPER_LIP_IDX]
    lower = landmarks[LOWER_LIP_IDX]
    mar = abs((lower.y - upper.y) * h)
    face_height = abs((landmarks[FACE_TOP].y - landmarks[FACE_BOTTOM].y) * h)
    return mar / face_height if face_height > 0 else 0

# --- 通知 ---
toaster = ToastNotifier()
_last_notify_time = 0
def notify_mouth():
    global _last_notify_time
    now = time.time()
    if now - _last_notify_time >= 1:
        toaster.show_toast("口呼吸検出", "口が開きました", duration=3, threaded=True)
        _last_notify_time = now

# --- UI ---
class AppUI:
    def __init__(self, root):
        self.root = root
        self.root.title("MouthBreath Monitor")
        self.status_var = tk.StringVar(value="状態: unknown")
        self.mar_var = tk.StringVar(value="MAR: 0.000")
        self.time_var = tk.StringVar(value="口開き累積: 0秒")
        self.create_widgets()
        self.mouth_time = 0
        self.history = []
        self.update_chart()
    def create_widgets(self):
        ttk.Label(self.root, textvariable=self.status_var, font=("Meiryo", 16)).pack(pady=5)
        ttk.Label(self.root, textvariable=self.mar_var, font=("Meiryo", 14)).pack(pady=5)
        ttk.Label(self.root, textvariable=self.time_var, font=("Meiryo", 12)).pack(pady=5)
        self.fig, self.ax = plt.subplots(figsize=(4,2))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack()
    def update_status(self, state, mar):
        self.status_var.set(f"状態: {state}")
        self.mar_var.set(f"MAR: {mar:.3f}")
        if state == 'mouth':
            self.mouth_time += 1/FRAME_RATE
        self.time_var.set(f"口開き累積: {int(self.mouth_time)}秒")
        self.history.append((time.time(), mar, state))
        if len(self.history) > 300:
            self.history = self.history[-300:]
        self.update_chart()
    def update_chart(self):
        times = [h[0] for h in self.history]
        mars = [h[1] for h in self.history]
        self.ax.clear()
        self.ax.plot(mars, label="MAR")
        self.ax.set_ylim(0,1)
        self.ax.set_ylabel("MAR")
        self.ax.legend()
        self.canvas.draw()

# --- メイン処理 ---
def main_loop(ui, show_camera=True):
    cap = cv2.VideoCapture(0)
    state_machine = StateMachine()
    with mp_face.FaceMesh(static_image_mode=False, max_num_faces=1, refine_landmarks=True) as face_mesh:
        while True:
            ret, frame = cap.read()
            if not ret:
                continue
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = face_mesh.process(rgb)
            mar = 0
            state = 'unknown'
            now = time.time()
            if results.multi_face_landmarks:
                for face_landmarks in results.multi_face_landmarks:
                    lm = face_landmarks.landmark
                    mar = calc_mar(lm, frame.shape)
                    state = state_machine.update(mar, now)
                    if state_machine.should_notify(now):
                        notify_mouth()
            ui.update_status(state, mar)
            if show_camera:
                cv2.imshow('Camera', frame)
                if cv2.waitKey(int(1000/FRAME_RATE)) & 0xFF == ord('q'):
                    break
            else:
                time.sleep(1/FRAME_RATE)
    cap.release()
    if show_camera:
        cv2.destroyAllWindows()

if __name__ == "__main__":
    import sys
    # デフォルトはバックグラウンド監視（UI・映像・グラフなし）
    if len(sys.argv) > 1 and sys.argv[1] == "--ui":
        root = tk.Tk()
        ui = AppUI(root)
        t = threading.Thread(target=main_loop, args=(ui,), daemon=True)
        t.start()
        root.mainloop()
    else:
        class DummyUI:
            def update_status(self, state, mar):
                pass
        main_loop(DummyUI(), show_camera=False)
