from flask import Flask, request, render_template, Response
import cv2
import mediapipe as mp
import numpy as np
from flask_cors import CORS
from flask_cors import cross_origin
from pushover_complete import PushoverAPI
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Handle the form submission
        message = request.form.get('message')
        # Here you would trigger the notification to your iPhone
        send_notification_to_iphone(message)
        return 'Notification sent!'
    return render_template('index.html')


# import smtplib
# from email.mime.text import MIMEText

# def send_notification_to_iphone(message):
#     smtp_server = 'smtp.gmail.com'
#     smtp_port = 587
#     sender_email = 'lockedincal11@gmail.com'
#     receiver_email = 'kesavan6002@gmail.com'
#     password = 'lockedin11'

#     msg = MIMEText(message)
#     msg['Subject'] = 'Notification from Flask'
#     msg['From'] = sender_email
#     msg['To'] = receiver_email

#     with smtplib.SMTP(smtp_server, smtp_port) as server:
#         server.starttls()
#         server.login(sender_email, password)
#         server.sendmail(sender_email, receiver_email, msg.as_string())
#     print("Email sent successfully!")
global user_key

def send_notification_to_iphone(message):
    device = 'email'
    api_token = 'axup77m6g6snv69v5n9vv2r68c8q16'
    pushover = PushoverAPI(api_token)
    pushover.send_message(user_key,message,title="Notification from Flask")
    # pushover.send_message(message, device,user_key, title="Notification from Flask")


# Initialize Mediapipe Face Mesh detector


global stream_active 
stream_active = True

global sleep_data
sleep_data = []

global sleepTrack
sleepTrack = True

global focusTrack
focusTrack = True


def euc_dist(p1, p2, w, h):
        return np.sqrt((int(p1.x * w) - int(p2.x * w))**2 + (int(p1.y * h) - int(p2.y * h))**2)
def eye_track():
    # Initializing video and mesh model


    # Calibration vars
    calibration_frames = fps * 10
    

    

    while True:
        ret, frame = cap.read()
        h, w, _ = frame.shape
        if not ret:
            print("Unable to retrieve webcam frame")
            break
        
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mesh = face_mesh.process(rgb)
        landmark_pts = mesh.multi_face_landmarks
        

def generate_frames():
    global baseline_eye_distance, baseline_face_width, calibrate_eye_distance_total, calibrate_face_width_total, frame_count

    cap = cv2.VideoCapture(0)
    fps = cap.get(cv2.CAP_PROP_FPS)

    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True)

    # Calibration variables
    baseline_eye_distance = None  # Distance between eyelids during calibration
    baseline_face_width = None    # Face width during calibration

    calibrate_eye_distance_total = 0
    calibrate_face_width_total = 0
    calibration_frames = fps * 10
    frame_count = 0

    closed_eye_counter = 0
    sleep_threshold = 5 * fps
    sleeping = 0
    
    counter = 0
    vert_dists = []
    hori_dists = []
    hori = None
    vert = None

    u_count = 0
    f_count = 0


    while True:
        
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Process the frame to get landmarks
        results = face_mesh.process(rgb_frame)
        landmark_pts = results.multi_face_landmarks
        

        h, w, _ = frame.shape
        global focusTrack
        global sleepTrack
        if results.multi_face_landmarks:
           if stream_active:
                landmarks = results.multi_face_landmarks[0].landmark

                # Get key landmarks for the eye
                top_right = landmarks[159]  # Top of right eye
                bottom_right = landmarks[145]  # Bottom of right eye
                
                # Get key landmarks for focus
                forehead = landmarks[151]
                chin = landmarks[175]
                lc = landmarks[411]
                rc = landmarks[187]
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
                    cv2.putText(frame, "Calibrating... Keep your eyes open and don't move your head!", (50, 50),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
                    calibrate_eye_distance_total += eye_distance
                    calibrate_face_width_total += face_width
                    vert_dists.append(euc_dist(forehead, chin, w, h))
                    hori_dists.append(euc_dist(lc, rc, w, h))
                    frame_count += 1
                    
                if sleepTrack:        
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
                    if normalized_eye_distance < baseline_eye_distance * 0.70:
                        closed_eye_counter += 1
                        sleep_data.append(0)
                        cv2.putText(frame, "Eyes Closed", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
                    else:
                        print("Eyes Open")
                        sleep_data.append(1)
                        cv2.putText(frame, "Eyes Open", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
                    if closed_eye_counter >= sleep_threshold:
                        sleeping += 1
                        send_notification_to_iphone("WAKE UP!!")                
                        closed_eye_counter = 0  
                
                if focusTrack:
                    if hori is None or vert is None:
                        hori = np.mean(hori_dists, axis=0)
                        vert = np.mean(vert_dists, axis=0)
                    
                    hori_c = euc_dist(forehead, chin, w, h)
                    vert_c = euc_dist(lc, rc, w, h) 


                    if hori_c <= 0.77 * hori or vert_c <= 0.687 * vert:
                        cv2.putText(frame, "Unfocused", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                        sleep_data.append(0)
                    else:
                        cv2.putText(frame, "Focused", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                        sleep_data.append(1) 

        # Encode the frame in JPEG format
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        # Yield the frame in byte format
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    cap.release()
    
@app.route('/receive_data', methods=['POST'])
def receive_data():
  data = request.json
  global user_key
  user_key = data["user_email"]
  global focusTrack
  focusTrack = data["focus"]
  global sleepTrack
  focusTrack = data["sleep"]
  print(user_key)
  return user_key

@app.route('/video_feed',  methods=['GET'])
@cross_origin()
def video_feed():
  print('here')
  return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/pause_stream', methods=['POST'])
def pause_stream():
    global stream_active
    stream_active = False
    global sleep_data
    zerocount = 0
    for i in sleep_data:
        if i == 0:
            zerocount += 1

    data = {
        "zero": zerocount,
        "one": len(sleep_data) - zerocount
    }
    return data

@app.route('/resume_stream', methods=['POST'])
def resume_stream():
    global sleep_data
    sleep_data = []
    global stream_active
    stream_active = True
    video_feed()
    return 'Stream resumed'



if __name__ == '__main__':
    app.run(debug=True)

