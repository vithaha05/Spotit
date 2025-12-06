import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import platform

class UIManager:
    def __init__(self):
        self.font_path = self._get_system_font()
        self.large_font_size = 60
        self.medium_font_size = 30
        self.small_font_size = 18
        
        # Load Fonts
        try:
            self.font_large = ImageFont.truetype(self.font_path, self.large_font_size)
            self.font_medium = ImageFont.truetype(self.font_path, self.medium_font_size)
            self.font_small = ImageFont.truetype(self.font_path, self.small_font_size)
        except IOError:
            self.font_large = ImageFont.load_default()
            self.font_medium = ImageFont.load_default()
            self.font_small = ImageFont.load_default()

    def _get_system_font(self):
        system = platform.system()
        if system == "Darwin": # macOS
            return "/System/Library/Fonts/Supplemental/Arial.ttf"
        elif system == "Windows":
            return "arial.ttf"
        else:
            return "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

    def _draw_glass_rect(self, draw, xy, color, alpha=150, radius=15):
        """Draw a rounded rectangle with alpha blending (simulated)."""
        # PIL doesn't support alpha on draw.rectangle directly on RGB images easily without layers
        # For simplicity in this real-time app, we'll just draw a semi-transparent box
        # To do this properly in PIL, we need a separate layer
        pass 
        # Actually, for performance, we will handle alpha blending in OpenCV before passing to PIL
        # or just use solid colors with PIL for text and OpenCV for shapes.
        # Let's stick to OpenCV for shapes (faster) and PIL for text.

    def overlay_text(self, img, text, pos, font, color=(255, 255, 255)):
        draw = ImageDraw.Draw(img)
        draw.text(pos, text, font=font, fill=color)

    def draw_overlay(self, frame, status, last_action, mode, action_time, current_time):
        # Convert to PIL
        img_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(img_pil, "RGBA")
        
        h, w = frame.shape[:2]
        
        # ---------------------------
        # Header (Glass Effect)
        # ---------------------------
        # Draw semi-transparent header using PIL
        header_h = 80
        draw.rectangle([(0, 0), (w, header_h)], fill=(0, 0, 0, 180))
        
        # Title
        draw.text((20, 15), "Gesture Music Controller", font=self.font_medium, fill=(255, 255, 255, 255))
        
        # Status (with Emoji!)
        # Map status to emoji if possible, or just use the text
        # The status from music_controller is like "> Playing" or "|| Paused"
        # Let's beautify it
        status_text = status.replace(">", "▶").replace("||", "⏸")
        status_color = (100, 255, 100, 255) if "Playing" in status else (255, 200, 100, 255)
        draw.text((20, 50), status_text, font=self.font_small, fill=status_color)

        # ---------------------------
        # Visual Feedback (Center Flash)
        # ---------------------------
        if last_action and (current_time - action_time) < 1.5:
            # Fade out effect
            elapsed = current_time - action_time
            alpha = int(255 * (1 - (elapsed / 1.5)))
            
            # Center text
            text = last_action
            # Calculate text size
            bbox = draw.textbbox((0, 0), text, font=self.font_large)
            text_w = bbox[2] - bbox[0]
            text_h = bbox[3] - bbox[1]
            
            x = (w - text_w) // 2
            y = (h - text_h) // 2
            
            # Draw glow/background
            padding = 20
            draw.rounded_rectangle(
                [(x - padding, y - padding), (x + text_w + padding, y + text_h + padding)],
                radius=20,
                fill=(0, 0, 0, alpha // 2)
            )
            
            draw.text((x, y), text, font=self.font_large, fill=(255, 255, 255, alpha))

        # ---------------------------
        # Footer (Instructions)
        # ---------------------------
        footer_h = 40
        draw.rectangle([(0, h - footer_h), (w, h)], fill=(0, 0, 0, 180))
        
        instructions = "👆 Point: Vol | ✊ Fist: Play | ✋ Palm: Pause | 🤙 Shaka: View | 🤘 Rock: Quit"
        draw.text((10, h - 30), instructions, font=self.font_small, fill=(200, 200, 200, 255))

        # Convert back to OpenCV
        return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

    def draw_mini_mode(self, status, last_action, action_time, current_time):
        w, h = 400, 150
        img_pil = Image.new('RGBA', (w, h), (20, 20, 20, 255))
        draw = ImageDraw.Draw(img_pil)
        
        # Border
        draw.rectangle([(0, 0), (w-1, h-1)], outline=(50, 50, 50), width=2)
        
        # Title
        draw.text((15, 15), "Spotit Mini", font=self.font_small, fill=(100, 100, 100, 255))
        
        # Main Status (Large)
        status_text = status.replace(">", "▶").replace("||", "⏸")
        draw.text((15, 45), status_text, font=self.font_medium, fill=(255, 255, 255, 255))
        
        # Last Action Feedback
        if last_action and (current_time - action_time) < 2.0:
            draw.text((15, 90), f"Action: {last_action}", font=self.font_small, fill=(0, 255, 255, 255))
        else:
            draw.text((15, 90), "Listening for gestures...", font=self.font_small, fill=(80, 80, 80, 255))
            
        return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
