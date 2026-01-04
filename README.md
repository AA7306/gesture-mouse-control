#  Hand Gesture Mouse Control

A real-time hand gesture–based mouse control system built with Python and computer vision.  
Control your cursor, click, drag, and scroll using hand gestures captured via webcam.

---

##  Features
- Cursor movement using index finger
- Click and drag using middle finger + thumb pinch
- Dedicated scroll mode (gesture-isolated)
- Keyboard hotkeys for mode switching
- Optional voice control (implemented but disabled by default)
- Smooth cursor movement with damping
- Safety exit using ESC key

---

##  Gesture Controls
| Action | Gesture |
|------|--------|
| Move Cursor | Index finger |
| Click | Middle finger + thumb pinch |
| Drag | Hold middle finger + thumb pinch |
| Scroll | Scroll mode + wrist movement |

---

##  Keyboard Shortcuts
- **Ctrl + Shift + ;** → Scroll Mode ON  
- **Ctrl + Shift + \\** → Scroll Mode OFF  
- **ESC** → Exit application  

---

##  Tech Stack
- Python
- MediaPipe
- OpenCV
- PyAutoGUI
- NumPy
- pynput

---

## 📦 Installation

### Option 1: Using setup script (Recommended on Windows)
```bat
setup_env.bat
```
## Notes  
- Works best in good lighting conditions  
- Designed for single-hand detection  
- Voice control is disabled by default due to microphone driver limitations on some systems (e.g., Intel Smart Sound)

## Future Improvements  
- Right-click gesture support  
- Calibration UI  
- Multi-monitor support  
- Gesture customization via config file

## Author  
**Alen Alex Paul**

