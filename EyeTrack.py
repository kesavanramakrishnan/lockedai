import cv2
import mediapipe as mp
import numpy as np

cap = cv2.VideoCapture(0)
face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)

minX = float('inf')
maxX = float('-inf')

while True:
    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)
    if not ret:
        print('Unable to retrieve from webcam')
        break
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    h, w, _ = frame.shape

    mesh = face_mesh.process(rgb)
    landmark_pts = mesh.multi_face_landmarks
    if landmark_pts:    

        # Creating ROI based on center nose point
        nose = landmark_pts[0].landmark[168]
        cx = int(nose.x * w)
        cy = int(nose.y * h)
        
        size = 600
        x1 = max(0, cx - size//2)
        y1 = max(0, cy - size//2)
        x2 = min(w, cx + size//2)
        y2 = min(h, cy + size//2)

        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0))
        roi = frame[y1:y2, x1:x2]

        # Tracking center eye coordinate
        rh, rw, _ = roi.shape
        eye_r = landmark_pts[0].landmark[473]
        rx = int(eye_r.x * rw)
        ry = int(eye_r.y * rh)
        x = int(eye_r.x * w)
        y = int(eye_r.y * h)
        cv2.circle(frame, (x, y), 2, (0, 255, 0))
        print(f"cx: {rx}, cy: {ry}")

        if rx > maxX:
            maxX = rx
        elif rx < minX:
            minX = rx 
    
    cv2.imshow("Face Mesh", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
print(f"min: {minX}, max: {maxX}")