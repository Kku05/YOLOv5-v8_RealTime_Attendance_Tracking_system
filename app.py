from flask import Flask, render_template, request, redirect, url_for, Response, jsonify, session, flash
import os
import cv2
from ultralytics import YOLO
import face_recognition
import numpy as np
import csv
from sklearn.neighbors import KDTree
from datetime import datetime
import dlib
from scipy.spatial import distance as dist
import mediapipe as mp
import base64
import re
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PHOTOS_DIR = os.path.join(BASE_DIR, 'photos')
CLASSES_CSV = os.path.join(BASE_DIR, 'classes.csv')
USERS_CSV = os.path.join(BASE_DIR, 'users.csv')
KNOWN_FACES_CSV = os.path.join(BASE_DIR, 'known_faces.csv')
SECRET_KEY_FILE = os.path.join(BASE_DIR, '.secret_key')

os.makedirs(PHOTOS_DIR, exist_ok=True)

# ==============================================================================
# Security: Cryptographic Secret Key Management
# ==============================================================================
def get_or_create_secret_key():
    if os.environ.get('SECRET_KEY'):
        return os.environ.get('SECRET_KEY')
    if os.path.exists(SECRET_KEY_FILE):
        try:
            with open(SECRET_KEY_FILE, 'r', encoding='utf-8') as f:
                key = f.read().strip()
                if key:
                    return key
        except Exception:
            pass
    # Generate 32-byte secure random token
    new_key = os.urandom(32).hex()
    try:
        with open(SECRET_KEY_FILE, 'w', encoding='utf-8') as f:
            f.write(new_key)
    except Exception:
        pass
    return new_key

app.secret_key = get_or_create_secret_key()

# ==============================================================================
# Security: Salted Password Hashing & Credential Upgrade
# ==============================================================================
def ensure_secure_user_credentials():
    """Automatically upgrades any plain text passwords in users.csv to secure salted hashes."""
    if not os.path.exists(USERS_CSV):
        return

    updated_rows = []
    needs_rewrite = False

    with open(USERS_CSV, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader, None)
        for row in reader:
            if not row or len(row) < 2:
                continue
            u = row[0].strip()
            pwd = row[1].strip()
            assigned = row[2].strip() if len(row) > 2 else 'ALL'
            role = row[3].strip() if len(row) > 3 else 'Faculty'

            if not (pwd.startswith('scrypt:') or pwd.startswith('pbkdf2:')):
                pwd = generate_password_hash(pwd)
                needs_rewrite = True

            updated_rows.append([u, pwd, assigned, role])

    if needs_rewrite:
        with open(USERS_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['username', 'password_hash', 'assigned_classes', 'role'])
            writer.writerows(updated_rows)
        print("🔒 Successfully secured users.csv with cryptographic password hashes.")

ensure_secure_user_credentials()

# ==============================================================================
# Class & User Registry Handlers
# ==============================================================================
def get_all_classes():
    """Returns a list of standardized class dictionaries."""
    classes = []
    seen = set()
    if os.path.exists(CLASSES_CSV):
        with open(CLASSES_CSV, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader, None)
            for row in reader:
                if not row or not row[0].strip():
                    continue
                code = row[0].strip()
                name = row[1].strip() if len(row) > 1 else code
                dept = row[2].strip() if len(row) > 2 else 'General'
                if code.lower() not in seen:
                    classes.append({'code': code, 'name': name, 'department': dept})
                    seen.add(code.lower())

    # Also discover any classes from registered students
    students = get_registered_students_list()
    for s in students:
        c = s.get('class_name', '').strip()
        if c and c != 'Unassigned' and c.lower() not in seen:
            classes.append({'code': c, 'name': c, 'department': 'General'})
            seen.add(c.lower())

    return classes

