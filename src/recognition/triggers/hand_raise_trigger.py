"""Hand raise trigger - detects when hand is raised above shoulder"""

from typing import Dict, Any
from src.recognition.base_trigger import BaseTrigger
from src.recognition.trigger_registry import TriggerRegistry
from src.detection.landmark_utils import (
    get_landmark_position, 
    LandmarkIndex
)


@TriggerRegistry.register("hand_raise")
class HandRaiseTrigger(BaseTrigger):
    """Detects when hand(s) are raised above shoulder level"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize hand raise trigger.
        
        Config parameters:
            hand: "left", "right", or "both"
            threshold: Height above shoulder (0.0-1.0, default 0.2)
        """
        super().__init__(config)
        self.hand = self.get_config_param("hand", "right").lower()
        self.threshold = self.get_config_param("threshold", 0.2)
        
    def detect(self, landmarks: object, frame_data: Dict[str, Any]) -> bool:
        """Detect if hand is raised above shoulder"""
        if landmarks is None:
            self.is_active = False
            self.current_value = 0.0
            return False
        
        # Get positions based on which hand to check
        if self.hand == "left":
            result = self._check_hand(
                landmarks, 
                LandmarkIndex.LEFT_WRIST, 
                LandmarkIndex.LEFT_SHOULDER
            )
        elif self.hand == "right":
            result = self._check_hand(
                landmarks, 
                LandmarkIndex.RIGHT_WRIST, 
                LandmarkIndex.RIGHT_SHOULDER
            )
        elif self.hand == "both":
            left_result = self._check_hand(
                landmarks, 
                LandmarkIndex.LEFT_WRIST, 
                LandmarkIndex.LEFT_SHOULDER
            )
            right_result = self._check_hand(
                landmarks, 
                LandmarkIndex.RIGHT_WRIST, 
                LandmarkIndex.RIGHT_SHOULDER
            )
            result = left_result and right_result
        else:
            result = False
        
        self.is_active = result
        return result
    
    def _check_hand(self, landmarks: object, wrist_id: int, shoulder_id: int) -> bool:
        """Check if a specific hand is raised"""
        wrist_pos = get_landmark_position(landmarks, wrist_id)
        shoulder_pos = get_landmark_position(landmarks, shoulder_id)
        
        if wrist_pos is None or shoulder_pos is None:
            return False
        
        # Calculate height difference (negative because y increases downward)
        height_diff = shoulder_pos[1] - wrist_pos[1]
        
        # Update current value for analog output
        self.current_value = max(0.0, min(1.0, height_diff / self.threshold))
        
        return height_diff > self.threshold
    
    def get_value(self) -> float:
        """Get trigger value (0.0-1.0)"""
        return self.current_value
    
    def get_name(self) -> str:
        """Get trigger type name"""
        return "hand_raise"


