import cv2
import mediapipe as mp
import numpy as np

mp_face = mp.solutions.face_mesh

# MAR計算用インデックス（唇上下）
UPPER_LIP_IDX = 13  # 上唇中央
LOWER_LIP_IDX = 14  # 下唇中央

def calc_mar(landmarks, image_shape):
    h, w = image_shape[:2]
    upper = landmarks[UPPER_LIP_IDX]
    lower = landmarks[LOWER_LIP_IDX]
    # 顔サイズ正規化（例: 顔高さ）
    mar = abs((lower.y - upper.y) * h)
    face_height = abs((landmarks[10].y - landmarks[152].y) * h)  # 顔上下
    return mar / face_height if face_height > 0 else 0

cap = cv2.VideoCapture(0)
with mp_face.FaceMesh(static_image_mode=False, max_num_faces=1, refine_landmarks=True) as face_mesh:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb)
        mar = None
        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                lm = face_landmarks.landmark
                mar = calc_mar(lm, frame.shape)
                print(f"MAR:{mar:.3f}", flush=True)
                # 可視化（オプション）
                cv2.putText(frame, f"MAR:{mar:.3f}", (30,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
        cv2.imshow('Camera', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
cap.release()
cv2.destroyAllWindows()
