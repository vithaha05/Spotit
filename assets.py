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
from ui_manager import UIManager

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

mp_holistic = mp.solutions.holistic
mp_drawing = mp.solutions.drawing_utils

L_EYE = {"outer": 33, "inner": 133, "top": 159, "bottom": 145}
R_EYE = {"outer": 362, "inner": 263, "top": 386, "bottom": 374}
NOSE = 1
INDEX_TIP = 8
INDEX_PIP = 6
WRIST = 0

class GestureApp:
    def __init__(self):
        self.music_controller = MusicController()
        self.gesture_actions = GestureActions(self.music_controller)
        self.ui_manager = UIManager()
        
        # Initialize MediaPipe Holistic
        self.holistic = mp_holistic.Holistic(
            min_detection_confidence=0.6,
            min_tracking_confidence=0.6
        )
        
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, CAM_W)
        self.cap.set(4, CAM_H)
        
        self.frame_count = 0
        self.nose_history = deque(maxlen=NOD_HISTORY)
        self.gesture_history = deque(maxlen=GESTURE_HISTORY_LEN)
        self.last_action = None
        self.action_display_time = 0
        
        # Quit Timer
        self.quit_hold_start = 0
        
        # View Mode: 'FULL' or 'MINI'
        self.view_mode = 'FULL'
        self.window_name = "Gesture Music Controller"

    def print_controls(self):
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
        print("  • Shaka 🤙         → Toggle View 🔄")
        print("  • Rock 🤘          → Quit (Hold 2s) 🚪")
        print("\nApp Controls:")
        print("  • Press 'v'        → Toggle View (Full/Mini)")
        print("  • Press 'q'        → Quit")
        print("=" * 60)
        print("\n🎧 Open your music app (Spotify, Apple Music, etc.)")
        print("📷 Starting camera for gesture detection...\n")

    def run(self):
        self.print_controls()
        
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            if self.frame_count % PROCESS_EVERY_N_FRAMES == 0:
                results = self.holistic.process(rgb)
            self.frame_count += 1

            gesture = "neutral"
            face = None
            current_time = time.time()

            # --------------------------------------------
            # FACE DETECTION
            # --------------------------------------------
            if results.face_landmarks:
                face = results.face_landmarks.landmark
                self.nose_history.append(face[NOSE].y)

            # HANDS
            lh = results.left_hand_landmarks.landmark if results.left_hand_landmarks else None
            rh = results.right_hand_landmarks.landmark if results.right_hand_landmarks else None

            # Draw hand mesh (Only in FULL mode)
            if self.view_mode == 'FULL':
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
            self.gesture_history.append(gesture)
            chosen = Counter(self.gesture_history).most_common(1)[0][0]

            # ---------------------------
            # Process gestures
            # ---------------------------
            action = self.gesture_actions.process_gesture(chosen, lh, rh, face, results.pose_landmarks.landmark if results.pose_landmarks else None)
            
            # Quit Logic (Hold Rock for 2s)
            if action == "quit":
                if self.quit_hold_start == 0:
                    self.quit_hold_start = current_time
                
                hold_duration = current_time - self.quit_hold_start
                self.last_action = f"🚪 Quitting in {2.0 - hold_duration:.1f}s..."
                self.action_display_time = current_time
                
                if hold_duration > 2.0:
                    print("👋 Quit Gesture Detected!")
                    break
            else:
                self.quit_hold_start = 0 # Reset if gesture lost
                
                if action:
                    if action == "toggle_view":
                        self.view_mode = 'MINI' if self.view_mode == 'FULL' else 'FULL'
                        cv2.destroyWindow(self.window_name)
                        self.last_action = "🔄 View Toggled"
                        self.action_display_time = current_time
                    else:
                        action_map = {
                            "play_pause": "▶⏸ Play/Pause",
                            "volume_up": "🔊 Vol Up",
                            "volume_down": "🔉 Vol Down",
                            "mute": "🔇 Mute Toggle",
                            "next_track": "⏭ Next",
                            "prev_track": "⏮ Previous"
                        }
                        self.last_action = action_map.get(action, action)
                        self.action_display_time = current_time

            # ---------------------------
            # DRAW UI (Using UIManager)
            # ---------------------------
            status = self.music_controller.get_status()
            
            if self.view_mode == 'FULL':
                display_img = self.ui_manager.draw_overlay(frame, status, self.last_action, self.view_mode, self.action_display_time, current_time)
            else:
                display_img = self.ui_manager.draw_mini_mode(status, self.last_action, self.action_display_time, current_time)

            cv2.imshow(self.window_name, display_img)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('v'):
                self.view_mode = 'MINI' if self.view_mode == 'FULL' else 'FULL'
                # Resize window when switching modes to fit content
                cv2.destroyWindow(self.window_name) 

        self.cap.release()
        cv2.destroyAllWindows()
        self.holistic.close()
        print("\n👋 Goodbye! Thanks for using Gesture Music Controller.\n")

if __name__ == "__main__":
    app = GestureApp()
    app.run()