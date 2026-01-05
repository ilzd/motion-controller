"""Trigger implementations"""

# Import to register triggers
from src.recognition.triggers.hand_raise_trigger import HandRaiseTrigger
from src.recognition.triggers.body_lean_trigger import BodyLeanTrigger
from src.recognition.triggers.pose_hold_trigger import PoseHoldTrigger
from src.recognition.triggers.hand_gesture_trigger import HandGestureTrigger

__all__ = ["HandRaiseTrigger", "BodyLeanTrigger", "PoseHoldTrigger", "HandGestureTrigger"]


