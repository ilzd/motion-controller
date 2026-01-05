"""Utility functions for working with MediaPipe hand landmarks"""

from typing import Tuple, Optional
from src.detection.hand_detector import get_hand_landmark_position


# MediaPipe hand landmark indices
class HandLandmarkIndex:
    """MediaPipe hand landmark indices"""
    WRIST = 0
    THUMB_CMC = 1
    THUMB_MCP = 2
    THUMB_IP = 3
    THUMB_TIP = 4
    INDEX_MCP = 5
    INDEX_PIP = 6
    INDEX_DIP = 7
    INDEX_TIP = 8
    MIDDLE_MCP = 9
    MIDDLE_PIP = 10
    MIDDLE_DIP = 11
    MIDDLE_TIP = 12
    RING_MCP = 13
    RING_PIP = 14
    RING_DIP = 15
    RING_TIP = 16
    PINKY_MCP = 17
    PINKY_PIP = 18
    PINKY_DIP = 19
    PINKY_TIP = 20


def calculate_finger_extension(hand_landmarks: object, finger: str) -> Optional[float]:
    """
    Calculate how extended a finger is (0.0 = fully closed, 1.0 = fully extended).
    
    Args:
        hand_landmarks: MediaPipe hand landmarks
        finger: "thumb", "index", "middle", "ring", or "pinky"
        
    Returns:
        Extension value 0.0-1.0, or None if invalid
    """
    if hand_landmarks is None:
        return None
    
    finger = finger.lower()
    
    try:
        if finger == "thumb":
            tip = get_hand_landmark_position(hand_landmarks, HandLandmarkIndex.THUMB_TIP)
            ip = get_hand_landmark_position(hand_landmarks, HandLandmarkIndex.THUMB_IP)
            mcp = get_hand_landmark_position(hand_landmarks, HandLandmarkIndex.THUMB_MCP)
            wrist = get_hand_landmark_position(hand_landmarks, HandLandmarkIndex.WRIST)
            
            if None in [tip, ip, mcp, wrist]:
                return None
            
            # For thumb, measure distance from wrist
            tip_dist = abs(tip[0] - wrist[0]) + abs(tip[1] - wrist[1])
            ip_dist = abs(ip[0] - wrist[0]) + abs(ip[1] - wrist[1])
            
            if ip_dist == 0:
                return 0.0
            
            extension = min(1.0, tip_dist / ip_dist)
            return extension
            
        elif finger == "index":
            tip = get_hand_landmark_position(hand_landmarks, HandLandmarkIndex.INDEX_TIP)
            pip = get_hand_landmark_position(hand_landmarks, HandLandmarkIndex.INDEX_PIP)
            mcp = get_hand_landmark_position(hand_landmarks, HandLandmarkIndex.INDEX_MCP)
        elif finger == "middle":
            tip = get_hand_landmark_position(hand_landmarks, HandLandmarkIndex.MIDDLE_TIP)
            pip = get_hand_landmark_position(hand_landmarks, HandLandmarkIndex.MIDDLE_PIP)
            mcp = get_hand_landmark_position(hand_landmarks, HandLandmarkIndex.MIDDLE_MCP)
        elif finger == "ring":
            tip = get_hand_landmark_position(hand_landmarks, HandLandmarkIndex.RING_TIP)
            pip = get_hand_landmark_position(hand_landmarks, HandLandmarkIndex.RING_PIP)
            mcp = get_hand_landmark_position(hand_landmarks, HandLandmarkIndex.RING_MCP)
        elif finger == "pinky":
            tip = get_hand_landmark_position(hand_landmarks, HandLandmarkIndex.PINKY_TIP)
            pip = get_hand_landmark_position(hand_landmarks, HandLandmarkIndex.PINKY_PIP)
            mcp = get_hand_landmark_position(hand_landmarks, HandLandmarkIndex.PINKY_MCP)
        else:
            return None
        
        if None in [tip, pip, mcp]:
            return None
        
        # For other fingers, measure Y distance (tip above PIP = extended)
        # Calculate extension based on how far tip is above PIP
        y_diff = pip[1] - tip[1]  # Positive = tip above PIP = extended
        
        # Normalize: assume fully extended is when tip is significantly above PIP
        # Use MCP-PIP distance as reference
        mcp_pip_dist = abs(pip[1] - mcp[1])
        
        if mcp_pip_dist == 0:
            return 0.0
        
        extension = max(0.0, min(1.0, y_diff / mcp_pip_dist))
        return extension
        
    except Exception:
        return None


