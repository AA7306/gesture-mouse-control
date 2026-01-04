import mediapipe as mp
import pyautogui
import numpy as np
import cv2
import time
from pynput import keyboard
import threading
import queue
import json
# import sounddevice as sd
# from vosk import Model, KaldiRecognizer

# NOTE:
# Voice control is implemented but disabled by default due to
# hardware limitations on some systems (e.g., Intel Smart Sound mics).
# Keyboard hotkeys remain the reliable control method.


# ============================================================
# GLOBAL STATE
# ============================================================
SCROLL_MODE = False
RUNNING = True

# ============================================================
# HOTKEY CALLBACKS
# ============================================================
def activate_scroll():
    global SCROLL_MODE
    SCROLL_MODE = True
    print("[MODE] Scroll Mode ON")

def deactivate_scroll():
    global SCROLL_MODE
    SCROLL_MODE = False
    print("[MODE] Scroll Mode OFF")

def on_esc_press(key):
    global RUNNING
    if key == keyboard.Key.esc:
        RUNNING = False
        print("[EXIT] ESC pressed")

keyboard.GlobalHotKeys({
    '<ctrl>+<shift>+;': activate_scroll,
    '<ctrl>+<shift>+\\': deactivate_scroll
}).start()

keyboard.Listener(on_press=on_esc_press, daemon=True).start()

# ============================================================
# VOICE CONTROL (PHASE 4 – FIXED FOR INTEL SMART SOUND)
# ============================================================
def voice_listener():
    global RUNNING

    DEVICE_ID = 14          # Intel Smart Sound (WASAPI)
    SAMPLE_RATE = 48000     # REQUIRED by your hardware

    model = Model("vosk-model-small-en-us-0.15")
    recognizer = KaldiRecognizer(model, SAMPLE_RATE)
    recognizer.SetWords(False)

    q = queue.Queue()

    def callback(indata, frames, time_info, status):
        if status:
            print("[VOICE STATUS]", status)
        q.put(bytes(indata))

    with sd.RawInputStream(
        device=DEVICE_ID,
        samplerate=SAMPLE_RATE,
        blocksize=12000,
        dtype='int16',
        channels=1,
        callback=callback
    ):
        print("[VOICE] Listening (say: 'scroll mode on' / 'scroll mode off')")
        while RUNNING:
            data = q.get()
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                text = result.get("text", "").lower()

                if text:
                    print("[VOICE HEARD]:", text)

                if "scroll mode on" in text:
                    activate_scroll()

                elif "scroll mode off" in text:
                    deactivate_scroll()

# NOTE:
# Voice control is implemented but disabled by default due to
# hardware limitations on some systems (e.g., Intel Smart Sound mics).
# Keyboard hotkeys remain the reliable control method.


# threading.Thread(target=voice_listener, daemon=True).start()

# ============================================================
# CONFIG
# ============================================================
CAM_WIDTH, CAM_HEIGHT = 320, 240
SMOOTHING = 0.55

PINCH_CLICK_THRESHOLD = 0.04
DRAG_START_TIME = 0.25

PINCH_SCROLL_THRESHOLD = 0.045
SCROLL_MULTIPLIER = 1500
SCROLL_DEADZONE = 0.015
SCROLL_COOLDOWN = 0.03

SHOW_FEEDBACK = True

# ============================================================
# MEDIAPIPE INIT
# ============================================================
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    max_num_hands=1,
    model_complexity=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

screen_w, screen_h = pyautogui.size()

# ============================================================
# STATE
# ============================================================
smooth_x, smooth_y = 0.0, 0.0
pinching = False
dragging = False
pinch_start = None

scroll_anchor_y = None
last_scroll = 0

def dist(a, b):
    return np.hypot(a.x - b.x, a.y - b.y)

# ============================================================
# CAMERA
# ============================================================
cap = cv2.VideoCapture(0)
cap.set(3, CAM_WIDTH)
cap.set(4, CAM_HEIGHT)

print("""
========================================
 HAND GESTURE MOUSE — PHASE 4 FINAL
========================================
Gesture:
  Index          -> Move cursor
  Middle+Thumb   -> Click / Drag
Scroll Mode:
  Keyboard       -> Ctrl+Shift+; / \\
  Voice          -> "scroll mode on/off"
Safety:
  ESC            -> Exit
========================================
""")

# ============================================================
# MAIN LOOP
# ============================================================
try:
    while RUNNING:
        success, frame = cap.read()
        if not success:
            time.sleep(0.01)
            continue

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)

        if not results.multi_hand_landmarks:
            if dragging:
                pyautogui.mouseUp()
                dragging = False
            pinching = False
            scroll_anchor_y = None

            if SHOW_FEEDBACK:
                cv2.putText(frame, "No hand", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,255), 2)
                cv2.imshow("Gesture Control", frame)
                cv2.waitKey(1)
            continue

        hand = results.multi_hand_landmarks[0]
        mp_draw.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)
        lm = hand.landmark

        index = lm[8]
        middle = lm[12]
        thumb = lm[4]
        wrist = lm[0]

        # ========================================================
        # SCROLL MODE (ISOLATED)
        # ========================================================
        if SCROLL_MODE:
            d = dist(index, thumb)
            if d < PINCH_SCROLL_THRESHOLD:
                if scroll_anchor_y is None:
                    scroll_anchor_y = wrist.y
                else:
                    offset = scroll_anchor_y - wrist.y
                    if abs(offset) > SCROLL_DEADZONE:
                        if time.time() - last_scroll > SCROLL_COOLDOWN:
                            pyautogui.scroll(int(offset * SCROLL_MULTIPLIER))
                            last_scroll = time.time()
            else:
                scroll_anchor_y = None

            if SHOW_FEEDBACK:
                cv2.putText(frame, "SCROLL MODE", (10,30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,255), 2)
                cv2.imshow("Gesture Control", frame)
                cv2.waitKey(1)
            continue

        # ========================================================
        # NORMAL MODE
        # ========================================================
        smooth_x = smooth_x * SMOOTHING + index.x * (1 - SMOOTHING)
        smooth_y = smooth_y * SMOOTHING + index.y * (1 - SMOOTHING)
        pyautogui.moveTo(int(smooth_x * screen_w), int(smooth_y * screen_h))

        d_click = dist(middle, thumb)
        if d_click < PINCH_CLICK_THRESHOLD:
            if not pinching:
                pinching = True
                pinch_start = time.time()
            elif not dragging and time.time() - pinch_start > DRAG_START_TIME:
                pyautogui.mouseDown()
                dragging = True
        else:
            if pinching:
                if dragging:
                    pyautogui.mouseUp()
                    dragging = False
                else:
                    pyautogui.click()
            pinching = False

        if SHOW_FEEDBACK:
            status = "Dragging" if dragging else "Move/Click"
            cv2.putText(frame, status, (10,30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)
            cv2.imshow("Gesture Control", frame)
            cv2.waitKey(1)

except Exception as e:
    print("[ERROR]", e)

finally:
    RUNNING = False
    cap.release()
    cv2.destroyAllWindows()
    print("[SHUTDOWN] Clean exit")
