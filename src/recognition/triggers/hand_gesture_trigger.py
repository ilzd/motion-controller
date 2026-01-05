"""Hand gesture trigger - detects open/closed hand state"""

from typing import Dict, Any, Optional
from src.recognition.base_trigger import BaseTrigger
from src.recognition.trigger_registry import TriggerRegistry
from src.detection.hand_detector import is_hand_open, get_hand_landmark_position
from src.utils.constants import MIN_LANDMARK_VISIBILITY


@TriggerRegistry.register("hand_gesture")
class HandGestureTrigger(BaseTrigger):
    """Detects hand gestures (open/closed)"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize hand gesture trigger.
        
        Config parameters:
            hand: "left", "right", or "both"
            gesture: "open" or "closed"
            confidence: Minimum confidence threshold (0.0-1.0, default 0.7)
        """
        super().__init__(config)
        self.hand = self.get_config_param("hand", "right").lower()
        self.gesture = self.get_config_param("gesture", "open").lower()
        self.confidence_threshold = self.get_config_param("confidence", 0.7)
        
        # Validate gesture type
        if self.gesture not in ["open", "closed"]:
            raise ValueError(f"Invalid gesture type '{self.gesture}'. Must be 'open' or 'closed'")
    
    def detect(self, landmarks: object, frame_data: Dict[str, Any]) -> bool:
        """
        Detect hand gesture.
        
        Args:
            landmarks: MediaPipe pose landmarks (not used, but required by interface)
            frame_data: Must contain 'hands' key with hand detection results
        """
        # Get hands from frame_data
        hands = frame_data.get("hands")
        
        if hands is None or not hands:
            self.is_active = False
            self.current_value = 0.0
            return False
        
        result = False
        
        if self.hand == "left":
            result = self._check_hand(hands.get("left"))
        elif self.hand == "right":
            result = self._check_hand(hands.get("right"))
        elif self.hand == "both":
            left_result = self._check_hand(hands.get("left"))
            right_result = self._check_hand(hands.get("right"))
            # Both hands must match gesture
            if self.gesture == "open":
                result = left_result and right_result
            else:  # closed
                result = left_result and right_result
        else:
            result = False
        
        # Apply debouncing
        result = self._apply_debouncing(result)
        self.is_active = result
        return result
    
    def _check_hand(self, hand_data: Optional[Dict]) -> bool:
        """Check if a specific hand matches the gesture"""
        if hand_data is None:
            return False
        
        hand_landmarks = hand_data.get("landmarks")
        if hand_landmarks is None:
            return False
        
        # Determine if hand is open
        is_open = is_hand_open(hand_landmarks)
        
        # Check if it matches desired gesture
        if self.gesture == "open":
            matches = is_open
        else:  # closed
            matches = not is_open
        
        # Update confidence value
        if matches:
            # Calculate confidence based on how clearly the gesture is shown
            # For open: count extended fingers (higher = more confident)
            # For closed: count closed fingers (higher = more confident)
            self.current_value = self._calculate_confidence(hand_landmarks, is_open)
        else:
            self.current_value = 0.0
        
        return matches and (self.current_value >= self.confidence_threshold)
    
    def _calculate_confidence(self, hand_landmarks: object, is_open: bool) -> float:
        """
        Calculate confidence score for the gesture (0.0-1.0).
        
        Args:
            hand_landmarks: MediaPipe hand landmarks
            is_open: Whether hand is detected as open
            
        Returns:
            Confidence value 0.0-1.0
        """
        if hand_landmarks is None:
            return 0.0
        
        try:
            extended_count = 0
            total_fingers = 5
            
            # Check each finger
            finger_tips = [8, 12, 16, 20]  # Index, Middle, Ring, Pinky
            finger_pips = [6, 10, 14, 18]
            
            for tip_idx, pip_idx in zip(finger_tips, finger_pips):
                tip = hand_landmarks.landmark[tip_idx]
                pip = hand_landmarks.landmark[pip_idx]
                
                if tip.y < pip.y:  # Extended
                    extended_count += 1
            
            # Check thumb
            thumb_tip = hand_landmarks.landmark[4]
            thumb_ip = hand_landmarks.landmark[3]
            wrist = hand_landmarks.landmark[0]
            thumb_extended = abs(thumb_tip.x - wrist.x) > abs(thumb_ip.x - wrist.x)
            
            if thumb_extended:
                extended_count += 1
            
            if is_open:
                # Confidence increases with more extended fingers
                confidence = extended_count / total_fingers
            else:
                # Confidence increases with more closed fingers
                confidence = (total_fingers - extended_count) / total_fingers
            
            return confidence
            
        except Exception:
            return 0.0
    
    def get_value(self) -> float:
        """Get trigger value (0.0-1.0 representing confidence)"""
        return self.current_value
    
    def get_name(self) -> str:
        """Get trigger type name"""
        return "hand_gesture"


