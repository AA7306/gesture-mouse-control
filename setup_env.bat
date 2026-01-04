@echo off
echo =====================================
echo    Setting up Gesture Control Env
echo =====================================

REM Step 1: Create virtual environment
python3.10 -m venv gesture_env

REM Step 2: Activate the environment
call gesture_env\Scripts\activate

REM Step 3: Upgrade pip and install dependencies
pip install --upgrade pip
pip install mediapipe opencv-python pyautogui

REM Step 4: Run the app
python hand_control.py
pause
