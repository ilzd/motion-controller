"""Trigger implementations"""

# Import to register triggers
from src.recognition.triggers.hand_raise_trigger import HandRaiseTrigger
from src.recognition.triggers.body_lean_trigger import BodyLeanTrigger
from src.recognition.triggers.pose_hold_trigger import PoseHoldTrigger
from src.recognition.triggers.hand_gesture_trigger import HandGestureTrigger
from src.recognition.triggers.arm_stretch_trigger import ArmStretchTrigger
from src.recognition.triggers.leg_raise_trigger import LegRaiseTrigger
from src.recognition.triggers.motion_speed_trigger import MotionSpeedTrigger
from src.recognition.triggers.pointing_gesture_trigger import PointingGestureTrigger

__all__ = [
    "HandRaiseTrigger", 
    "BodyLeanTrigger", 
    "PoseHoldTrigger", 
    "HandGestureTrigger",
    "ArmStretchTrigger",
    "LegRaiseTrigger",
    "MotionSpeedTrigger",
    "PointingGestureTrigger"
]


