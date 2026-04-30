"""
Driver Drowsiness Detection System
Real-time monitoring using webcam and MediaPipe
"""

import cv2
import numpy as np
import mediapipe as mp
import time
import threading
import base64
import warnings
warnings.filterwarnings('ignore')

from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize MediaPipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# Eye and mouth indices for MediaPipe Face Mesh
# Left eye indices
LEFT_EYE = [33, 160, 158, 133, 153, 144]
RIGHT_EYE = [362, 385, 387, 263, 373, 380]
# Mouth indices for yawn detection
MOUTH_TOP = [13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28]
MOUTH_BOTTOM = [78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93]
# Full mouth indices
MOUTH = [61, 146, 91, 181, 84, 17, 314, 405, 320, 307, 375, 321, 308, 324, 318, 402, 317, 14, 87, 178, 88, 95]

# Global variables
drowsy_counter = 0
alarm_playing = False
status = "Awake"
ear_value = 0.0
mar_value = 0.0
alarm_thread = None

# Thresholds
EYE_AR_THRESH = 0.25
EYE_AR_CONSEC_FRAMES = 15  # Reduced for quicker detection
MOUTH_AR_THRESH = 0.5

def eye_aspect_ratio(landmarks, eye_indices):
    """
    Calculate Eye Aspect Ratio (EAR)
    """
    try:
        points = []
        for idx in eye_indices:
            point = landmarks[idx]
            points.append([point.x, point.y])
        
        points = np.array(points, dtype=np.float32)
        
        # Compute euclidean distances
        vertical1 = np.linalg.norm(points[1] - points[5])
        vertical2 = np.linalg.norm(points[2] - points[4])
        horizontal = np.linalg.norm(points[0] - points[3])
        
        if horizontal == 0:
            return 0.0
            
        ear = (vertical1 + vertical2) / (2.0 * horizontal)
        return float(ear)
    except Exception as e:
        return 0.0

def mouth_aspect_ratio(landmarks):
    """
    Calculate Mouth Aspect Ratio (MAR) for yawn detection
    """
    try:
        # Get mouth points
        top_lip = landmarks[13]
        bottom_lip = landmarks[14]
        left_corner = landmarks[78]
        right_corner = landmarks[308]
        
        # Calculate vertical distance
        vertical = np.abs(top_lip.y - bottom_lip.y)
        
        # Calculate horizontal distance
        horizontal = np.abs(left_corner.x - right_corner.x)
        
        if horizontal == 0:
            return 0.0
            
        mar = vertical / horizontal
        return float(mar)
    except Exception as e:
        return 0.0

def play_alarm_windows():
    """Play alarm sound on Windows"""
    global alarm_playing
    import winsound
    while alarm_playing:
        try:
            winsound.Beep(1000, 500)  # 1000 Hz for 500ms
            time.sleep(0.3)
        except:
            pass

def play_alarm_other():
    """Play alarm sound on other OS"""
    global alarm_playing
    while alarm_playing:
        try:
            print('\a', end='', flush=True)
            time.sleep(0.5)
        except:
            pass

def start_alarm():
    """Start alarm in separate thread"""
    global alarm_thread, alarm_playing
    import sys
    if alarm_thread is None or not alarm_thread.is_alive():
        if sys.platform == "win32":
            alarm_thread = threading.Thread(target=play_alarm_windows, daemon=True)
        else:
            alarm_thread = threading.Thread(target=play_alarm_other, daemon=True)
        alarm_thread.start()

def stop_alarm():
    """Stop the alarm"""
    global alarm_playing
    alarm_playing = False

