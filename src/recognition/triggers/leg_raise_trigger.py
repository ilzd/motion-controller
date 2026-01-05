"""Leg raise trigger - detects leg lifting/kicking"""

from typing import Dict, Any, Optional
from src.recognition.base_trigger import BaseTrigger
from src.recognition.trigger_registry import TriggerRegistry
from src.detection.landmark_utils import (
    get_landmark_position,
    get_landmark_visibility,
    LandmarkIndex
)
from src.utils.constants import MIN_LANDMARK_VISIBILITY
from src.utils.math_utils import calculate_angle_2d


@TriggerRegistry.register("leg_raise")
class LegRaiseTrigger(BaseTrigger):
    """Detects when leg is raised/kicked"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize leg raise trigger.
        
        Config parameters:
            leg: "left", "right", or "both"
            direction: "forward", "back", "up", or "any"
            min_height: Minimum height above hip (0.0-1.0, default 0.15)
            min_angle: Minimum knee angle in degrees (default 120, lower = more bent)
        """
        super().__init__(config)
        self.leg = self.get_config_param("leg", "right").lower()
        self.direction = self.get_config_param("direction", "forward").lower()
        self.min_height = self.get_config_param("min_height", 0.15)
        self.min_angle = self.get_config_param("min_angle", 120.0)
        
    def detect(self, landmarks: object, frame_data: Dict[str, Any]) -> bool:
        """Detect if leg is raised"""
        if landmarks is None:
            self.is_active = False
            self.current_value = 0.0
            return False
        
        if self.leg == "left":
            result = self._check_leg(
                landmarks,
                LandmarkIndex.LEFT_HIP,
                LandmarkIndex.LEFT_KNEE,
                LandmarkIndex.LEFT_ANKLE
            )
        elif self.leg == "right":
            result = self._check_leg(
                landmarks,
                LandmarkIndex.RIGHT_HIP,
                LandmarkIndex.RIGHT_KNEE,
                LandmarkIndex.RIGHT_ANKLE
            )
        elif self.leg == "both":
            left_result = self._check_leg(
                landmarks,
                LandmarkIndex.LEFT_HIP,
                LandmarkIndex.LEFT_KNEE,
                LandmarkIndex.LEFT_ANKLE
            )
            right_result = self._check_leg(
                landmarks,
                LandmarkIndex.RIGHT_HIP,
                LandmarkIndex.RIGHT_KNEE,
                LandmarkIndex.RIGHT_ANKLE
            )
            result = left_result or right_result
        else:
            result = False
        
        # Apply debouncing
        result = self._apply_debouncing(result)
        self.is_active = result
        return result
    
    def _check_leg(self, landmarks: object, hip_id: int, knee_id: int, ankle_id: int) -> bool:
        """Check if a specific leg is raised"""
        hip_pos = get_landmark_position(landmarks, hip_id)
        knee_pos = get_landmark_position(landmarks, knee_id)
        ankle_pos = get_landmark_position(landmarks, ankle_id)
        
        if None in [hip_pos, knee_pos, ankle_pos]:
            return False
        
        # Check visibility
        hip_vis = get_landmark_visibility(landmarks, hip_id)
        knee_vis = get_landmark_visibility(landmarks, knee_id)
        ankle_vis = get_landmark_visibility(landmarks, ankle_id)
        
        if (hip_vis is None or hip_vis < MIN_LANDMARK_VISIBILITY or
            knee_vis is None or knee_vis < MIN_LANDMARK_VISIBILITY or
            ankle_vis is None or ankle_vis < MIN_LANDMARK_VISIBILITY):
            return False
        
        # Check height - knee should be above hip
        height_diff = hip_pos[1] - knee_pos[1]  # Positive = knee above hip
        if height_diff < self.min_height:
            self.current_value = 0.0
            return False
        
        # Check knee angle - leg should be somewhat extended
        knee_angle = calculate_angle_2d(
            (hip_pos[0], hip_pos[1]),
            (knee_pos[0], knee_pos[1]),
            (ankle_pos[0], ankle_pos[1])
        )
        
        if knee_angle < self.min_angle:
            self.current_value = 0.0
            return False
        
        # Check direction
        direction_match = True
        if self.direction != "any":
            # Calculate vector from hip to knee
            dx = knee_pos[0] - hip_pos[0]
            dy = knee_pos[1] - hip_pos[1]
            dz = knee_pos[2] - hip_pos[2] if len(knee_pos) > 2 else 0.0
            
            if self.direction == "forward":
                # Forward: knee closer to camera
                direction_match = dz < -0.01
            elif self.direction == "back":
                # Back: knee farther from camera
                direction_match = dz > 0.01
            elif self.direction == "up":
                # Up: knee significantly above hip
                direction_match = height_diff > self.min_height * 1.5
        
        if direction_match:
            # Value based on height and angle quality
            height_ratio = min(1.0, height_diff / (self.min_height * 2))
            angle_ratio = min(1.0, (knee_angle - self.min_angle) / (180 - self.min_angle))
            self.current_value = (height_ratio + angle_ratio) / 2.0
            return True
        else:
            self.current_value = 0.0
            return False
    
    def get_value(self) -> float:
        """Get trigger value (0.0-1.0 representing leg raise quality)"""
        return self.current_value
    
    def get_name(self) -> str:
        """Get trigger type name"""
        return "leg_raise"

