import cv2
import mediapipe as mp
import numpy as np

# Initialize Mediapipe Face Mesh detector
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True)

cap = cv2.VideoCapture(0)

# Calibration variables
baseline_eye_distance = None  # Distance between eyelids during calibration
baseline_face_width = None    # Face width during calibration

calibrate_eye_distance_total = 0
calibrate_face_width_total = 0
calibration_frames = 120
frame_count = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process the frame to get landmarks
    results = face_mesh.process(rgb_frame)

    h, w, _ = frame.shape

    if results.multi_face_landmarks:
        landmarks = results.multi_face_landmarks[0].landmark

        # Get key landmarks for the eye
        top_right = landmarks[159]  # Top of right eye
        bottom_right = landmarks[145]  # Bottom of right eye

        # Convert normalized coordinates to pixel coordinates
        top_right_px = (int(top_right.x * w), int(top_right.y * h))
        bottom_right_px = (int(bottom_right.x * w), int(bottom_right.y * h))

        # Calculate the pixel distance between the top and bottom eyelid
        eye_distance = np.linalg.norm(np.array(top_right_px) - np.array(bottom_right_px))

        # Calculate face width using landmarks on the left and right side of the face
        left_cheek = landmarks[234]  # Left edge of the face
        right_cheek = landmarks[454]  # Right edge of the face
        left_cheek_px = (int(left_cheek.x * w), int(left_cheek.y * h))
        right_cheek_px = (int(right_cheek.x * w), int(right_cheek.y * h))

        # Calculate face width in pixels
        face_width = np.linalg.norm(np.array(left_cheek_px) - np.array(right_cheek_px))

        # Calibration step: Set baseline eye distance and face width
        if frame_count < calibration_frames:
            cv2.putText(frame, "Calibrating... Keep your eyes open!", (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
            calibrate_eye_distance_total += eye_distance
            calibrate_face_width_total += face_width
            frame_count += 1
            
        baseline_eye_distance = calibrate_eye_distance_total / calibration_frames
        baseline_face_width = calibrate_face_width_total / calibration_frames


        # Calculate the scaling factor based on face width
        scaling_factor = baseline_face_width / face_width

        # Normalize the current eye distance
        normalized_eye_distance = eye_distance * scaling_factor
        # print(f"Normalized Eye Distance: {normalized_eye_distance}")

        # Display circles on the landmarks
        cv2.circle(frame, top_right_px, 3, (0, 255, 0), -1)
        cv2.circle(frame, bottom_right_px, 3, (0, 255, 0), -1)

        # Determine if eyes are open or closed using a threshold
        if normalized_eye_distance < baseline_eye_distance * 0.71:
            print("Eyes Closed")
        else:
            print("Eyes Open")

    # Show the video feed
    cv2.imshow("Eye Tracker", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
