# Changelog

## Latest Update: PPT File Selection & Presentation Display

### New Features

1. **PPT File Selection**
   - File dialog appears at startup to select PowerPoint presentation (.ppt or .pptx)
   - Cross-platform support (macOS, Windows, Linux)
   - Opens presentation with default application

2. **Presentation Display**
   - Presentation shown on the right side of the control window
   - Real-time screen capture of presentation region
   - Air writing overlay blended on top of presentation
   - Camera feed displayed on the left side

3. **Presentation Manager Module**
   - `PresentationManager` class handles file selection and window management
   - Automatic presentation opening
   - Screen region capture for display

### Updated Files

- `assets.py`: Added file selection dialog, presentation display integration
- `presentation_manager.py`: New module for PPT file handling
- `requirements.txt`: Added Pillow dependency

### Usage Flow

1. **Start Application**: Run `python assets.py`
2. **Select PPT File**: File dialog appears - choose your presentation
3. **Position Window**: Presentation opens - position it on right side of screen
4. **Control**: All gestures now control the selected presentation

### Display Layout

```
┌──────────────┬──────────────────────┐
│              │                      │
│   Camera     │   Presentation       │
│   Feed       │   (with overlay)     │
│              │                      │
│              │                      │
└──────────────┴──────────────────────┘
```

### Gesture Controls (Applied to Selected Presentation)

- **Swipe Right** → Next slide
- **Swipe Left** → Previous slide
- **Rubbing Hands** → Start/End presentation (F5/ESC)
- **One Finger** → Draw on presentation
- **Pinch** → Change drawing color
- **Index + Middle** → Erase mode
- **Circle Motion** → Auto-highlight
- **Index Pointing** → Laser pointer

### Technical Details

- Screen capture uses `pyautogui.screenshot()` for right half of screen
- Air writing overlay is blended using alpha channel
- Presentation region: Right half of screen (configurable)
- Display size: 960x720 pixels (adjustable via `PRESENTATION_W`, `PRESENTATION_H`)

### Notes

- Window positioning may require manual adjustment on some systems
- Screen capture works best when presentation is in right half of screen
- Air writing coordinates map to full screen but display on presentation region

