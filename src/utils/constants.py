"""Application-wide constants"""

# Camera defaults
DEFAULT_CAMERA_ID = 0
DEFAULT_CAMERA_RESOLUTION = (640, 480)
DEFAULT_CAMERA_FPS = 30

# MediaPipe defaults
DEFAULT_MODEL_COMPLEXITY = 0  # 0=fastest, 1=balanced, 2=most accurate
DEFAULT_MIN_DETECTION_CONFIDENCE = 0.5
DEFAULT_MIN_TRACKING_CONFIDENCE = 0.5

# Trigger defaults
DEFAULT_HAND_RAISE_THRESHOLD = 0.2
DEFAULT_BODY_LEAN_THRESHOLD = 15.0
MIN_LANDMARK_VISIBILITY = 0.5  # Minimum visibility score for reliable detection

# Gamepad defaults
GAMEPAD_STICK_MAX_VALUE = 32767  # Maximum value for analog sticks
GAMEPAD_TRIGGER_MAX_VALUE = 255  # Maximum value for triggers

# Processing defaults
PROCESSING_TIMER_INTERVAL_MS = 33  # ~30 FPS
GESTURE_MONITOR_UPDATE_INTERVAL = 2  # Update every N frames
MAX_FRAME_SKIP_COUNT = 10  # Warn if skipping too many frames

# Debouncing
DEFAULT_DEBOUNCE_FRAMES = 2  # Require N consecutive frames for state change

