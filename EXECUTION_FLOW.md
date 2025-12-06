# Execution Flow: assets.py

## Complete Step-by-Step Flow After Running `python assets.py`

### Phase 1: Initialization & Setup

```
┌─────────────────────────────────────────────────────────┐
│ 1. Script Starts                                        │
│    • Imports all modules                                │
│    • Loads configuration (camera size, thresholds)      │
│    • Defines helper functions                           │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 2. main() Function Called                               │
│    • Entry point of the application                     │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 3. Optional Telegram Bot Initialization                 │
│    • Tries to initialize Telegram bot                  │
│    • If fails, continues without it (optional)           │
└─────────────────────────────────────────────────────────┘
```

### Phase 2: File Selection

```
┌─────────────────────────────────────────────────────────┐
│ 4. Display Welcome Message                              │
│    • Prints "Presentation Control System..."            │
│    • Shows instructions                                │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 5. Create PresentationManager Instance                 │
│    • presentation_manager = PresentationManager()        │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 6. Open File Dialog                                     │
│    • Tkinter file dialog appears                        │
│    • User browses and selects .ppt or .pptx file        │
│    • File path stored in presentation_manager            │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 7. File Selection Check                                 │
│    • If no file selected → Exit program                 │
│    • If file selected → Continue                        │
└─────────────────────────────────────────────────────────┘
```

### Phase 3: Presentation Opening

```
┌─────────────────────────────────────────────────────────┐
│ 8. Open Presentation File                               │
│    • Calls presentation_manager.open_presentation()      │
│    • Uses platform-specific command:                    │
│      - macOS: 'open' command                            │
│      - Windows: 'start' command                        │
│      - Linux: 'xdg-open' command                        │
│    • Opens with default PowerPoint application          │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 9. Wait for Application to Open                        │
│    • Sleeps for 2 seconds                              │
│    • Allows PowerPoint/Keynote to fully load             │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 10. Window Positioning Instructions                     │
│     • Prints instructions to position window            │
│     • Shows keyboard shortcuts for window management     │
│     • Waits 3 seconds for user to position window       │
└─────────────────────────────────────────────────────────┘
```

### Phase 4: Module Initialization

```
┌─────────────────────────────────────────────────────────┐
│ 11. Initialize PresentationController                   │
│     • Creates controller for slide navigation           │
│     • Sets up state management                          │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 12. Initialize AirWritingEngine                        │
│     • Creates drawing canvas (full screen size)          │
│     • Sets up color palette                             │
│     • Initializes drawing modes                         │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 13. Initialize GestureActions                           │
│     • Links controller and writing engine               │
│     • Sets up gesture-to-action mapping                 │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 14. Initialize MediaPipe Holistic                       │
│     • Sets up hand and face detection                   │
│     • Configures detection confidence (0.6)              │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 15. Initialize Camera                                  │
│     • Opens camera (VideoCapture(0))                    │
│     • Sets resolution to 640x480                        │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 16. Initialize Data Structures                          │
│     • frame_count = 0                                   │
│     • nose_history = deque (for nod detection)           │
│     • gesture_history = deque (for stabilization)       │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 17. Display Control Instructions                        │
│     • Prints all available gestures and actions         │
│     • Shows "Press 'q' to quit"                         │
└─────────────────────────────────────────────────────────┘
```

### Phase 5: Main Loop (Continuous)

