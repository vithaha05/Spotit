"""
GestureActions Module
Maps detected gestures to music control actions.
Includes robust detection logic and gesture smoothing.
"""

from music_controller import MusicController
import math
import time
from collections import deque

class GestureActions:
    """
    Coordinates gesture detection with music control actions.
    Maps gestures to music playback controls.
    """
    
    def __init__(self, music_controller: MusicController):
        """
        Initialize gesture actions handler.
        
        Args:
            music_controller: MusicController instance
        """
        self.music_controller = music_controller
        
        # Cooldowns (seconds)
        self.volume_cooldown = 0
        self.play_pause_cooldown = 0
        self.mute_cooldown = 0
        self.track_cooldown = 0
        self.toggle_cooldown = 0
        
        # Gesture Smoothing (Debouncing)
        self.gesture_history = deque(maxlen=5)
        self.required_consecutive_frames = 3
        
    def dist(self, a, b):
        """Calculate distance between two points"""
        return math.hypot(a[0] - b[0], a[1] - b[1])
    
    def get_hand_size(self, hand_landmarks):
        """Estimate hand size (wrist to middle finger knuckle)."""
        WRIST = 0
        MIDDLE_MCP = 9
        return self.dist(
            (hand_landmarks[WRIST].x, hand_landmarks[WRIST].y),
            (hand_landmarks[MIDDLE_MCP].x, hand_landmarks[MIDDLE_MCP].y)
        )

    def detect_hand_above_head(self, hand_landmarks, face_landmarks):
        """Detect if hand is raised above the head (nose level)."""
        if not hand_landmarks or not face_landmarks:
            return False
        WRIST = 0
        NOSE = 1
        return hand_landmarks[WRIST].y < (face_landmarks[NOSE].y - 0.15)

    def detect_open_palm(self, hand_landmarks):
        """
        Detect Open Palm for PAUSE.
        All fingers extended and separated.
        """
        if not hand_landmarks:
            return False
            
        tips = [8, 12, 16, 20]
        pips = [6, 10, 14, 18]
        
        # Check if all fingers are extended
        fingers_extended = all(hand_landmarks[tip].y < hand_landmarks[pip].y for tip, pip in zip(tips, pips))
        
        # Check thumb extended
        thumb_tip = hand_landmarks[4]
        index_base = hand_landmarks[5]
        thumb_extended = self.dist((thumb_tip.x, thumb_tip.y), (index_base.x, index_base.y)) > 0.05
        
        # Check for separation (palm is open)
        width = self.dist(
            (hand_landmarks[8].x, hand_landmarks[8].y),
            (hand_landmarks[20].x, hand_landmarks[20].y)
        )
        hand_size = self.get_hand_size(hand_landmarks)
        is_wide = width > (hand_size * 0.5)
        
        return fingers_extended and thumb_extended and is_wide

    def detect_closed_fist(self, hand_landmarks):
        """
        Detect Closed Fist for PLAY.
        All fingers curled AND thumb curled.
        """
        if not hand_landmarks:
            return False
            
        tips = [8, 12, 16, 20]
        pips = [6, 10, 14, 18]
        
        # Fingers curled (tip below PIP)
        fingers_curled = all(hand_landmarks[tip].y > hand_landmarks[pip].y for tip, pip in zip(tips, pips))
        
        # Thumb curled (tip close to index base)
        thumb_tip = hand_landmarks[4]
        index_base = hand_landmarks[5]
        thumb_curled = self.dist((thumb_tip.x, thumb_tip.y), (index_base.x, index_base.y)) < 0.05
        
        return fingers_curled and thumb_curled

    def detect_index_up(self, hand_landmarks):
        """
        Detect Index Finger Up (☝️) for Volume Up.
        Only index extended, others curled.
        """
        if not hand_landmarks:
            return False
            
        INDEX_TIP = 8
        INDEX_PIP = 6
        MIDDLE_TIP = 12
        MIDDLE_PIP = 10
        RING_TIP = 16
        RING_PIP = 14
        PINKY_TIP = 20
        PINKY_PIP = 18
        
        # Index extended
        index_up = hand_landmarks[INDEX_TIP].y < hand_landmarks[INDEX_PIP].y
        
        # Others curled
        others_down = (hand_landmarks[MIDDLE_TIP].y > hand_landmarks[MIDDLE_PIP].y and
                      hand_landmarks[RING_TIP].y > hand_landmarks[RING_PIP].y and
                      hand_landmarks[PINKY_TIP].y > hand_landmarks[PINKY_PIP].y)
        
        return index_up and others_down

    def detect_peace_sign(self, hand_landmarks):
        """
        Detect Peace Sign (✌️) for Volume Down.
        Index and Middle extended, others curled.
        """
        if not hand_landmarks:
            return False
            
        INDEX_TIP = 8
        INDEX_PIP = 6
        MIDDLE_TIP = 12
        MIDDLE_PIP = 10
        RING_TIP = 16
        RING_PIP = 14
        PINKY_TIP = 20
        PINKY_PIP = 18
        
        # Index and Middle extended
        index_up = hand_landmarks[INDEX_TIP].y < hand_landmarks[INDEX_PIP].y
        middle_up = hand_landmarks[MIDDLE_TIP].y < hand_landmarks[MIDDLE_PIP].y
        
        # Others curled
        others_down = (hand_landmarks[RING_TIP].y > hand_landmarks[RING_PIP].y and
                      hand_landmarks[PINKY_TIP].y > hand_landmarks[PINKY_PIP].y)
        
        return index_up and middle_up and others_down

    def detect_shaka(self, hand_landmarks):
        """
        Detect Shaka Gesture (🤙) for View Toggle.
        Thumb and Pinky extended, middle 3 fingers curled.
        Uses distance-based checks for robustness.
        """
        if not hand_landmarks:
            return False
            
        hand_size = self.get_hand_size(hand_landmarks)
        
        # Landmarks
        WRIST = 0
        THUMB_TIP = 4
        INDEX_MCP = 5
        INDEX_TIP = 8
        MIDDLE_TIP = 12
        RING_TIP = 16
        PINKY_TIP = 20
        
        # 1. Thumb Extended
        # Tip should be far from Index MCP
        thumb_len = self.dist((hand_landmarks[THUMB_TIP].x, hand_landmarks[THUMB_TIP].y), 
                            (hand_landmarks[INDEX_MCP].x, hand_landmarks[INDEX_MCP].y))
        thumb_extended = thumb_len > (hand_size * 0.5)
        
        # 2. Pinky Extended
        # Tip should be far from Wrist
        pinky_len = self.dist((hand_landmarks[PINKY_TIP].x, hand_landmarks[PINKY_TIP].y), 
                            (hand_landmarks[WRIST].x, hand_landmarks[WRIST].y))
        pinky_extended = pinky_len > (hand_size * 1.3)
        
        # 3. Middle 3 Fingers Curled (Not Extended)
        # Tips should be closer to wrist than extended fingers would be
        # Extended middle finger is approx 2.0 * hand_size
        # Curled/Loose is typically < 1.5 * hand_size
        
        def is_curled(tip_idx):
            tip = hand_landmarks[tip_idx]
            wrist = hand_landmarks[WRIST]
            d = self.dist((tip.x, tip.y), (wrist.x, wrist.y))
            return d < (hand_size * 1.6) # Threshold for "not fully extended"
            
        index_curled = is_curled(INDEX_TIP)
        middle_curled = is_curled(MIDDLE_TIP)
        ring_curled = is_curled(RING_TIP)
        
        return thumb_extended and pinky_extended and index_curled and middle_curled and ring_curled

    def detect_rock_sign(self, hand_landmarks):
        """
        Detect Rock Sign (🤘) for Quit.
        Index and Pinky extended. Middle, Ring, Thumb curled.
        """
        if not hand_landmarks:
            return False
            
        hand_size = self.get_hand_size(hand_landmarks)
        WRIST = 0
        THUMB_TIP = 4
        INDEX_TIP = 8
        MIDDLE_TIP = 12
        RING_TIP = 16
        PINKY_TIP = 20
        
        # 1. Index and Pinky Extended
        def is_extended(tip_idx):
            tip = hand_landmarks[tip_idx]
            wrist = hand_landmarks[WRIST]
            d = self.dist((tip.x, tip.y), (wrist.x, wrist.y))
            return d > (hand_size * 1.3)
            
        index_extended = is_extended(INDEX_TIP)
        pinky_extended = is_extended(PINKY_TIP)
        
        # 2. Middle and Ring Curled
        def is_curled(tip_idx):
            tip = hand_landmarks[tip_idx]
            wrist = hand_landmarks[WRIST]
            d = self.dist((tip.x, tip.y), (wrist.x, wrist.y))
            return d < (hand_size * 1.6)
            
        middle_curled = is_curled(MIDDLE_TIP)
        ring_curled = is_curled(RING_TIP)
        
        # 3. Thumb Curled (optional, but helps distinguish from Spider-Man/I-Love-You)
        # Check if thumb tip is close to ring/middle MCPs or just not extended far
        thumb_curled = is_curled(THUMB_TIP)
        
        return index_extended and pinky_extended and middle_curled and ring_curled

    def detect_crossed_arms(self, left_hand, right_hand, pose_landmarks):
        """
        Detect Crossed Arms (Wakanda Style) for Mute.
        Wrists crossed in front of chest.
        """
        if not left_hand or not right_hand or not pose_landmarks:
            return False
            
        # Get wrist positions from pose landmarks (more stable for body pose)
        # 15: Left Wrist, 16: Right Wrist
        # 11: Left Shoulder, 12: Right Shoulder
        
        l_wrist = pose_landmarks[15]
        r_wrist = pose_landmarks[16]
        l_shoulder = pose_landmarks[11]
        r_shoulder = pose_landmarks[12]
        
        # Check if wrists are close to each other
        wrist_dist = self.dist((l_wrist.x, l_wrist.y), (r_wrist.x, r_wrist.y))
        
        # Check if wrists are between shoulders (horizontally) and below chin
        # Simple check: wrists are close and roughly chest height
        
        return wrist_dist < 0.15
    
    def process_gesture(self, gesture, left_hand, right_hand, face_landmarks=None, pose_landmarks=None):
        """
        Process detected gesture and trigger music control actions.
        """
        current_time = time.time()
        detected_gesture = None
        
        # ---------------------------
        # 1. Detect Raw Gesture
        # ---------------------------
        
        # Mute: Crossed Arms (Wakanda)
        if pose_landmarks and self.detect_crossed_arms(left_hand, right_hand, pose_landmarks):
            detected_gesture = "mute"
            
        # Track Control: Hands Above Head
        # Right Hand Up -> Previous Track
        elif face_landmarks and right_hand and self.detect_hand_above_head(right_hand, face_landmarks):
            detected_gesture = "prev_track"
            
        # Left Hand Up -> Next Track
        elif face_landmarks and left_hand and self.detect_hand_above_head(left_hand, face_landmarks):
            detected_gesture = "next_track"

        # Hand-specific gestures
        if not detected_gesture:
            active_hand = left_hand or right_hand
            if active_hand:
                if self.detect_shaka(active_hand):
                    detected_gesture = "toggle_view"
                elif self.detect_rock_sign(active_hand):
                    detected_gesture = "quit"
                elif self.detect_open_palm(active_hand):
                    detected_gesture = "pause"
                elif self.detect_closed_fist(active_hand):
                    detected_gesture = "play"
                elif self.detect_index_up(active_hand):
                    detected_gesture = "volume_up"
                elif self.detect_peace_sign(active_hand):
                    detected_gesture = "volume_down"
        
        # ---------------------------
        # 2. Smoothing / Debouncing
        # ---------------------------
        self.gesture_history.append(detected_gesture)
        
        if len(self.gesture_history) == self.gesture_history.maxlen:
            recent_gestures = list(self.gesture_history)[-self.required_consecutive_frames:]
            if all(g == detected_gesture for g in recent_gestures) and detected_gesture is not None:
                stable_gesture = detected_gesture
            else:
                stable_gesture = None
        else:
            stable_gesture = None

        # ---------------------------
        # 3. Trigger Actions
        # ---------------------------
        if stable_gesture:
            if stable_gesture == "quit":
                # Require 2 seconds hold for quit to prevent accidents
                # We reuse toggle_cooldown or create a new one? 
                # Let's use a specific check in assets.py or handle it here?
                # Actually, process_gesture usually handles cooldowns.
                # But for quit, we want to return "quit" only if held?
                # Or return "quit" and let assets.py handle the timing?
                # Let's return "quit" and let assets.py handle the "Quitting..." UI and delay.
                return "quit"

            elif stable_gesture == "toggle_view":
                if current_time - self.toggle_cooldown > 2.0:
                    self.toggle_cooldown = current_time
                    return "toggle_view"

            elif stable_gesture == "mute":
                if current_time - self.mute_cooldown > 2.0:
                    self.music_controller.mute()
                    self.mute_cooldown = current_time
                    return "mute"
            
            elif stable_gesture == "next_track":
                if current_time - self.track_cooldown > 1.5:
                    self.music_controller.next_track()
                    self.track_cooldown = current_time
                    return "next_track"
            
            elif stable_gesture == "prev_track":
                if current_time - self.track_cooldown > 1.5:
                    self.music_controller.previous_track()
                    self.track_cooldown = current_time
                    return "prev_track"
            
            elif stable_gesture == "play":
                if current_time - self.play_pause_cooldown > 1.0:
                    self.music_controller.play()
                    self.play_pause_cooldown = current_time
                    return "play"
            
            elif stable_gesture == "pause":
                if current_time - self.play_pause_cooldown > 1.0:
                    self.music_controller.pause()
                    self.play_pause_cooldown = current_time
                    return "pause"
            
            elif stable_gesture == "volume_up":
                if current_time - self.volume_cooldown > 0.2:
                    self.music_controller.volume_up(2)
                    self.volume_cooldown = current_time
                    return "volume_up"
            
            elif stable_gesture == "volume_down":
                if current_time - self.volume_cooldown > 0.2:
                    self.music_controller.volume_down(2)
                    self.volume_cooldown = current_time
                    return "volume_down"
        
        return None
