"""Pointing gesture trigger - detects pointing with index finger"""

from typing import Dict, Any, Optional
from src.recognition.base_trigger import BaseTrigger
from src.recognition.trigger_registry import TriggerRegistry
from src.detection.hand_landmark_utils import HandLandmarkIndex
from src.detection.hand_detector import get_hand_landmark_position


@TriggerRegistry.register("pointing_gesture")
class PointingGestureTrigger(BaseTrigger):
    """Detects pointing gesture (index finger extended, others closed)"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize pointing gesture trigger.
        
        Config parameters:
            hand: "left", "right", or "both"
            min_confidence: Minimum confidence threshold (0.0-1.0, default 0.7)
            require_thumb: Whether thumb must also be extended (default False)
        """
        super().__init__(config)
        self.hand = self.get_config_param("hand", "right").lower()
        self.min_confidence = self.get_config_param("min_confidence", 0.7)
        self.require_thumb = self.get_config_param("require_thumb", False)
        
    def detect(self, landmarks: object, frame_data: Dict[str, Any]) -> bool:
        """Detect pointing gesture"""
        hands = frame_data.get("hands")
        
        if hands is None or not hands:
            self.is_active = False
            self.current_value = 0.0
            return False
        
        if self.hand == "left":
            result = self._check_hand(hands.get("left"))
        elif self.hand == "right":
            result = self._check_hand(hands.get("right"))
        elif self.hand == "both":
            left_result = self._check_hand(hands.get("left"))
            right_result = self._check_hand(hands.get("right"))
            result = left_result or right_result
        else:
            result = False
        
        # Apply debouncing
        result = self._apply_debouncing(result)
        self.is_active = result
        return result
    
    def _check_hand(self, hand_data: Optional[Dict]) -> bool:
        """Check if hand is pointing"""
        if hand_data is None:
            return False
        
        hand_landmarks = hand_data.get("landmarks")
        if hand_landmarks is None:
            return False
        
        # Check index finger extension
        index_tip = get_hand_landmark_position(hand_landmarks, HandLandmarkIndex.INDEX_TIP)
        index_pip = get_hand_landmark_position(hand_landmarks, HandLandmarkIndex.INDEX_PIP)
        index_mcp = get_hand_landmark_position(hand_landmarks, HandLandmarkIndex.INDEX_MCP)
        
        if None in [index_tip, index_pip, index_mcp]:
            self.current_value = 0.0
            return False
        
        # Index finger should be extended (tip above PIP)
        index_extended = index_tip[1] < index_pip[1]
        
        if not index_extended:
            self.current_value = 0.0
            return False
        
        # Check other fingers are closed
        middle_tip = get_hand_landmark_position(hand_landmarks, HandLandmarkIndex.MIDDLE_TIP)
        middle_pip = get_hand_landmark_position(hand_landmarks, HandLandmarkIndex.MIDDLE_PIP)
        ring_tip = get_hand_landmark_position(hand_landmarks, HandLandmarkIndex.RING_TIP)
        ring_pip = get_hand_landmark_position(hand_landmarks, HandLandmarkIndex.RING_PIP)
        pinky_tip = get_hand_landmark_position(hand_landmarks, HandLandmarkIndex.PINKY_TIP)
        pinky_pip = get_hand_landmark_position(hand_landmarks, HandLandmarkIndex.PINKY_PIP)
        
        if None in [middle_tip, middle_pip, ring_tip, ring_pip, pinky_tip, pinky_pip]:
            self.current_value = 0.0
            return False
        
        # Other fingers should be closed (tip below PIP)
        middle_closed = middle_tip[1] > middle_pip[1]
        ring_closed = ring_tip[1] > ring_pip[1]
        pinky_closed = pinky_tip[1] > pinky_pip[1]
        
        # Check thumb if required
        thumb_ok = True
        if self.require_thumb:
            thumb_tip = get_hand_landmark_position(hand_landmarks, HandLandmarkIndex.THUMB_TIP)
            thumb_ip = get_hand_landmark_position(hand_landmarks, HandLandmarkIndex.THUMB_IP)
            wrist = get_hand_landmark_position(hand_landmarks, HandLandmarkIndex.WRIST)
            
            if None in [thumb_tip, thumb_ip, wrist]:
                thumb_ok = False
            else:
                # Thumb extended if tip is further from wrist than IP
                thumb_extended = abs(thumb_tip[0] - wrist[0]) > abs(thumb_ip[0] - wrist[0])
                thumb_ok = thumb_extended
        
        if middle_closed and ring_closed and pinky_closed and thumb_ok:
            # Calculate confidence based on how clearly pointing
            index_extension = (index_pip[1] - index_tip[1]) / abs(index_mcp[1] - index_pip[1])
            confidence = min(1.0, max(0.0, index_extension))
            
            self.current_value = confidence
            return confidence >= self.min_confidence
        else:
            self.current_value = 0.0
            return False
    
    def get_value(self) -> float:
        """Get trigger value (0.0-1.0 representing pointing confidence)"""
        return self.current_value
    
    def get_name(self) -> str:
        """Get trigger type name"""
        return "pointing_gesture"

