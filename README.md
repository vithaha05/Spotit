# 🎵 Gesture Music Controller

Control your music with hand gestures! Use natural hand movements to play/pause, skip tracks, and adjust volume on any music player.

## Features

| Gesture | Action |
|---------|--------|
| **Closed Fist** ✊ | Play ▶ |
| **Open Palm** ✋ | Pause ⏸ |
| **Right Hand Up** 🙋‍♂️ | Previous Track ⏮ |
| **Left Hand Up** 🙋‍♀️ | Next Track ⏭ |
| **Index Finger Up** ☝️ | Volume Up 🔊 |
| **Peace Sign** ✌️ | Volume Down 🔉 |
| **Crossed Arms** 🙅 | Mute/Unmute 🔇 |

## Installation

```bash
pip install opencv-python mediapipe numpy pyautogui
```

## Usage

1. **Open your music app** (Spotify, Apple Music, YouTube, etc.)

2. **Run the controller:**
   ```bash
   python assets.py
   ```

3. **Use gestures** in front of your camera to control playback!

4. Press **'q'** to quit.

## How It Works

- Uses **MediaPipe Holistic** for real-time hand and pose tracking
- Detects gestures and sends **AppleScript/System** commands
- Works with **Spotify, Apple Music, and System Volume**

## Requirements

- Python 3.8+
- Webcam
- macOS (optimized for AppleScript control)

## Files

| File | Purpose |
|------|---------|
| `assets.py` | Main application with camera and gesture loop |
| `music_controller.py` | Sends media key commands |
| `gesture_actions.py` | Maps gestures to actions |

## Tips

- Ensure good lighting for better hand detection
- Keep your hand within the camera frame
- Make gestures clearly and deliberately
- Allow ~0.5 seconds between actions

## License

MIT
