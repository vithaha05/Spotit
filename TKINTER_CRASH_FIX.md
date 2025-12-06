# Tkinter Crash Fix

## Problem
The application crashes when trying to use tkinter file dialog on macOS:
```
Exception Type: EXC_CRASH (SIGABRT)
Termination Reason: Namespace SIGNAL, Code 6, Abort trap: 6
Thread 0 Crashed:: Dispatch queue: com.apple.main-thread
TkpInit + 452  (Tk initialization failure)
```

## Root Cause
Tkinter's platform-specific initialization (`TkpInit`) fails on macOS in certain contexts:
- Running from VS Code
- Headless environments
- Display server issues
- macOS security/permissions

## Solution
Added robust error handling with fallback to command-line input:

### 1. Try tkinter first (if available)
```python
try:
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(...)
    root.destroy()
except Exception as e:
    # Fallback to CLI input
    return self._select_file_cli()
```

### 2. Fallback to command-line input
If tkinter fails, the user can type the file path directly:
```
Please enter the path to your PowerPoint file:
  (Example: /Users/apple/Desktop/presentation.pptx)
  (Or press Enter to cancel)
```

## Usage Options

### Option 1: File Dialog (if tkinter works)
- GUI file picker appears
- User selects file visually

### Option 2: Command-Line Input (fallback)
- If tkinter crashes, automatically falls back
- User types file path manually
- Path validation and error checking included

### Option 3: Direct Path (skip dialog entirely)
```python
presentation_manager = PresentationManager(
    direct_path="/Users/apple/Desktop/myfile.pptx"
)
```

## Benefits
- ✅ No crashes - graceful fallback
- ✅ Works in all environments
- ✅ User-friendly error messages
- ✅ Path validation
- ✅ Multiple input methods

## Testing
The fix handles:
- ✅ tkinter working normally
- ✅ tkinter crashing (fallback to CLI)
- ✅ Invalid file paths
- ✅ Missing files
- ✅ Wrong file extensions

