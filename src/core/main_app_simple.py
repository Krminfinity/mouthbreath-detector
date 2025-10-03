import cv2
import mediapipe as mp
import numpy as np
import threading
import time
from win10toast import ToastNotifier
import argparse

# --- 設定値 ---
MAR_THRESHOLD_HIGH = 0.002
MAR_THRESHOLD_LOW = 0.001
NOTIFY_DURATION = 1   # 口開き連続秒数（1秒以上で通知）
COOLDOWN_SEC = 300   # 通知クールダウン
FRAME_RATE = 10      # fps

# --- 状態管理 ---
class StateMachine:
    def __init__(self):
        self.state = "normal"  # "normal", "mouth_open", "mouth_detected"
        self.mouth_open_start = None
        self.last_notify_time = 0
        
    def update(self, mar, current_time):
        # 口呼吸判定ロジック
        if mar < MAR_THRESHOLD_HIGH:  # 口が開いている
            if self.state == "normal":
                self.state = "mouth_open"
                self.mouth_open_start = current_time
            elif self.state == "mouth_open":
                # 口開き継続時間をチェック
                if current_time - self.mouth_open_start >= NOTIFY_DURATION:
                    if current_time - self.last_notify_time >= COOLDOWN_SEC:
                        self.state = "mouth_detected"
                        self.last_notify_time = current_time
                        return True  # 通知を送信
        else:  # 口が閉じている
            self.state = "normal"
            self.mouth_open_start = None
            
        return False

# グローバル変数
is_running = True
state_machine = StateMachine()

def calculate_mar(landmarks):
    """
    口のアスペクト比（MAR）を計算
    """
    # 上唇と下唇の重要なランドマーク
    # 13, 14 (上唇中央), 17, 18 (下唇中央)
    # 61, 291 (口角)
    
    upper_lip = landmarks[13]  # 上唇中央
    lower_lip = landmarks[17]  # 下唇中央
    left_corner = landmarks[61]   # 左口角
    right_corner = landmarks[291]  # 右口角
    
    # 垂直距離（上唇と下唇の距離）
    vertical_distance = np.sqrt((upper_lip.x - lower_lip.x)**2 + (upper_lip.y - lower_lip.y)**2)
    
    # 水平距離（左右の口角の距離）
    horizontal_distance = np.sqrt((left_corner.x - right_corner.x)**2 + (left_corner.y - right_corner.y)**2)
    
    # MAR = 垂直距離 / 水平距離
    if horizontal_distance == 0:
        return 0
    
    mar = vertical_distance / horizontal_distance
    return mar

def send_notification():
    """
    Windows通知を送信
    """
    try:
        toaster = ToastNotifier()
        toaster.show_toast(
            "口呼吸検出",
            "口呼吸が検出されました。鼻呼吸を意識してください。",
            icon_path=None,
            duration=3,
            threaded=True
        )
        print(f"[{time.strftime('%H:%M:%S')}] 通知送信: 口呼吸検出")
    except Exception as e:
        print(f"通知エラー: {e}")

def background_monitor():
    """
    バックグラウンドでの監視機能
    """
    print("口呼吸検出システムを開始します...")
    print("終了するには Ctrl+C を押してください")
    
    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(
        static_image_mode=False,
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("エラー: カメラにアクセスできません")
        return
    
    global is_running
    
    try:
        while is_running:
            ret, frame = cap.read()
            if not ret:
                continue
            
            # RGB変換
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = face_mesh.process(rgb_frame)
            
            current_time = time.time()
            
            if results.multi_face_landmarks:
                for face_landmarks in results.multi_face_landmarks:
                    # MARを計算
                    mar = calculate_mar(face_landmarks.landmark)
                    
                    # 状態更新
                    should_notify = state_machine.update(mar, current_time)
                    
                    if should_notify:
                        # 通知を別スレッドで送信
                        notification_thread = threading.Thread(target=send_notification)
                        notification_thread.daemon = True
                        notification_thread.start()
                    
                    # デバッグ出力（定期的に）
                    if int(current_time) % 10 == 0:
                        print(f"[{time.strftime('%H:%M:%S')}] MAR: {mar:.4f}, State: {state_machine.state}")
            
            # フレームレート制御
            time.sleep(1.0 / FRAME_RATE)
            
    except KeyboardInterrupt:
        print("\n終了中...")
    finally:
        cap.release()
        cv2.destroyAllWindows()

def display_ui():
    """
    UI表示モード（簡易版）
    """
    print("UI表示モードは現在開発中です。")
    print("バックグラウンドモードを使用してください。")
    background_monitor()

def main():
    parser = argparse.ArgumentParser(description='口呼吸検出システム')
    parser.add_argument('--ui', action='store_true', help='UI表示モードで起動')
    args = parser.parse_args()
    
    if args.ui:
        display_ui()
    else:
        background_monitor()

if __name__ == "__main__":
    main()