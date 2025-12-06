# Architecture Documentation

## System Overview

The Presentation Control System extends the original gesture detection architecture with new modules while preserving the existing MediaPipe Holistic detection pipeline.

## Module Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    assets.py (Main)                     │
│  • MediaPipe Holistic initialization                    │
│  • Camera capture loop                                  │
│  • Gesture detection (preserved from original)          │
│  • Module coordination                                  │
└──────────────┬──────────────────────────────────────────┘
               │
       ┌───────┴────────┐
       │                 │
┌──────▼──────┐  ┌──────▼──────────┐
│ GestureActions│  │ PresentationCtrl│
│               │  │                │
│ • Swipe det. │  │ • Slide nav.   │
│ • Pinch det. │  │ • F5/ESC       │
│ • Finger st. │  │ • Cooldowns    │
└──────┬───────┘  └────────────────┘
       │
       │ uses
       │
┌──────▼──────────┐
│ AirWritingEngine│
│                 │
│ • Canvas mgmt   │
│ • Stroke render │
│ • Color cycling │
│ • Circle detect │
│ • Laser pointer │
└─────────────────┘
```

## Integration Flow

### 1. Initialization (`main()`)
```python
# Create controller instances
presentation_controller = PresentationController()
air_writing_engine = AirWritingEngine(SCREEN_WIDTH, SCREEN_HEIGHT)
gesture_actions = GestureActions(presentation_controller, air_writing_engine)
```

### 2. Frame Processing Loop
```
For each frame:
  1. Capture frame from camera
  2. Process with MediaPipe Holistic
  3. Detect gestures (existing logic preserved)
  4. Detect swipes (new - independent)
  5. Process gesture actions (new)
  6. Render air writing overlay
  7. Display combined view
```

### 3. Gesture → Action Mapping

| Gesture | Detection | Action |
|---------|-----------|--------|
| Swipe Right | `detect_swipe()` | `next_slide()` |
| Swipe Left | `detect_swipe()` | `previous_slide()` |
| Rubbing Hands | Existing logic | `toggle_presentation()` |
| One Finger | Index tip < PIP | `start_drawing()` |
| Pinch | Thumb-Index distance | `change_color()` |
| Index+Middle | Both extended | `set_mode(ERASE)` |
| Circle Motion | Circle detection | `draw_highlight_region()` |
| Index Pointing | Index up, middle down | `update_laser_pointer()` |

## Key Design Decisions

### 1. Preserved Architecture
- ✅ MediaPipe Holistic detection unchanged
- ✅ Gesture detection logic intact
- ✅ Frame loop structure identical
- ✅ Helper functions preserved

### 2. Modular Extensions
- New modules are self-contained
- Clear interfaces between modules
- Easy to test independently
- Can be extended without modifying core

### 3. Separation of Concerns
- **GestureActions**: Maps gestures to actions
- **PresentationController**: Handles slide control
- **AirWritingEngine**: Manages drawing state
- **Main loop**: Coordinates everything

## Performance Considerations

### Current Optimizations
1. **Frame Skipping**: `PROCESS_EVERY_N_FRAMES` reduces processing load
2. **Gesture History**: Stabilizes detections, reduces flicker
3. **Action Cooldowns**: Prevents rapid-fire triggers
4. **Efficient Rendering**: Canvas updates only when drawing

### Suggested Improvements

#### 1. Multi-threading
```python
# Separate threads for:
- Gesture detection (CPU-intensive)
- Rendering (I/O-bound)
- Action execution (blocking operations)
```

#### 2. Kalman Filtering
```python
# Smooth finger tracking
from filterpy.kalman import KalmanFilter

kf = KalmanFilter(dim_x=4, dim_z=2)
# Predict and update finger positions
```

#### 3. Adaptive Thresholds
```python
# Adjust thresholds based on:
- Lighting conditions
- Hand distance from camera
- Background complexity
```

#### 4. GPU Acceleration
```python
# Use MediaPipe GPU backend
mp_holistic = mp.solutions.holistic.Holistic(
    static_image_mode=False,
    model_complexity=2,
    enable_segmentation=False,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)
# Enable GPU: requires specific setup
```

## Code Snippets

### Swipe Detection
```python
def detect_swipe(self, hand_landmarks):
    # Track wrist position over time
    current_pos = (hand_landmarks[WRIST].x, hand_landmarks[WRIST].y)
    self.swipe_history.append(current_pos)
    
    # Calculate horizontal movement
    dx = end_pos[0] - start_pos[0]
    if abs(dx) > threshold:
        return 'swipe_right' if dx > 0 else 'swipe_left'
```

### Air Writing Update
```python
def update_drawing(self, point):
    canvas_point = self._normalized_to_canvas(point)
    if self.current_mode == DrawingMode.DRAW:
        cv2.line(self.canvas, self.last_point, canvas_point, 
                self.get_current_color(), self.stroke_thickness)
```

### Circle Detection
```python
def detect_circle_motion(self, point):
    # Calculate center and radius of recent points
    center = (avg_x, avg_y)
    avg_radius = mean(distances)
    
    # Check if motion forms circle (low variance)
    if radius_variance < threshold:
        return center, avg_radius
```

## Extension Points

### Adding New Gestures
1. Add detection in main loop
2. Create action method in appropriate module
3. Map gesture to action in `GestureActions`

### Custom Drawing Modes
1. Add enum value to `DrawingMode`
2. Implement logic in `AirWritingEngine.update_drawing()`
3. Add gesture detection in `GestureActions`

### New Presentation Controls
1. Add method to `PresentationController`
2. Map gesture in `GestureActions.process_gesture()`
3. Update documentation

## Testing Strategy

### Unit Tests
- Test each module independently
- Mock MediaPipe landmarks
- Verify action triggers

### Integration Tests
- Test gesture → action flow
- Verify module coordination
- Check edge cases

### Performance Tests
- Measure frame processing time
- Check memory usage
- Profile bottlenecks

## Future Enhancements

1. **Voice Commands**: Combine with speech recognition
2. **Multi-hand Support**: Track both hands independently
3. **Gesture Macros**: Record and replay gesture sequences
4. **Cloud Sync**: Save drawings to cloud
5. **AR Overlay**: Use ARKit/ARCore for better tracking