```
┌─────────────────────────────────────────────────────────┐
│ 18. START MAIN LOOP                                     │
│     while True:                                          │
│     (This loop runs continuously until 'q' is pressed) │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 19. Capture Camera Frame                                │
│     • cap.read() → Gets frame from camera               │
│     • If no frame → Break loop and exit                 │
│     • Flip frame horizontally (mirror effect)           │
│     • Convert BGR to RGB for MediaPipe                  │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 20. Process with MediaPipe                              │
│     • holistic.process(rgb) → Detects landmarks        │
│     • Gets face, left hand, right hand landmarks        │
│     • Only processes every N frames (optimization)      │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 21. Face Detection                                      │
│     • If face detected:                                 │
│       - Extract face landmarks                          │
│       - Track nose position (for nod detection)         │
│       - Check mouth gap (for "tongue" gesture)           │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 22. Nod/Blink Detection                                  │
│     • Analyze nose history                             │
│     • Detect quick downward movement → "blink"          │
│     • Detect slow movement → "nod"                      │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 23. Hand Detection                                      │
│     • Extract left and right hand landmarks             │
│     • Draw hand mesh on frame (visual feedback)         │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 24. Gesture Classification                              │
│     Checks for various gestures:                        │
│     • "idea" - Index finger up                          │
│     • "thinking" - Finger near mouth                    │
│     • "rubbing" - Hands joined together                 │
│     • "hands_up" - Hands above head                     │
│     • "tuff" - Weighing hands gesture                  │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 25. Swipe Detection                                     │
│     • gesture_actions.detect_swipe(hand)                │
│     • Tracks hand movement over time                    │
│     • If swipe_right → next_slide()                      │
│     • If swipe_left → previous_slide()                  │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 26. Gesture Stabilization                               │
│     • Add current gesture to history                    │
│     • Use Counter to find most common gesture           │
│     • Reduces flickering (smooths detection)            │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 27. Process Gesture Actions                             │
│     • gesture_actions.process_gesture()                 │
│     • Handles:                                           │
│       - Rubbing → Toggle presentation                    │
│       - Pinch → Change color                             │
│       - Index+Middle → Erase mode                        │
│       - Index pointing → Laser pointer                  │
│       - Circle motion → Highlight                        │
│       - One finger → Drawing                            │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 28. Capture Presentation Screen                         │
│     • presentation_manager.capture_presentation_screen()│
│     • Screenshots right half of screen                  │
│     • Converts to OpenCV format (BGR)                    │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 29. Get Air Writing Overlay                              │
│     • air_writing_engine.get_canvas_overlay()           │
│     • Gets current drawing canvas                        │
│     • Includes laser pointer if active                   │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 30. Blend Overlay on Presentation                       │
│     • Resize presentation to display size               │
│     • Extract alpha channel from overlay                │
│     • Blend overlay onto presentation                    │
│     • Creates final presentation_with_overlay            │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 31. Prepare Camera Panel                                │
│     • Add gesture text overlay                          │
│     • Add writing status                                │
│     • Add mode indicator                                │
│     • Add presentation status                           │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 32. Combine Panels                                      │
│     • Create combined image (1600x720)                   │
│     • Place camera on left (640x480)                    │
│     • Place presentation on right (960x720)             │
│     • Draw separator line                               │
│     • Add labels                                         │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 33. Display Combined Window                            │
│     • cv2.imshow("Presentation Control...")             │
│     • Shows camera + presentation side by side          │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 34. Check for Quit                                      │
│     • cv2.waitKey(1) → Check for 'q' key                │
│     • If 'q' pressed → Break loop                       │
│     • Otherwise → Go back to step 19 (continue loop)     │
└─────────────────────────────────────────────────────────┘
```

### Phase 6: Cleanup & Exit

```
┌─────────────────────────────────────────────────────────┐
│ 35. Release Resources                                   │
│     • cap.release() → Close camera                       │
│     • cv2.destroyAllWindows() → Close OpenCV windows   │
│     • holistic.close() → Close MediaPipe                 │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 36. Program Exits                                       │
│     • Returns from main()                               │
│     • Script ends                                        │
└─────────────────────────────────────────────────────────┘
```

## Visual Flow Summary

```
START
  ↓
Initialize Modules
  ↓
Select PPT File (Dialog)
  ↓
Open Presentation
  ↓
Wait for Window Positioning
  ↓
Initialize Camera & MediaPipe
  ↓
┌─────────────────────────┐
│   MAIN LOOP (Continuous)│
│                         │
│  Capture Frame          │
│  ↓                      │
│  Detect Gestures        │
│  ↓                      │
│  Process Actions        │
│  ↓                      │
│  Capture Presentation   │
│  ↓                      │
│  Blend Overlay          │
│  ↓                      │
│  Display Combined       │
│  ↓                      │
│  Check for 'q'          │
│  ↓                      │
│  (Loop back or exit)    │
└─────────────────────────┘
  ↓
Cleanup & Exit
  ↓
END
```

## Key Points

1. **One-time Setup**: File selection and module initialization happen once at startup
2. **Continuous Loop**: Main processing loop runs ~30 FPS (depending on camera)
3. **Real-time Processing**: Each frame goes through detection → action → display pipeline
4. **Gesture Stabilization**: Uses history buffer to smooth out detections
5. **Screen Capture**: Captures presentation region every frame for display
6. **Overlay Blending**: Air writing is blended on top of presentation in real-time

## Performance Considerations

- MediaPipe processing happens every frame (PROCESS_EVERY_N_FRAMES = 1)
- Screen capture adds slight overhead (~10-20ms per frame)
- Gesture history prevents rapid-fire actions (cooldown system)
- Display updates at camera frame rate (typically 30 FPS)