def add_new_class(code, name=None, dept='General'):
    """Adds a new class to classes.csv if not already present."""
    code = code.strip()
    if not code:
        return
    existing = [c['code'].lower() for c in get_all_classes()]
    if code.lower() not in existing:
        if not os.path.exists(CLASSES_CSV):
            with open(CLASSES_CSV, 'w', newline='', encoding='utf-8') as f:
                f.write('class_code,class_name,department\n')
        with open(CLASSES_CSV, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([code, name if name else code, dept])

def get_teacher_assigned_classes(username):
    """Returns assigned classes for a specific teacher."""
    if not username:
        return []
    all_classes_list = [c['code'] for c in get_all_classes()]
    if os.path.exists(USERS_CSV):
        with open(USERS_CSV, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader, None)
            for row in reader:
                if not row or len(row) < 2:
                    continue
                u = row[0].strip()
                if u.lower() == username.strip().lower():
                    if len(row) > 2 and row[2].strip():
                        raw_assigned = row[2].strip()
                        if raw_assigned.upper() == 'ALL':
                            return all_classes_list
                        return [c.strip() for c in raw_assigned.split(';') if c.strip()]
    return all_classes_list

# ==============================================================================
# ==============================================================================
# Model & Landmark Initializations (Memory-Optimized Lazy Loading)
# ==============================================================================
import torch
torch.set_num_threads(1)  # Reduce PyTorch memory footprint for cloud containers

_model_cache = {}

def get_yolo_model(mode="yolov8_eye"):
    """Lazily loads only the requested model on-demand to stay within 512MB RAM."""
    is_v5 = mode.startswith("yolov5")
    key = "yolov5" if is_v5 else "yolov8"
    if key not in _model_cache:
        if is_v5:
            p = os.path.join(BASE_DIR, 'yolov5/yolov5su.pt')
            if not os.path.exists(p):
                p = os.path.join(BASE_DIR, 'yolov5/yolov5s.pt')
        else:
            p = os.path.join(BASE_DIR, 'yolov8/yolov8n.pt')
        _model_cache[key] = YOLO(p) if os.path.exists(p) else None
    return _model_cache.get(key)

# Dlib detector (lightweight)
dlib_detector = dlib.get_frontal_face_detector()

def get_dlib_predictor():
    """Lazily loads the 100MB dlib landmark file only when eye blink mode is active."""
    if "dlib_predictor" not in _model_cache:
        landmark_path = os.path.join(BASE_DIR, "shape_predictor_68_face_landmarks.dat")
        _model_cache["dlib_predictor"] = dlib.shape_predictor(landmark_path) if os.path.exists(landmark_path) else None
    return _model_cache.get("dlib_predictor")

# Thresholds for Anti-Spoofing Blink Detection
EAR_THRESHOLD = 0.28
EAR_CONSECUTIVE_MIN = 1
EAR_CONSECUTIVE_MAX = 5
BLINK_TIMEOUT = 1.0  # seconds between blinks

# Mediapipe Hands
try:
    mp_hands = mp.solutions.hands if hasattr(mp, 'solutions') and hasattr(mp.solutions, 'hands') else None
    mp_draw = mp.solutions.drawing_utils if hasattr(mp, 'solutions') and hasattr(mp.solutions, 'drawing_utils') else None
except Exception:
    mp_hands = None
    mp_draw = None

# Mode Display Names Mapping
MODE_DISPLAY_NAMES = {
    "yolov8_eye": "YOLOv8 + Eye Blink",
    "yolov8_hand": "YOLOv8 + Hand Gesture",
    "yolov5_eye": "YOLOv5 + Eye Blink",
    "yolov5_hand": "YOLOv5 + Hand Gesture",
    "yolov8_face": "YOLOv8 Standard Face",
    "yolov5_face": "YOLOv5 Standard Face"
}

# ==============================================================================
# Face Database & Student Encodings (Complete Metadata)
# ==============================================================================
known_face_encodings = []
known_face_names = []
known_face_ids = []
known_face_classes = []
known_face_emails = []
face_encodings_tree = None

def load_known_faces():
    global known_face_encodings, known_face_names, known_face_ids, known_face_classes, known_face_emails, face_encodings_tree
    known_face_encodings = []
    known_face_names = []
    known_face_ids = []
    known_face_classes = []
    known_face_emails = []

    if not os.path.exists(KNOWN_FACES_CSV):
        with open(KNOWN_FACES_CSV, 'w', newline='', encoding='utf-8') as f:
            f.write('image_path,name,id,class_name,email\n')

    if os.path.exists(KNOWN_FACES_CSV):
        with open(KNOWN_FACES_CSV, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            header = next(reader, None)
            for row in reader:
                if not row or len(row) < 3:
                    continue
                image_path = row[0].strip()
                name = row[1].strip()
                uid = row[2].strip()
                class_name = row[3].strip() if len(row) > 3 and row[3].strip() else 'Unassigned'
                email = row[4].strip() if len(row) > 4 and row[4].strip() else 'N/A'

                if not image_path or not name:
                    continue

                full_image_path = os.path.join(BASE_DIR, image_path) if not os.path.isabs(image_path) else image_path
                if os.path.exists(full_image_path):
                    try:
                        image = face_recognition.load_image_file(full_image_path)
                        encoding = face_recognition.face_encodings(image)
                        if encoding:
                            known_face_encodings.append(encoding[0])
                            known_face_names.append(name)
                            known_face_ids.append(uid)
                            known_face_classes.append(class_name)
                            known_face_emails.append(email)
                    except Exception as e:
                        print(f"Warning: Could not process face image {full_image_path}: {e}")

    if known_face_encodings:
        face_encodings_tree = KDTree(known_face_encodings)
    else:
        face_encodings_tree = None
    print(f"✅ Loaded {len(known_face_names)} known student face embeddings.")

def get_registered_students_list(class_filter=None):
    students = []
    if os.path.exists(KNOWN_FACES_CSV):
        with open(KNOWN_FACES_CSV, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            header = next(reader, None)
            for row in reader:
                if not row or len(row) < 3:
                    continue
                img = row[0].strip()
                name = row[1].strip()
                uid = row[2].strip()
                cname = row[3].strip() if len(row) > 3 and row[3].strip() else 'Unassigned'
                email = row[4].strip() if len(row) > 4 and row[4].strip() else 'N/A'

                if name and uid:
                    students.append({
                        'name': name,
                        'id': uid,
                        'class_name': cname,
                        'email': email,
                        'image_path': img
                    })

    if class_filter:
        cf = class_filter.strip().lower()
        exact_matches = [s for s in students if s['class_name'].lower() == cf]
        if exact_matches:
            return exact_matches
        
        partial_matches = [s for s in students if (cf in s['class_name'].lower() or s['class_name'].lower() in cf)]
        if partial_matches:
            return partial_matches

    return students

# Initial load
load_known_faces()

# ==============================================================================
# Global Attendance State
# ==============================================================================
attendance_data = []
recorded_names = set()
recorded_ids = set()
attendance_filename = ""
active_detection_mode = "yolov8_eye"
last_blink_time = datetime.now()

def calculate_ear(eye):
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])
    C = dist.euclidean(eye[0], eye[3])
    return (A + B) / (2.0 * C) if C != 0 else 0.0

# ==============================================================================
# Auth & Dashboard Routes
# ==============================================================================
@app.route('/')
def login():
    if 'username' in session:
        return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_user():
    username = (request.form.get('username') or '').strip()
    user_id = (request.form.get('user_id') or '').strip()

    matched_user = None
    if os.path.exists(USERS_CSV):
        with open(USERS_CSV, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            header = next(reader, None)
            for row in reader:
                if not row or len(row) < 2:
                    continue
                u = row[0].strip()
                pwd_hash = row[1].strip()
                assigned = row[2].strip() if len(row) > 2 else 'ALL'
                role = row[3].strip() if len(row) > 3 else 'Faculty'

                if u.lower() == username.lower():
                    # Validate hash or plaintext fallback
                    is_valid = False
                    if pwd_hash.startswith('scrypt:') or pwd_hash.startswith('pbkdf2:'):
                        is_valid = check_password_hash(pwd_hash, user_id)
                    else:
                        is_valid = (pwd_hash == user_id)

                    if is_valid:
                        matched_user = (u, assigned, role)
                        break

    if matched_user:
        session['username'] = matched_user[0]
        session['role'] = matched_user[2]
        session['is_admin'] = (matched_user[2].lower() in ['admin', 'administrator', 'principal'])
        load_known_faces()
        return redirect(url_for('home'))
    else:
        return render_template('login.html', error="Invalid username or password ID. Please try again.")

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/home')
def home():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    assigned_classes = get_teacher_assigned_classes(username)
    all_classes = get_all_classes()
    total_students = len(get_registered_students_list())
    
    return render_template(
        'home.html',
        username=username,
        role=session.get('role', 'Faculty'),
        is_admin=session.get('is_admin', False),
        assigned_classes=assigned_classes,
        all_classes=all_classes,
        total_students=total_students
    )

# ==============================================================================
# Student Registration & Management (Role-Based Admin Protection)
# ==============================================================================
@app.route('/register_student', methods=['GET', 'POST'])
def register_student():
    if 'username' not in session:
        return redirect(url_for('login'))

    error_msg = None
    success_msg = None

    if request.method == 'POST':
        student_name = (request.form.get('name') or '').strip()
        student_id = (request.form.get('id') or '').strip()
        selected_class = (request.form.get('class_select') or '').strip()
        custom_class = (request.form.get('custom_class') or '').strip()
        student_email = (request.form.get('email') or '').strip()
        image_data_b64 = request.form.get('webcam_image', '')
        uploaded_file = request.files.get('file_image')

        # Determine class name (from dropdown or custom input)
        student_class = custom_class if (selected_class == '__NEW__' or not selected_class) else selected_class

        if not student_name or not student_id or not student_class:
            error_msg = "Student Name, Roll/ID, and Class/Section are all required."
        else:
            # Check duplicate ID
            current_students = get_registered_students_list()
            if any(s['id'].lower() == student_id.lower() for s in current_students):
                error_msg = f"Student with ID '{student_id}' is already registered."
            else:
                # If a new class was entered, add to classes.csv automatically!
                add_new_class(student_class)

                safe_name = re.sub(r'[^a-zA-Z0-9_-]', '_', student_name.lower())
                safe_id = re.sub(r'[^a-zA-Z0-9_-]', '_', student_id)
                saved_filename = f"{safe_id}_{safe_name}.jpg"
                save_full_path = os.path.join(PHOTOS_DIR, saved_filename)
                rel_path = f"photos/{saved_filename}"

                image_saved = False

                if image_data_b64 and 'base64,' in image_data_b64:
                    try:
                        b64_content = image_data_b64.split('base64,')[1]
                        image_bytes = base64.b64decode(b64_content)
                        with open(save_full_path, 'wb') as f:
                            f.write(image_bytes)
                        image_saved = True
                    except Exception as e:
                        error_msg = f"Failed to decode webcam snapshot: {e}"
                elif uploaded_file and uploaded_file.filename:
                    try:
                        uploaded_file.save(save_full_path)
                        image_saved = True
                    except Exception as e:
                        error_msg = f"Failed to save uploaded photo: {e}"
                else:
                    error_msg = "Please capture a webcam photo or upload an image file."

                if image_saved:
                    try:
                        img_check = face_recognition.load_image_file(save_full_path)
                        encs = face_recognition.face_encodings(img_check)
                        if not encs:
                            if os.path.exists(save_full_path):
                                os.remove(save_full_path)
                            error_msg = "No clear human face detected in the image. Please retake or upload a clear frontal portrait."
                        else:
                            # Append to known_faces.csv with full details
                            file_exists = os.path.exists(KNOWN_FACES_CSV) and os.path.getsize(KNOWN_FACES_CSV) > 0
                            with open(KNOWN_FACES_CSV, 'a', newline='', encoding='utf-8') as f:
                                writer = csv.writer(f)
                                if not file_exists:
                                    writer.writerow(['image_path', 'name', 'id', 'class_name', 'email'])
                                writer.writerow([rel_path, student_name, student_id, student_class, student_email])

                            # Hot-reload in-memory embeddings immediately
                            load_known_faces()
                            success_msg = f"Student '{student_name}' (ID: {student_id}, Class: {student_class}) successfully registered!"
                    except Exception as e:
                        if os.path.exists(save_full_path):
                            os.remove(save_full_path)
                        error_msg = f"Face validation error: {e}"

    students = get_registered_students_list()
    classes = get_all_classes()
    return render_template(
        'register_student.html',
        students=students,
        classes=classes,
        error_msg=error_msg,
        success_msg=success_msg,
        is_admin=session.get('is_admin', False),
        total_students=len(students)
    )

@app.route('/delete_student/<student_id>', methods=['POST'])
def delete_student(student_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    # Security: Restrict deletion strictly to Administrator roles
    if not session.get('is_admin', False):
        flash("Access Denied: Only Administrators are authorized to delete student profiles.", "danger")
        return redirect(url_for('register_student'))

    current_students = get_registered_students_list()
    remaining_students = []
    deleted_image_path = None

    for s in current_students:
        if s['id'].strip() == student_id.strip():
            deleted_image_path = s.get('image_path', '')
        else:
            remaining_students.append(s)

    with open(KNOWN_FACES_CSV, 'w', newline='', encoding='utf-8') as file:
        fieldnames = ['image_path', 'name', 'id', 'class_name', 'email']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for s in remaining_students:
            writer.writerow({
                'image_path': s.get('image_path', ''),
                'name': s.get('name', ''),
                'id': s.get('id', ''),
                'class_name': s.get('class_name', 'Unassigned'),
                'email': s.get('email', 'N/A')
            })

    if deleted_image_path:
        full_img_path = os.path.join(BASE_DIR, deleted_image_path)
        if os.path.exists(full_img_path):
            try:
                os.remove(full_img_path)
            except Exception:
                pass

    load_known_faces()
    flash("Student profile successfully deleted by Administrator.", "success")
    return redirect(url_for('register_student'))

# ==============================================================================
# Attendance Taking Routes (Assigned + Substitute Class Support)
# ==============================================================================
@app.route('/take_attendance', methods=['GET', 'POST'])
def take_attendance():
    if 'username' not in session:
        return redirect(url_for('login'))

    global attendance_filename, recorded_names, recorded_ids, attendance_data, active_detection_mode, last_blink_time
    teacher_name = session['username']
    assigned_classes = get_teacher_assigned_classes(teacher_name)
    all_classes = get_all_classes()

    if request.method == 'POST':
        selected_class = (request.form.get('class_select') or '').strip()
        custom_class = (request.form.get('custom_class') or '').strip()
        active_detection_mode = request.form.get('detection_mode', 'yolov8_eye')

        class_name = custom_class if (selected_class == '__CUSTOM__' or not selected_class) else selected_class
        if not class_name:
            class_name = (request.form.get('class_name') or 'General').strip()

        # Check if substitute/proxy
        is_substitute = class_name not in assigned_classes

        # Auto-register new class if custom
        if custom_class:
            add_new_class(custom_class)

        session['active_class'] = class_name
        session['detection_mode'] = active_detection_mode
        session['is_substitute'] = is_substitute

        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        attendance_folder = os.path.join(BASE_DIR, f"attendance/{teacher_name}/{class_name}/{current_time[:8]}")
        os.makedirs(attendance_folder, exist_ok=True)
        attendance_filename = os.path.join(attendance_folder, f"{teacher_name}_{class_name}_{current_time}.csv")

        # Reset attendance session data (Duplicate Lockout)
        recorded_names = set()
        recorded_ids = set()
        attendance_data = []
        last_blink_time = datetime.now()

        mode_name = MODE_DISPLAY_NAMES.get(active_detection_mode, "YOLOv8 + Eye Blink")

        return render_template(
            'take_attendance.html',
            teacher_name=teacher_name,
            class_name=class_name,
            is_substitute=is_substitute,
            detection_mode=active_detection_mode,
            mode_name=mode_name,
            attendance_data=attendance_data
        )

    session.pop('active_class', None)
    session.pop('detection_mode', None)
    
    # Pre-select class if query parameter provided
    preselected_class = request.args.get('class', '')
    
    return render_template(
        'take_attendance.html',
        teacher_name=teacher_name,
        assigned_classes=assigned_classes,
        all_classes=all_classes,
        preselected_class=preselected_class
    )

@app.route('/get_attendance')
def get_attendance():
    if 'username' not in session:
        return jsonify([])
    global attendance_data
    return jsonify(attendance_data)

# ==============================================================================
# Dynamic Multi-Model Frame Generator with Anti-Spoofing & Duplicate Lockout
# ==============================================================================
# ==============================================================================
# Dynamic Multi-Model Frame Processor with Anti-Spoofing & Duplicate Lockout
# ==============================================================================
blink_counter = 0
blink_detected = False
eye_was_open = False

def process_single_frame(frame, mode="yolov8_eye"):
    """Processes a single BGR video frame with YOLO, anti-spoofing and face recognition."""
    global attendance_data, recorded_names, recorded_ids, last_blink_time, blink_counter, eye_was_open, blink_detected

    selected_model = get_yolo_model(mode)
    is_eye_mode = "eye" in mode
    is_hand_mode = "hand" in mode
    dlib_predictor_instance = get_dlib_predictor() if is_eye_mode else None
    mode_label = MODE_DISPLAY_NAMES.get(mode, "Detection Active")

    # Anti-Spoofing Eye Blink Detection
    if is_eye_mode and dlib_predictor_instance is not None:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = dlib_detector(gray)
        for face in faces:
            landmarks = dlib_predictor_instance(gray, face)
            left_eye = [(landmarks.part(i).x, landmarks.part(i).y) for i in range(36, 42)]
            right_eye = [(landmarks.part(i).x, landmarks.part(i).y) for i in range(42, 48)]

            left_ear = calculate_ear(left_eye)
            right_ear = calculate_ear(right_eye)
            ear = (left_ear + right_ear) / 2.0

            if ear < EAR_THRESHOLD:
                blink_counter += 1
            else:
                if EAR_CONSECUTIVE_MIN <= blink_counter <= EAR_CONSECUTIVE_MAX and eye_was_open:
                    current_time = datetime.now()
                    if (current_time - last_blink_time).total_seconds() > BLINK_TIMEOUT:
                        blink_detected = True
                        last_blink_time = current_time
                blink_counter = 0
                eye_was_open = True

            for (x, y) in left_eye + right_eye:
                cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)

    # Hand gesture detection
    hand_detected = False
    if is_hand_mode and mp_hands is not None:
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        with mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.7) as hands:
            hand_results = hands.process(rgb_frame)
            if hand_results.multi_hand_landmarks:
                for hand_landmarks in hand_results.multi_hand_landmarks:
                    mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                    hand_detected = True

    # YOLO object/face detection
    boxes = []
    confidences = []

    if selected_model is not None:
        results = selected_model(frame, verbose=False)
        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                confidence = float(box.conf[0])
                class_id = int(box.cls[0])

                if confidence > 0.45 and class_id == 0:
                    boxes.append([x1, y1, x2 - x1, y2 - y1])
                    confidences.append(confidence)

    # Robust Fallback: If close-up face has no YOLO body detection, use frontal face detector
    if len(boxes) == 0 and dlib_detector is not None:
        gray_f = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        d_faces = dlib_detector(gray_f, 0)
        for df in d_faces:
            fx1, fy1, fx2, fy2 = df.left(), df.top(), df.right(), df.bottom()
            boxes.append([fx1, fy1, fx2 - fx1, fy2 - fy1])
            confidences.append(0.95)

    indices = cv2.dnn.NMSBoxes(boxes, confidences, score_threshold=0.3, nms_threshold=0.3)

    for i in indices:
        box = boxes[i]
        x1, y1, w, h = box
        x2 = min(frame.shape[1], max(0, x1 + w))
        y2 = min(frame.shape[0], max(0, y1 + h))
        x1 = max(0, x1)
        y1 = max(0, y1)

        face_roi = frame[y1:y2, x1:x2]
        if face_roi.size == 0 or face_roi.shape[0] < 20 or face_roi.shape[1] < 20:
            continue

        rgb_face_roi = cv2.cvtColor(face_roi, cv2.COLOR_BGR2RGB)
        face_encodings = face_recognition.face_encodings(rgb_face_roi)
        if not face_encodings:
            continue

        face_encoding = face_encodings[0]
        name, uid, cname = "Unknown", "Unknown", "Unknown"
        if face_encodings_tree is not None:
            dist_val, ind = face_encodings_tree.query([face_encoding], k=1)
            best_match_index = ind[0][0]
            if dist_val[0][0] < 0.65:
                name = known_face_names[best_match_index]
                uid = known_face_ids[best_match_index]
                cname = known_face_classes[best_match_index] if best_match_index < len(known_face_classes) else 'N/A'

        # Liveness evaluation
        is_liveness_verified = False
        if is_eye_mode:
            is_liveness_verified = blink_detected
        elif is_hand_mode:
            is_liveness_verified = hand_detected
        else:
            is_liveness_verified = True

        # Anti-Spoofing & Duplicate Lockout
        if name != "Unknown" and is_liveness_verified:
            student_class = cname if cname != 'Unknown' else session.get('active_class', 'N/A')
            label = f"{name} ({uid})"

            if uid not in recorded_ids and name not in recorded_names:
                timestamp_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                attendance_data.append({
                    'Name': name,
                    'ID': uid,
                    'Class': student_class,
                    'Time': timestamp_now,
                    'Verification_Mode': mode_label
                })
                recorded_names.add(name)
                recorded_ids.add(uid)
                if is_eye_mode:
                    blink_detected = False
        else:
            label = name

        is_known = (name != "Unknown")
        is_already_marked = (uid in recorded_ids)

        if is_already_marked:
            color = (255, 191, 0)
            label += " [PRESENT]"
        elif is_known and is_liveness_verified:
            color = (0, 255, 0)
            label += " [LIVENESS VERIFIED]"
        elif is_known and not is_liveness_verified:
            color = (0, 165, 255)
            label += " [BLINK / GESTURE REQUIRED]"
        else:
            color = (0, 0, 255)

        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        cv2.putText(frame, label, (x1, max(15, y1 - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 2)

    # Mode banner overlay on video
    cv2.putText(frame, f"Engine: {mode_label}", (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
    return frame

def generate_frames(mode="yolov8_eye"):
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        cap = cv2.VideoCapture(1)

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    cap.set(cv2.CAP_PROP_FPS, 30)

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            processed = process_single_frame(frame, mode)
            ret, buffer = cv2.imencode('.jpg', processed)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
    finally:
        cap.release()

@app.route('/video_feed')
def video_feed():
    if 'username' not in session:
        return redirect(url_for('login'))
    mode = request.args.get('mode') or session.get('detection_mode', active_detection_mode)
    return Response(generate_frames(mode), mimetype='multipart/x-mixed-replace; boundary=frame')

# ==============================================================================
# Save & View Attendance Records with Cross-Instructor Substitute Discovery
# ==============================================================================
def find_attendance_files(class_name, date):
    """Finds all CSV attendance files across both regular and substitute instructor folders."""
    found = []
    base_att_dir = os.path.join(BASE_DIR, "attendance")
    if not os.path.exists(base_att_dir):
        return found

    for instructor in os.listdir(base_att_dir):
        folder = os.path.join(base_att_dir, instructor, class_name, date)
        if os.path.exists(folder):
            for f in os.listdir(folder):
                if f.endswith('.csv'):
                    found.append((f, os.path.join(folder, f), instructor))
    return found

@app.route('/save_attendance')
def save_attendance():
    if 'username' not in session:
        return redirect(url_for('login'))
    global attendance_filename, attendance_data
    if attendance_filename and attendance_data:
        is_substitute = session.get('is_substitute', False)
        instructor_role = "Substitute Instructor" if is_substitute else "Regular Instructor"

        with open(attendance_filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Name', 'ID', 'Class', 'Time', 'Verification_Mode', 'Instructor_Role']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for data in attendance_data:
                record = {
                    'Name': data.get('Name', ''),
                    'ID': data.get('ID', ''),
                    'Class': data.get('Class', session.get('active_class', 'N/A')),
                    'Time': data.get('Time', ''),
                    'Verification_Mode': data.get('Verification_Mode', MODE_DISPLAY_NAMES.get(active_detection_mode, 'Verified')),
                    'Instructor_Role': instructor_role
                }
                writer.writerow(record)
    return redirect(url_for('home'))

@app.route('/see_attendance', methods=['GET', 'POST'])
def see_attendance():
    if 'username' not in session:
        return redirect(url_for('login'))
    teacher_name = session['username']
    assigned_classes = get_teacher_assigned_classes(teacher_name)
    all_classes = get_all_classes()

    if request.method == 'POST':
        selected_class = (request.form.get('class_select') or '').strip()
        custom_class = (request.form.get('custom_class') or '').strip()
        class_name = custom_class if (selected_class == '__CUSTOM__' or not selected_class) else selected_class
        if not class_name:
            class_name = (request.form.get('class_name') or '').strip()

        date_raw = request.form.get('date', '').strip()
        date = date_raw.replace('-', '')
        
        # Discover all session files across regular and substitute teachers
        files_info = find_attendance_files(class_name, date)
        csv_files = [item[0] for item in files_info]
        
        return render_template(
            'see_attendance.html',
            teacher_name=teacher_name,
            class_name=class_name,
            date=date,
            csv_files=csv_files,
            assigned_classes=assigned_classes,
            all_classes=all_classes
        )
        
    return render_template(
        'see_attendance.html',
        teacher_name=teacher_name,
        csv_files=[],
        assigned_classes=assigned_classes,
        all_classes=all_classes
    )

@app.route('/view_attendance', methods=['POST'])
def view_attendance():
    if 'username' not in session:
        return redirect(url_for('login'))
    teacher_name = session['username']
    class_name = request.form.get('class_name', '').strip()
    date = request.form.get('date', '').strip()
    csv_file = request.form.get('csv_file', '').strip()

    attendance_records = []
    files_info = find_attendance_files(class_name, date)
    csv_files = [item[0] for item in files_info]

    # Find the target file across teacher directories
    target_path = None
    for fname, fpath, instructor in files_info:
        if fname == csv_file:
            target_path = fpath
            break

    present_ids = set()
    if target_path and os.path.exists(target_path):
        with open(target_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if 'Verification_Mode' not in row or not row['Verification_Mode']:
                    row['Verification_Mode'] = 'Standard Verified'
                if 'Class' not in row or not row['Class']:
                    row['Class'] = class_name
                attendance_records.append(row)
                if row.get('ID'):
                    present_ids.add(row['ID'].strip())

    # Get registered students belonging to this class (or all registered if no specific class match)
    class_students = get_registered_students_list(class_filter=class_name)
    if not class_students:
        class_students = get_registered_students_list()

    absent_records = [s for s in class_students if s['id'].strip() not in present_ids]

    total_registered = len(class_students)
    total_present = len(attendance_records)
    total_absent = len(absent_records)
    attendance_rate = round((total_present / total_registered * 100), 1) if total_registered > 0 else 0

    stats = {
        'total_registered': total_registered,
        'total_present': total_present,
        'total_absent': total_absent,
        'attendance_rate': attendance_rate
    }

    assigned_classes = get_teacher_assigned_classes(teacher_name)
    all_classes = get_all_classes()

    return render_template(
        'see_attendance.html',
        teacher_name=teacher_name,
        class_name=class_name,
        date=date,
        csv_file=csv_file,
        attendance_records=attendance_records,
        absent_records=absent_records,
        stats=stats,
        csv_files=csv_files,
        assigned_classes=assigned_classes,
        all_classes=all_classes
    )

# ==============================================================================
# Main Entry Point
# ==============================================================================
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5001))
    host = os.environ.get("HOST", "0.0.0.0")
    print(f"🚀 Starting Unified Attendance System on http://{host}:{port}")
    app.run(host=host, port=port, debug=False)