def process_frame(frame):
    """Process each frame for drowsiness detection"""
    global drowsy_counter, alarm_playing, status, ear_value, mar_value
    
    # Convert BGR to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb_frame)
    
    status = "Awake"
    
    if results.multi_face_landmarks:
        face_landmarks = results.multi_face_landmarks[0]
        landmarks = face_landmarks.landmark
        
        # Calculate EAR for both eyes
        left_ear = eye_aspect_ratio(landmarks, LEFT_EYE)
        right_ear = eye_aspect_ratio(landmarks, RIGHT_EYE)
        ear_value = (left_ear + right_ear) / 2.0
        
        # Calculate MAR for yawn detection
        mar_value = mouth_aspect_ratio(landmarks)
        
        # Draw landmarks on face
        h, w = frame.shape[:2]
        
        # Draw eye landmarks
        for idx in LEFT_EYE + RIGHT_EYE:
            point = landmarks[idx]
            cx, cy = int(point.x * w), int(point.y * h)
            cv2.circle(frame, (cx, cy), 1, (0, 255, 0), -1)
        
        # Draw mouth landmarks
        mouth_points = [13, 14, 78, 308, 61, 291]
        for idx in mouth_points:
            point = landmarks[idx]
            cx, cy = int(point.x * w), int(point.y * h)
            cv2.circle(frame, (cx, cy), 1, (0, 0, 255), -1)
        
        # Drowsiness detection based on EAR
        if ear_value < EYE_AR_THRESH:
            drowsy_counter += 1
            
            if drowsy_counter >= EYE_AR_CONSEC_FRAMES:
                status = "Drowsy"
                if not alarm_playing:
                    alarm_playing = True
                    start_alarm()
        else:
            drowsy_counter = max(0, drowsy_counter - 1)  # Gradually decrease
            if alarm_playing:
                alarm_playing = False
                stop_alarm()
        
        # Yawn detection
        if mar_value > MOUTH_AR_THRESH:
            cv2.putText(frame, "YAWNING!", (frame.shape[1] - 150, 70), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        
    else:
        ear_value = 0.0
        mar_value = 0.0
        drowsy_counter = 0
        if alarm_playing:
            alarm_playing = False
            stop_alarm()
        cv2.putText(frame, "No Face Detected", (frame.shape[1]//2 - 80, frame.shape[0]//2),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    
    # Display status and metrics
    color = (0, 255, 0) if status == "Awake" else (0, 0, 255)
    
    # Background for text
    cv2.rectangle(frame, (0, 0), (250, 120), (0, 0, 0), -1)
    cv2.rectangle(frame, (0, 0), (250, 120), (255, 255, 255), 1)
    
    cv2.putText(frame, f"Status: {status}", (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
    cv2.putText(frame, f"EAR: {ear_value:.2f}", (10, 55), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    cv2.putText(frame, f"MAR: {mar_value:.2f}", (10, 80), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    cv2.putText(frame, f"Counter: {drowsy_counter}/{EYE_AR_CONSEC_FRAMES}", (10, 105), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
    
    # Warning message
    if status == "Drowsy":
        # Draw warning rectangle
        cv2.rectangle(frame, (0, frame.shape[0]-60), (frame.shape[1], frame.shape[0]), (0, 0, 255), -1)
        cv2.putText(frame, "!!! DROWSY - WAKE UP !!!", (frame.shape[1]//2-150, frame.shape[0]-20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    return frame

def generate_frames():
    """Generate video frames for streaming"""
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: Could not open camera!")
        return
    
    # Set camera properties
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    print("Camera initialized successfully!")
    
    while True:
        success, frame = cap.read()
        if not success:
            print("Failed to grab frame")
            break
        
        # Process frame
        frame = process_frame(frame)
        
        # Encode frame as JPEG
        try:
            ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
            if ret:
                frame_bytes = base64.b64encode(buffer).decode('utf-8')
                
                # Emit frame via WebSocket
                socketio.emit('video_frame', {
                    'frame': frame_bytes,
                    'status': status,
                    'ear': f"{ear_value:.2f}",
                    'mar': f"{mar_value:.2f}"
                })
            else:
                print("Failed to encode frame")
        except Exception as e:
            print(f"Error encoding frame: {e}")
        
        time.sleep(0.033)  # ~30 FPS
    
    cap.release()
    print("Camera released")

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print('Client connected')
    # Start video processing in a separate thread
    video_thread = threading.Thread(target=generate_frames, daemon=True)
    video_thread.start()
    emit('connected', {'data': 'Connected to server'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    global alarm_playing
    alarm_playing = False
    print('Client disconnected')

if __name__ == '__main__':
    print("=" * 60)
    print("🚗 DRIVER DROWSINESS DETECTION SYSTEM")
    print("=" * 60)
    print("Starting server...")
    print("Please ensure your webcam is connected and accessible")
    print("\n📱 Open your browser and go to: http://localhost:5000")
    print("⌨️  Press Ctrl+C to stop the server")
    print("=" * 60)
    
    try:
        socketio.run(app, debug=False, port=5000, host='0.0.0.0', allow_unsafe_werkzeug=True)
    except KeyboardInterrupt:
        print("\n\nServer stopped by user")
    except Exception as e:
        print(f"\nError: {e}")
        print("\nMake sure:")
        print("1. Webcam is connected")
        print("2. No other app is using the camera")
        print("3. Install all dependencies: pip install -r requirements.txt")