"""Arm stretch trigger - detects arm pointing/stretching in a direction"""

from typing import Dict, Any, Optional, Tuple
import numpy as np
from src.recognition.base_trigger import BaseTrigger
from src.recognition.trigger_registry import TriggerRegistry
from src.detection.landmark_utils import (
    get_landmark_position,
    get_landmark_visibility,
    LandmarkIndex
)
from src.utils.constants import MIN_LANDMARK_VISIBILITY
from src.utils.math_utils import calculate_angle_2d, calculate_distance_2d, calculate_distance_3d


@TriggerRegistry.register("arm_stretch")
class ArmStretchTrigger(BaseTrigger):
    """Detects when arm is stretched/pointed in a specific direction"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize arm stretch trigger.
        
        Config parameters:
            arm: "left", "right", or "both"
            direction: "up", "down", "left", "right", "forward", "back", or "any"
            min_extension: Minimum arm extension ratio (0.0-1.0, default 0.6)
            angle_tolerance: Angle tolerance in degrees (default 30)
            min_speed: Minimum movement speed for motion detection (default 0.0 = disabled)
        """
        super().__init__(config)
        self.arm = self.get_config_param("arm", "right").lower()
        self.direction = self.get_config_param("direction", "forward").lower()
        self.min_extension = self.get_config_param("min_extension", 0.6)
        self.angle_tolerance = self.get_config_param("angle_tolerance", 30.0)
        self.min_speed = self.get_config_param("min_speed", 0.0)
        
        # Track previous positions for speed calculation
        self.previous_wrist_pos: Optional[Tuple[float, float, float]] = None
        self.previous_shoulder_pos: Optional[Tuple[float, float, float]] = None
        self.previous_time: Optional[float] = None
        
    def detect(self, landmarks: object, frame_data: Dict[str, Any]) -> bool:
        """Detect if arm is stretched in specified direction"""
        if landmarks is None:
            self.is_active = False
            self.current_value = 0.0
            return False
        
        import time
        current_time = time.time()
        
        # Get arm landmarks
        if self.arm == "left":
            wrist_pos = get_landmark_position(landmarks, LandmarkIndex.LEFT_WRIST)
            elbow_pos = get_landmark_position(landmarks, LandmarkIndex.LEFT_ELBOW)
            shoulder_pos = get_landmark_position(landmarks, LandmarkIndex.LEFT_SHOULDER)
            wrist_vis = get_landmark_visibility(landmarks, LandmarkIndex.LEFT_WRIST)
            shoulder_vis = get_landmark_visibility(landmarks, LandmarkIndex.LEFT_SHOULDER)
        elif self.arm == "right":
            wrist_pos = get_landmark_position(landmarks, LandmarkIndex.RIGHT_WRIST)
            elbow_pos = get_landmark_position(landmarks, LandmarkIndex.RIGHT_ELBOW)
            shoulder_pos = get_landmark_position(landmarks, LandmarkIndex.RIGHT_SHOULDER)
            wrist_vis = get_landmark_visibility(landmarks, LandmarkIndex.RIGHT_WRIST)
            shoulder_vis = get_landmark_visibility(landmarks, LandmarkIndex.RIGHT_SHOULDER)
        else:
            # Check both arms - trigger if either matches
            left_result = self._check_arm(
                landmarks, 
                LandmarkIndex.LEFT_WRIST,
                LandmarkIndex.LEFT_ELBOW,
                LandmarkIndex.LEFT_SHOULDER,
                current_time
            )
            right_result = self._check_arm(
                landmarks,
                LandmarkIndex.RIGHT_WRIST,
                LandmarkIndex.RIGHT_ELBOW,
                LandmarkIndex.RIGHT_SHOULDER,
                current_time
            )
            result = left_result or right_result
            
            # Apply debouncing
            result = self._apply_debouncing(result)
            self.is_active = result
            return result
        
        if None in [wrist_pos, elbow_pos, shoulder_pos]:
            self.is_active = False
            self.current_value = 0.0
            return False
        
        if (wrist_vis is None or wrist_vis < MIN_LANDMARK_VISIBILITY or
            shoulder_vis is None or shoulder_vis < MIN_LANDMARK_VISIBILITY):
            self.is_active = False
            self.current_value = 0.0
            return False
        
        result = self._check_arm_stretch(
            wrist_pos, elbow_pos, shoulder_pos, current_time
        )
        
        # Apply debouncing
        result = self._apply_debouncing(result)
        self.is_active = result
        return result
    
    def _check_arm(self, landmarks: object, wrist_id: int, elbow_id: int, 
                   shoulder_id: int, current_time: float) -> bool:
        """Check a specific arm"""
        wrist_pos = get_landmark_position(landmarks, wrist_id)
        elbow_pos = get_landmark_position(landmarks, elbow_id)
        shoulder_pos = get_landmark_position(landmarks, shoulder_id)
        
        if None in [wrist_pos, elbow_pos, shoulder_pos]:
            return False
        
        return self._check_arm_stretch(wrist_pos, elbow_pos, shoulder_pos, current_time)
    
    def _check_arm_stretch(self, wrist_pos: Tuple[float, float, float],
                          elbow_pos: Tuple[float, float, float],
                          shoulder_pos: Tuple[float, float, float],
                          current_time: float) -> bool:
        """Check if arm is stretched in the specified direction"""
        # Calculate arm extension (how straight the arm is)
        # Use elbow as vertex, check angle between shoulder-elbow-wrist
        angle = calculate_angle_2d(
            (shoulder_pos[0], shoulder_pos[1]),
            (elbow_pos[0], elbow_pos[1]),
            (wrist_pos[0], wrist_pos[1])
        )
        
        # Arm is extended if angle is close to 180 degrees (straight)
        extension_ratio = 1.0 - abs(180.0 - angle) / 180.0
        
        if extension_ratio < self.min_extension:
            self.current_value = 0.0
            return False
        
        # Check direction
        direction_match = False
        if self.direction == "any":
            direction_match = True
        else:
            # Calculate vector from shoulder to wrist
            dx = wrist_pos[0] - shoulder_pos[0]
            dy = wrist_pos[1] - shoulder_pos[1]
            dz = wrist_pos[2] - shoulder_pos[2] if len(wrist_pos) > 2 else 0.0
            
            # Calculate angle from vertical/horizontal
            angle_2d = np.degrees(np.arctan2(dx, -dy))  # -dy because y increases downward
            
            if self.direction == "up":
                # Up: angle between -45 and 45 degrees (or 135 to -135)
                direction_match = abs(angle_2d) < self.angle_tolerance or abs(angle_2d) > 180 - self.angle_tolerance
            elif self.direction == "down":
                # Down: angle between 135 and -135 degrees
                direction_match = abs(angle_2d) > 180 - self.angle_tolerance or abs(angle_2d) < self.angle_tolerance
            elif self.direction == "right":
                # Right: angle between 45 and 135 degrees
                direction_match = 45 - self.angle_tolerance <= angle_2d <= 135 + self.angle_tolerance
            elif self.direction == "left":
                # Left: angle between -45 and -135 degrees (or 135 to 225)
                direction_match = (-135 - self.angle_tolerance <= angle_2d <= -45 + self.angle_tolerance or
                                 135 - self.angle_tolerance <= angle_2d <= 225 + self.angle_tolerance)
            elif self.direction == "forward":
                # Forward: wrist closer to camera (negative z)
                direction_match = dz < -0.01
            elif self.direction == "back":
                # Back: wrist farther from camera (positive z)
                direction_match = dz > 0.01
        
        # Check speed if required
        speed_ok = True
        if self.min_speed > 0.0:
            speed_ok = self._check_speed(wrist_pos, current_time)
        
        if direction_match and speed_ok:
            # Update value based on extension quality
            self.current_value = extension_ratio
            return True
        else:
            self.current_value = 0.0
            return False
    
    def _check_speed(self, wrist_pos: Tuple[float, float, float], current_time: float) -> bool:
        """Check if wrist is moving fast enough"""
        if self.previous_wrist_pos is None or self.previous_time is None:
            self.previous_wrist_pos = wrist_pos
            self.previous_time = current_time
            return False
        
        dt = current_time - self.previous_time
        if dt <= 0:
            return False
        
        # Calculate distance moved
        distance = calculate_distance_3d(self.previous_wrist_pos, wrist_pos)
        speed = distance / dt
        
        # Update previous values
        self.previous_wrist_pos = wrist_pos
        self.previous_time = current_time
        
        return speed >= self.min_speed
    
    def get_value(self) -> float:
        """Get trigger value (0.0-1.0 representing extension quality)"""
        return self.current_value
    
    def get_name(self) -> str:
        """Get trigger type name"""
        return "arm_stretch"
    
    def reset(self):
        """Reset trigger state"""
        super().reset()
        self.previous_wrist_pos = None
        self.previous_shoulder_pos = None
        self.previous_time = None



