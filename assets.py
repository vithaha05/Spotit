# Gesture Music Controller
# Control your music with hand gestures!

import cv2
import mediapipe as mp
import numpy as np
import time
from collections import deque, Counter
import math

# Import music control modules
from music_controller import MusicController
from gesture_actions import GestureActions

# ---------------------------
# Config
# ---------------------------
CAM_W, CAM_H = 640, 480
PROCESS_EVERY_N_FRAMES = 1

BLINK_EAR_THRESH = 0.18
MOUTH_OPEN_THRESH = 0.045
HANDS_JOINED_DIST = 0.08
NOD_HISTORY = 12
NOD_SPEED_THRESH = 0.018
GESTURE_HISTORY_LEN = 5

# ---------------------------
# Helpers
# ---------------------------
def dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])

def mouth_gap(face):
    try:
        top = face[13]
        bot = face[14]
        left = face[234]
        right = face[454]
    except:
        return 0
    gap = dist((top.x, top.y), (bot.x, bot.y))
    width = dist((left.x, left.y), (right.x, right.y))
    return gap / width if width else 0

mp_holistic = mp.solutions.holistic
mp_drawing = mp.solutions.drawing_utils

L_EYE = {"outer": 33, "inner": 133, "top": 159, "bottom": 145}
R_EYE = {"outer": 362, "inner": 263, "top": 386, "bottom": 374}
NOSE = 1
INDEX_TIP = 8
INDEX_PIP = 6
WRIST = 0

# ---------------------------
# Main
# ---------------------------
def main():
    # Initialize music controller
    music_controller = MusicController()
    gesture_actions = GestureActions(music_controller)

    # Initialize MediaPipe Holistic
    holistic = mp_holistic.Holistic(
        min_detection_confidence=0.6,
        min_tracking_confidence=0.6
    )

    cap = cv2.VideoCapture(0)
    cap.set(3, CAM_W)
    cap.set(4, CAM_H)

    frame_count = 0
    nose_history = deque(maxlen=NOD_HISTORY)
    gesture_history = deque(maxlen=GESTURE_HISTORY_LEN)
    last_action = None
    action_display_time = 0

    print("\n" + "=" * 60)
    print("🎵 GESTURE MUSIC CONTROLLER 🎵")
    print("=" * 60)
    print("\nControls:")
    print("  • Right Hand Up 🙋‍♂️  → Previous Track ⏮")
    print("  • Left Hand Up 🙋‍♀️   → Next Track ⏭")
    print("  • Closed Fist ✊   → Play ▶")
    print("  • Open Palm ✋     → Pause ⏸")
    print("  • Index Up ☝️      → Volume Up 🔊")
    print("  • Peace Sign ✌️    → Volume Down 🔉")
    print("  • Crossed Arms 🙅  → Mute/Unmute 🔇")
    print("\n  Press 'q' to quit")
    print("=" * 60)
    print("\n🎧 Open your music app (Spotify, Apple Music, etc.)")
    print("📷 Starting camera for gesture detection...\n")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        if frame_count % PROCESS_EVERY_N_FRAMES == 0:
            results = holistic.process(rgb)
        frame_count += 1

        gesture = "neutral"
        face = None
        current_time = time.time()

        # --------------------------------------------
        # FACE DETECTION
        # --------------------------------------------
        if results.face_landmarks:
            face = results.face_landmarks.landmark
            nose_history.append(face[NOSE].y)

        # HANDS
        lh = results.left_hand_landmarks.landmark if results.left_hand_landmarks else None
        rh = results.right_hand_landmarks.landmark if results.right_hand_landmarks else None

        # Draw hand mesh
        if results.left_hand_landmarks:
            mp_drawing.draw_landmarks(frame, results.left_hand_landmarks, 
                                     mp.solutions.hands.HAND_CONNECTIONS)
        if results.right_hand_landmarks:
            mp_drawing.draw_landmarks(frame, results.right_hand_landmarks, 
                                     mp.solutions.hands.HAND_CONNECTIONS)

        # RUBBING DETECTION (both hands close together)
        if lh and rh:
            d = dist((lh[INDEX_TIP].x, lh[INDEX_TIP].y), 
                    (rh[INDEX_TIP].x, rh[INDEX_TIP].y))
            if d < HANDS_JOINED_DIST:
                gesture = "rubbing"


        # ---------------------------
        # Gesture stabilization
        # ---------------------------
        gesture_history.append(gesture)
        chosen = Counter(gesture_history).most_common(1)[0][0]

        # ---------------------------
        # Process gestures
        # ---------------------------
        action = gesture_actions.process_gesture(chosen, lh, rh, face, results.pose_landmarks.landmark if results.pose_landmarks else None)
        
        if action:
            action_map = {
                "play_pause": "▶⏸ Play/Pause",
                "volume_up": "🔊 Volume Up",
                "volume_down": "🔉 Volume Down",
                "mute": "🔇 Mute Toggle"
            }
            last_action = action_map.get(action, action)
            action_display_time = current_time

        # ---------------------------
        # DRAW UI
        # ---------------------------
        vis = frame.copy()
        
        # Dark overlay at top for text
        overlay = vis.copy()
        cv2.rectangle(overlay, (0, 0), (CAM_W, 80), (0, 0, 0), -1)
        vis = cv2.addWeighted(overlay, 0.6, vis, 0.4, 0)
        
        # Title
        cv2.putText(vis, "Gesture Music Controller", (10, 25),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Status
        status = music_controller.get_status()
        cv2.putText(vis, status, (10, 55),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 255, 100), 2)
        
        # Last action (show for 2 seconds)
        if last_action and (current_time - action_display_time) < 2.0:
            # Draw action banner
            cv2.rectangle(vis, (0, CAM_H - 50), (CAM_W, CAM_H), (50, 50, 50), -1)
            cv2.putText(vis, last_action, (CAM_W // 2 - 80, CAM_H - 18),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
        
        # Instructions (bottom left)
        hint_y = CAM_H - 60
        cv2.putText(vis, "R/L Up: Prev/Next | Fist/Palm: Play/Pause | 1/2 Fingers: Vol | Cross: Mute", 
                   (5, hint_y), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (180, 180, 180), 1)

        cv2.imshow("Gesture Music Controller", vis)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    holistic.close()
    print("\n👋 Goodbye! Thanks for using Gesture Music Controller.\n")


if __name__ == "__main__":
    main()