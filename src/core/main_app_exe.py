import cv2
import numpy as np
import threading
import time
from win10toast import ToastNotifier
import argparse

# MediaPipeを直接インポート（drawing系を避ける）
try:
    from mediapipe import solutions
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    try:
        import mediapipe.solutions.face_mesh as mp_face_mesh
        MEDIAPIPE_AVAILABLE = True
    except ImportError:
        print("MediaPipeがインストールされていません。")
        MEDIAPIPE_AVAILABLE = False

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
                    self.state = "mouth_detected"
                    return self._should_notify(current_time)
        else:  # 口が閉じている
            self.state = "normal"
            self.mouth_open_start = None
        
        return False
    
    def _should_notify(self, current_time):
        # クールダウン期間をチェック
        if current_time - self.last_notify_time >= COOLDOWN_SEC:
            self.last_notify_time = current_time
            return True
        return False

# --- 口の開き度計算 ---
def calculate_mar(landmarks):
    """
    口の開き度（MAR: Mouth Aspect Ratio）を計算
    """
    # 口の輪郭の重要な点のインデックス（MediaPipe Face Meshの468個のランドマーク）
    mouth_points = [
        61, 84, 17, 314, 405, 320, 307, 375, 321, 308, 324, 318
    ]
    
    if len(landmarks) < 468:
        return 0.0
    
    # 口の上下の距離を計算
    upper_lip = landmarks[13]  # 上唇中央
    lower_lip = landmarks[14]  # 下唇中央
    
    # より正確な計算のため複数点を使用
    mouth_coords = []
    for idx in mouth_points:
        if idx < len(landmarks):
            point = landmarks[idx]
            mouth_coords.append([point.x, point.y])
    
    if len(mouth_coords) < 4:
        return 0.0
    
    mouth_coords = np.array(mouth_coords)
    
    # 口の幅と高さを計算
    y_coords = mouth_coords[:, 1]
    mouth_height = np.max(y_coords) - np.min(y_coords)
    
    x_coords = mouth_coords[:, 0]
    mouth_width = np.max(x_coords) - np.min(x_coords)
    
    # MAR計算（高さ/幅の比率）
    if mouth_width > 0:
        mar = mouth_height / mouth_width
    else:
        mar = 0.0
    
    return mar

# --- 通知機能 ---
def send_notification():
    """
    Windows通知を送信
    """
    try:
        toaster = ToastNotifier()
        toaster.show_toast(
            "口呼吸検出",
            "口呼吸を検出しました。鼻呼吸を意識してください。",
            duration=5,
            threaded=True
        )
        print(f"[{time.strftime('%H:%M:%S')}] 通知を送信しました")
    except Exception as e:
        print(f"通知送信エラー: {e}")

# --- メイン監視ループ ---
def main_monitoring_loop(duration_minutes=None):
    """
    口呼吸監視のメインループ  
    """
    if not MEDIAPIPE_AVAILABLE:
        print("MediaPipeが利用できません。")
        return
    
    try:
        # MediaPipe Face Mesh初期化
        face_mesh = solutions.face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
    except Exception as e:
        print(f"MediaPipe初期化エラー: {e}")
        return
    
    # カメラ初期化
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("カメラを開けませんでした。")
        return
    
    # フレームレート設定
    cap.set(cv2.CAP_PROP_FPS, FRAME_RATE)
    
    # 状態管理初期化
    state_machine = StateMachine()
    
    print(f"口呼吸監視を開始します...")
    if duration_minutes:
        print(f"監視時間: {duration_minutes}分")
    print("終了するには 'q' キーを押してください")
    
    start_time = time.time()
    frame_count = 0
    
    try:
        while True:
            success, image = cap.read()
            if not success:
                print("カメラからフレームを取得できませんでした")
                continue
            
            # 画像をRGBに変換（MediaPipe用）
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image_rgb.flags.writeable = False
            
            # Face Mesh処理
            results = face_mesh.process(image_rgb)
            
            current_time = time.time()
            
            if results.multi_face_landmarks:
                face_landmarks = results.multi_face_landmarks[0]
                
                # MAR計算
                mar = calculate_mar(face_landmarks.landmark)
                
                # 状態更新と通知判定
                should_notify = state_machine.update(mar, current_time)
                
                if should_notify:
                    # 別スレッドで通知送信
                    threading.Thread(target=send_notification, daemon=True).start()
                
                # デバッグ情報（コンソール出力）
                if frame_count % (FRAME_RATE * 5) == 0:  # 5秒毎
                    status_map = {
                        "normal": "正常",
                        "mouth_open": "口開き",
                        "mouth_detected": "口呼吸検出"
                    }
                    print(f"[{time.strftime('%H:%M:%S')}] MAR: {mar:.4f}, 状態: {status_map.get(state_machine.state, 'Unknown')}")
            
            frame_count += 1
            
            # 時間制限チェック
            if duration_minutes and (current_time - start_time) >= (duration_minutes * 60):
                print(f"{duration_minutes}分経過しました。監視を終了します。")
                break
            
            # フレームレート制御
            time.sleep(1.0 / FRAME_RATE)
            
            # 'q'キーで終了
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    except KeyboardInterrupt:
        print("\n監視を中断しました。")
    except Exception as e:
        print(f"エラーが発生しました: {e}")
    finally:
        cap.release()
        cv2.destroyAllWindows()
        if 'face_mesh' in locals():
            face_mesh.close()
        
    print("監視を終了しました。")

# --- メイン実行部 ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="口呼吸検出システム")
    parser.add_argument(
        "--duration", 
        type=int, 
        help="監視時間（分）。指定しない場合は無制限"
    )
    
    args = parser.parse_args()
    
    try:
        main_monitoring_loop(duration_minutes=args.duration)
    except Exception as e:
        print(f"アプリケーションエラー: {e}")
        input("何かキーを押してください...")