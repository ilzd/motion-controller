"""Body lean trigger - detects when body leans in a direction"""

from typing import Dict, Any
from src.recognition.base_trigger import BaseTrigger
from src.recognition.trigger_registry import TriggerRegistry
from src.detection.landmark_utils import (
    get_landmark_position, 
    LandmarkIndex
)
from src.utils.math_utils import calculate_lean_angle


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
        self.threshold = self.get_config_param("threshold", 15.0)
        
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
            # Use z-coordinate for forward/backward lean
            shoulder_z_avg = (left_shoulder[2] + right_shoulder[2]) / 2
            hip_z_avg = (left_hip[2] + right_hip[2]) / 2
            
            z_diff = shoulder_z_avg - hip_z_avg
            
            if self.direction == "forward":
                # Forward lean: shoulders closer to camera than hips
                self.current_value = max(0.0, min(1.0, -z_diff / (self.threshold / 100)))
                result = z_diff < -(self.threshold / 100)
            else:  # back
                # Backward lean: shoulders farther from camera than hips
                self.current_value = max(0.0, min(1.0, z_diff / (self.threshold / 100)))
                result = z_diff > (self.threshold / 100)
        
        self.is_active = result
        return result
    
    def get_value(self) -> float:
        """Get trigger value (0.0-1.0)"""
        return self.current_value
    
    def get_name(self) -> str:
        """Get trigger type name"""
        return "body_lean"


