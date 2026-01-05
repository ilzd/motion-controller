"""Hand detection using MediaPipe Hands"""

import cv2
import mediapipe as mp
import numpy as np
from typing import Optional, Tuple, Dict, Any
from src.utils.constants import (
    DEFAULT_MIN_DETECTION_CONFIDENCE,
    DEFAULT_MIN_TRACKING_CONFIDENCE
)


class HandDetector:
    """Wrapper for MediaPipe Hands detection"""
    
    def __init__(self,
                 static_image_mode: bool = False,
                 max_num_hands: int = 2,
                 min_detection_confidence: float = DEFAULT_MIN_DETECTION_CONFIDENCE,
                 min_tracking_confidence: float = DEFAULT_MIN_TRACKING_CONFIDENCE):
        """
        Initialize MediaPipe Hands detector.
        
        Args:
            static_image_mode: If True, treats each image as independent
            max_num_hands: Maximum number of hands to detect (1 or 2)
            min_detection_confidence: Minimum confidence for hand detection
            min_tracking_confidence: Minimum confidence for hand tracking
        """
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        self.hands = self.mp_hands.Hands(
            static_image_mode=static_image_mode,
            max_num_hands=max_num_hands,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
    
    def detect(self, frame: np.ndarray) -> Optional[Dict[str, Any]]:
        """
        Detect hands in a frame.
        
        Args:
            frame: BGR image from OpenCV
            
        Returns:
            Dictionary with 'left' and 'right' keys containing hand landmarks,
            or None if no hands detected. Each hand contains:
            - landmarks: MediaPipe hand landmarks (21 points)
            - handedness: 'Left' or 'Right' (from camera perspective)
        """
        if frame is None:
            return None
        
        # Convert BGR to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process the frame
        results = self.hands.process(rgb_frame)
        
        if not results.multi_hand_landmarks:
            return None
        
        # Organize hands by left/right
        hands_dict = {}
        
        for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
            # Get handedness (which hand from camera perspective)
            if results.multi_handedness:
                handedness = results.multi_handedness[idx].classification[0].label
            else:
                # Default to right if handedness not available
                handedness = "Right"
            
            # Store by lowercase key
            hand_key = handedness.lower()
            hands_dict[hand_key] = {
                'landmarks': hand_landmarks,
                'handedness': handedness
            }
        
        return hands_dict if hands_dict else None
    
    def draw_landmarks(self,
                      frame: np.ndarray,
                      hands: Optional[Dict[str, any]],
                      draw_connections: bool = True) -> np.ndarray:
        """
        Draw hand landmarks on frame.
        
        Args:
            frame: BGR image from OpenCV
            hands: Hands dictionary from detect()
            draw_connections: Whether to draw hand skeleton connections
            
        Returns:
            Frame with hand landmarks drawn
        """
        if hands is None:
            return frame
        
        # Create a copy to avoid modifying original
        annotated_frame = frame.copy()
        
        # Draw each hand
        for hand_data in hands.values():
            hand_landmarks = hand_data['landmarks']
            
            if draw_connections:
                self.mp_drawing.draw_landmarks(
                    annotated_frame,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS,
                    landmark_drawing_spec=self.mp_drawing_styles.get_default_hand_landmarks_style(),
                    connection_drawing_spec=self.mp_drawing_styles.get_default_hand_connections_style()
                )
            else:
                self.mp_drawing.draw_landmarks(
                    annotated_frame,
                    hand_landmarks,
                    None,
                    landmark_drawing_spec=self.mp_drawing_styles.get_default_hand_landmarks_style()
                )
        
        return annotated_frame
    
    def close(self):
        """Release MediaPipe resources"""
        self.hands.close()
    
    def __del__(self):
        """Cleanup on object destruction"""
        try:
            self.close()
        except:
            pass


def is_hand_open(hand_landmarks: object) -> bool:
    """
    Determine if a hand is open (fingers extended) or closed (fist).
    
    Algorithm: Check if fingertips are extended beyond their respective PIP joints.
    For each finger (thumb, index, middle, ring, pinky):
    - If fingertip is above PIP joint (lower Y value), finger is extended
    - If 3+ fingers are extended, hand is considered open
    
    Args:
        hand_landmarks: MediaPipe hand landmarks (21 points)
        
    Returns:
        True if hand is open, False if closed (fist)
    """
    if hand_landmarks is None:
        return False
    
    # MediaPipe hand landmark indices
    # Thumb: 4 (tip), 3 (IP), 2 (MCP)
    # Index: 8 (tip), 6 (PIP), 5 (MCP)
    # Middle: 12 (tip), 10 (PIP), 9 (MCP)
    # Ring: 16 (tip), 14 (PIP), 13 (MCP)
    # Pinky: 20 (tip), 18 (PIP), 17 (MCP)
    
    extended_fingers = 0
    
    # Check each finger (except thumb - different logic)
    finger_tips = [8, 12, 16, 20]  # Index, Middle, Ring, Pinky
    finger_pips = [6, 10, 14, 18]  # Corresponding PIP joints
    
    for tip_idx, pip_idx in zip(finger_tips, finger_pips):
        tip = hand_landmarks.landmark[tip_idx]
        pip = hand_landmarks.landmark[pip_idx]
        
        # Finger is extended if tip Y is above PIP Y (lower value = higher on screen)
        if tip.y < pip.y:
            extended_fingers += 1
    
    # Check thumb separately (compares X position instead of Y)
    thumb_tip = hand_landmarks.landmark[4]
    thumb_ip = hand_landmarks.landmark[3]
    # Thumb is extended if tip X is further from wrist than IP X
    # (depends on which hand, but this works for both)
    thumb_extended = abs(thumb_tip.x - hand_landmarks.landmark[0].x) > abs(thumb_ip.x - hand_landmarks.landmark[0].x)
    
    if thumb_extended:
        extended_fingers += 1
    
    # Hand is open if 3 or more fingers are extended
    return extended_fingers >= 3


def get_hand_landmark_position(hand_landmarks: object, landmark_id: int) -> Optional[Tuple[float, float, float]]:
    """
    Get the position of a specific hand landmark.
    
    Args:
        hand_landmarks: MediaPipe hand landmarks object
        landmark_id: Index of the landmark (0-20)
        
    Returns:
        (x, y, z) tuple with normalized coordinates, or None if invalid
    """
    if hand_landmarks is None:
        return None
    
    try:
        landmark = hand_landmarks.landmark[landmark_id]
        return (landmark.x, landmark.y, landmark.z)
    except (IndexError, AttributeError):
        return None

