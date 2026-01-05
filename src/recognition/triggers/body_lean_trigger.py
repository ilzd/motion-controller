"""Body lean trigger - detects when body leans in a direction"""

from typing import Dict, Any
import numpy as np
from src.recognition.base_trigger import BaseTrigger
from src.recognition.trigger_registry import TriggerRegistry
from src.detection.landmark_utils import (
    get_landmark_position,
    get_landmark_visibility,
    LandmarkIndex
)
from src.utils.math_utils import calculate_lean_angle
from src.utils.constants import DEFAULT_BODY_LEAN_THRESHOLD, MIN_LANDMARK_VISIBILITY


@TriggerRegistry.register("body_lean")
class BodyLeanTrigger(BaseTrigger):
    """Detects when body leans in a specific direction"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize body lean trigger.
        
        Config parameters:
            direction: "left", "right", "forward", or "back"
            threshold: Angle threshold in degrees (default 15)
        """
        super().__init__(config)
        self.direction = self.get_config_param("direction", "forward").lower()
        self.threshold = self.get_config_param("threshold", DEFAULT_BODY_LEAN_THRESHOLD)
        
    def detect(self, landmarks: object, frame_data: Dict[str, Any]) -> bool:
        """Detect if body is leaning in specified direction"""
        if landmarks is None:
            self.is_active = False
            self.current_value = 0.0
            return False
        
        # Get key body points
        left_shoulder = get_landmark_position(landmarks, LandmarkIndex.LEFT_SHOULDER)
        right_shoulder = get_landmark_position(landmarks, LandmarkIndex.RIGHT_SHOULDER)
        left_hip = get_landmark_position(landmarks, LandmarkIndex.LEFT_HIP)
        right_hip = get_landmark_position(landmarks, LandmarkIndex.RIGHT_HIP)
        
        if None in [left_shoulder, right_shoulder, left_hip, right_hip]:
            self.is_active = False
            self.current_value = 0.0
            return False
        
        # Check landmark visibility for reliable detection
        if (get_landmark_visibility(landmarks, LandmarkIndex.LEFT_SHOULDER) or 0) < MIN_LANDMARK_VISIBILITY:
            self.is_active = False
            self.current_value = 0.0
            return False
        if (get_landmark_visibility(landmarks, LandmarkIndex.RIGHT_SHOULDER) or 0) < MIN_LANDMARK_VISIBILITY:
            self.is_active = False
            self.current_value = 0.0
            return False
        if (get_landmark_visibility(landmarks, LandmarkIndex.LEFT_HIP) or 0) < MIN_LANDMARK_VISIBILITY:
            self.is_active = False
            self.current_value = 0.0
            return False
        if (get_landmark_visibility(landmarks, LandmarkIndex.RIGHT_HIP) or 0) < MIN_LANDMARK_VISIBILITY:
            self.is_active = False
            self.current_value = 0.0
            return False
        
        # Calculate midpoints
        shoulder_mid = (
            (left_shoulder[0] + right_shoulder[0]) / 2,
            (left_shoulder[1] + right_shoulder[1]) / 2
        )
        hip_mid = (
            (left_hip[0] + right_hip[0]) / 2,
            (left_hip[1] + right_hip[1]) / 2
        )
        
        result = False
        
        if self.direction == "left" or self.direction == "right":
            # Calculate lean angle (positive = right, negative = left)
            lean_angle = calculate_lean_angle(shoulder_mid, hip_mid)
            
            if self.direction == "left":
                angle_diff = -lean_angle  # Negative values for left
            else:
                angle_diff = lean_angle  # Positive values for right
            
            # Update value
            self.current_value = max(0.0, min(1.0, angle_diff / self.threshold))
            result = angle_diff > self.threshold
            
        elif self.direction == "forward" or self.direction == "back":
            # Improved forward/backward detection using angle from vertical
            # Calculate angle between shoulder-hip line and vertical
            # For forward/back, we need to look at the angle in the Y-Z plane
            # Use the vertical distance (Y) and depth (Z) to calculate lean angle
            shoulder_y_avg = (left_shoulder[1] + right_shoulder[1]) / 2
            hip_y_avg = (left_hip[1] + right_hip[1]) / 2
            shoulder_z_avg = (left_shoulder[2] + right_shoulder[2]) / 2
            hip_z_avg = (left_hip[2] + right_hip[2]) / 2
            
            # Calculate vertical distance (positive = shoulders below hips in image)
            y_diff = shoulder_y_avg - hip_y_avg
            # Calculate depth difference (negative = shoulders closer to camera)
            z_diff = shoulder_z_avg - hip_z_avg
            
            # Calculate angle from vertical using Y-Z plane
            # Use arctan2 to get angle considering both Y and Z
            if abs(y_diff) > 0.001:  # Avoid division by zero
                # Normalize z_diff by y_diff to get lean ratio
                lean_ratio = z_diff / abs(y_diff)
                # Convert to angle (threshold is in degrees, convert ratio to angle)
                # More negative z_diff = more forward lean
                lean_angle_degrees = abs(np.degrees(np.arctan(lean_ratio)))
            else:
                lean_angle_degrees = 0.0
            
            if self.direction == "forward":
                # Forward lean: shoulders closer to camera (negative z_diff)
                # and/or shoulders lower than hips (positive y_diff)
                forward_lean = z_diff < -0.01  # Threshold for forward lean
                self.current_value = max(0.0, min(1.0, abs(z_diff) * 100))  # Scale z_diff
                result = forward_lean and lean_angle_degrees > self.threshold
            else:  # back
                # Backward lean: shoulders farther from camera (positive z_diff)
                backward_lean = z_diff > 0.01  # Threshold for backward lean
                self.current_value = max(0.0, min(1.0, z_diff * 100))  # Scale z_diff
                result = backward_lean and lean_angle_degrees > self.threshold
        
        # Apply debouncing to prevent flickering
        result = self._apply_debouncing(result)
        self.is_active = result
        return result
    
    def get_value(self) -> float:
        """Get trigger value (0.0-1.0)"""
        return self.current_value
    
    def get_name(self) -> str:
        """Get trigger type name"""
        return "body_lean"


