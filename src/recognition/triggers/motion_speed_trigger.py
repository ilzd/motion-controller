"""Motion speed trigger - detects fast movement of body parts"""

import time
from typing import Dict, Any, Optional, Tuple
from src.recognition.base_trigger import BaseTrigger
from src.recognition.trigger_registry import TriggerRegistry
from src.detection.landmark_utils import (
    get_landmark_position,
    get_landmark_visibility,
    LandmarkIndex
)
from src.utils.constants import MIN_LANDMARK_VISIBILITY
from src.utils.math_utils import calculate_distance_3d


@TriggerRegistry.register("motion_speed")
class MotionSpeedTrigger(BaseTrigger):
    """Detects fast movement of body parts"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize motion speed trigger.
        
        Config parameters:
            body_part: "left_wrist", "right_wrist", "left_ankle", "right_ankle", 
                      "left_knee", "right_knee", "nose", "left_shoulder", "right_shoulder"
            min_speed: Minimum speed threshold (normalized units per second, default 0.5)
            direction: "any", "up", "down", "left", "right", "forward", "back"
            smoothing: Number of frames to average speed over (default 3)
        """
        super().__init__(config)
        self.body_part = self.get_config_param("body_part", "right_wrist").lower()
        self.min_speed = self.get_config_param("min_speed", 0.5)
        self.direction = self.get_config_param("direction", "any").lower()
        self.smoothing = self.get_config_param("smoothing", 3)
        
        # Track position history for speed calculation
        self.position_history: list = []
        self.time_history: list = []
        
        # Map body part names to landmark indices
        self.landmark_map = {
            "left_wrist": LandmarkIndex.LEFT_WRIST,
            "right_wrist": LandmarkIndex.RIGHT_WRIST,
            "left_ankle": LandmarkIndex.LEFT_ANKLE,
            "right_ankle": LandmarkIndex.RIGHT_ANKLE,
            "left_knee": LandmarkIndex.LEFT_KNEE,
            "right_knee": LandmarkIndex.RIGHT_KNEE,
            "nose": LandmarkIndex.NOSE,
            "left_shoulder": LandmarkIndex.LEFT_SHOULDER,
            "right_shoulder": LandmarkIndex.RIGHT_SHOULDER,
            "left_hip": LandmarkIndex.LEFT_HIP,
            "right_hip": LandmarkIndex.RIGHT_HIP,
        }
        
    def detect(self, landmarks: object, frame_data: Dict[str, Any]) -> bool:
        """Detect if body part is moving fast enough"""
        if landmarks is None:
            self.is_active = False
            self.current_value = 0.0
            return False
        
        landmark_id = self.landmark_map.get(self.body_part)
        if landmark_id is None:
            self.is_active = False
            self.current_value = 0.0
            return False
        
        pos = get_landmark_position(landmarks, landmark_id)
        if pos is None:
            self.is_active = False
            self.current_value = 0.0
            return False
        
        vis = get_landmark_visibility(landmarks, landmark_id)
        if vis is None or vis < MIN_LANDMARK_VISIBILITY:
            self.is_active = False
            self.current_value = 0.0
            return False
        
        current_time = time.time()
        
        # Add to history
        self.position_history.append(pos)
        self.time_history.append(current_time)
        
        # Keep only recent history
        if len(self.position_history) > self.smoothing + 1:
            self.position_history.pop(0)
            self.time_history.pop(0)
        
        # Need at least 2 points to calculate speed
        if len(self.position_history) < 2:
            self.is_active = False
            self.current_value = 0.0
            return False
        
        # Calculate speed over smoothing window
        start_pos = self.position_history[0]
        end_pos = self.position_history[-1]
        start_time = self.time_history[0]
        end_time = self.time_history[-1]
        
        dt = end_time - start_time
        if dt <= 0:
            self.is_active = False
            self.current_value = 0.0
            return False
        
        # Calculate distance moved
        distance = calculate_distance_3d(start_pos, end_pos)
        speed = distance / dt
        
        # Check direction if specified
        direction_match = True
        if self.direction != "any" and len(start_pos) > 2 and len(end_pos) > 2:
            dx = end_pos[0] - start_pos[0]
            dy = end_pos[1] - start_pos[1]
            dz = end_pos[2] - start_pos[2]
            
            if self.direction == "up":
                direction_match = dy < -0.001  # Moving up (y decreases)
            elif self.direction == "down":
                direction_match = dy > 0.001  # Moving down (y increases)
            elif self.direction == "left":
                direction_match = dx < -0.001  # Moving left (x decreases)
            elif self.direction == "right":
                direction_match = dx > 0.001  # Moving right (x increases)
            elif self.direction == "forward":
                direction_match = dz < -0.001  # Moving forward (z decreases)
            elif self.direction == "back":
                direction_match = dz > 0.001  # Moving back (z increases)
        
        if speed >= self.min_speed and direction_match:
            # Normalize value (cap at 2x min_speed for 1.0)
            self.current_value = min(1.0, speed / (self.min_speed * 2))
            result = True
        else:
            self.current_value = 0.0
            result = False
        
        # Apply debouncing
        result = self._apply_debouncing(result)
        self.is_active = result
        return result
    
    def get_value(self) -> float:
        """Get trigger value (0.0-1.0 representing speed relative to threshold)"""
        return self.current_value
    
    def get_name(self) -> str:
        """Get trigger type name"""
        return "motion_speed"
    
    def reset(self):
        """Reset trigger state"""
        super().reset()
        self.position_history.clear()
        self.time_history.clear()



