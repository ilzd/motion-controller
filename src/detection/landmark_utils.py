"""Utility functions for working with MediaPipe landmarks"""

import mediapipe as mp
from typing import Tuple, Optional
from src.utils.math_utils import calculate_angle_2d, calculate_distance_2d, calculate_distance_3d


# MediaPipe pose landmark indices
class LandmarkIndex:
    """MediaPipe pose landmark indices"""
    NOSE = 0
    LEFT_EYE_INNER = 1
    LEFT_EYE = 2
    LEFT_EYE_OUTER = 3
    RIGHT_EYE_INNER = 4
    RIGHT_EYE = 5
    RIGHT_EYE_OUTER = 6
    LEFT_EAR = 7
    RIGHT_EAR = 8
    MOUTH_LEFT = 9
    MOUTH_RIGHT = 10
    LEFT_SHOULDER = 11
    RIGHT_SHOULDER = 12
    LEFT_ELBOW = 13
    RIGHT_ELBOW = 14
    LEFT_WRIST = 15
    RIGHT_WRIST = 16
    LEFT_PINKY = 17
    RIGHT_PINKY = 18
    LEFT_INDEX = 19
    RIGHT_INDEX = 20
    LEFT_THUMB = 21
    RIGHT_THUMB = 22
    LEFT_HIP = 23
    RIGHT_HIP = 24
    LEFT_KNEE = 25
    RIGHT_KNEE = 26
    LEFT_ANKLE = 27
    RIGHT_ANKLE = 28
    LEFT_HEEL = 29
    RIGHT_HEEL = 30
    LEFT_FOOT_INDEX = 31
    RIGHT_FOOT_INDEX = 32


def get_landmark_position(landmarks: object, landmark_id: int) -> Optional[Tuple[float, float, float]]:
    """
    Get the position of a specific landmark.
    
    Args:
        landmarks: MediaPipe pose landmarks object
        landmark_id: Index of the landmark
        
    Returns:
        (x, y, z) tuple with normalized coordinates, or None if invalid
    """
    if landmarks is None:
        return None
    
    try:
        landmark = landmarks.landmark[landmark_id]
        return (landmark.x, landmark.y, landmark.z)
    except (IndexError, AttributeError):
        return None


def get_landmark_visibility(landmarks: object, landmark_id: int) -> Optional[float]:
    """
    Get the visibility score of a specific landmark.
    
    Args:
        landmarks: MediaPipe pose landmarks object
        landmark_id: Index of the landmark
        
    Returns:
        Visibility score (0-1), or None if invalid
    """
    if landmarks is None:
        return None
    
    try:
        landmark = landmarks.landmark[landmark_id]
        return landmark.visibility
    except (IndexError, AttributeError):
        return None


def calculate_angle(landmarks: object, 
                   point1_id: int, 
                   point2_id: int, 
                   point3_id: int) -> Optional[float]:
    """
    Calculate angle at point2 formed by three landmarks.
    
    Args:
        landmarks: MediaPipe pose landmarks object
        point1_id: First landmark ID
        point2_id: Vertex landmark ID
        point3_id: Third landmark ID
        
    Returns:
        Angle in degrees, or None if landmarks not available
    """
    pos1 = get_landmark_position(landmarks, point1_id)
    pos2 = get_landmark_position(landmarks, point2_id)
    pos3 = get_landmark_position(landmarks, point3_id)
    
    if pos1 is None or pos2 is None or pos3 is None:
        return None
    
    # Use only x and y coordinates for 2D angle
    return calculate_angle_2d(
        (pos1[0], pos1[1]),
        (pos2[0], pos2[1]),
        (pos3[0], pos3[1])
    )


def calculate_distance(landmarks: object, 
                      point1_id: int, 
                      point2_id: int,
                      use_3d: bool = False) -> Optional[float]:
    """
    Calculate distance between two landmarks.
    
    Args:
        landmarks: MediaPipe pose landmarks object
        point1_id: First landmark ID
        point2_id: Second landmark ID
        use_3d: Whether to use 3D coordinates (includes z)
        
    Returns:
        Distance (normalized), or None if landmarks not available
    """
    pos1 = get_landmark_position(landmarks, point1_id)
    pos2 = get_landmark_position(landmarks, point2_id)
    
    if pos1 is None or pos2 is None:
        return None
    
    if use_3d:
        return calculate_distance_3d(pos1, pos2)
    else:
        return calculate_distance_2d((pos1[0], pos1[1]), (pos2[0], pos2[1]))


def normalize_by_torso_height(landmarks: object, 
                              point: Tuple[float, float, float]) -> Optional[Tuple[float, float, float]]:
    """
    Normalize a point by the torso height (shoulder to hip distance).
    
    Args:
        landmarks: MediaPipe pose landmarks object
        point: Point to normalize (x, y, z)
        
    Returns:
        Normalized point, or None if torso not detected
    """
    # Calculate average torso height
    left_shoulder = get_landmark_position(landmarks, LandmarkIndex.LEFT_SHOULDER)
    right_shoulder = get_landmark_position(landmarks, LandmarkIndex.RIGHT_SHOULDER)
    left_hip = get_landmark_position(landmarks, LandmarkIndex.LEFT_HIP)
    right_hip = get_landmark_position(landmarks, LandmarkIndex.RIGHT_HIP)
    
    if None in [left_shoulder, right_shoulder, left_hip, right_hip]:
        return None
    
    # Calculate midpoints
    shoulder_mid_y = (left_shoulder[1] + right_shoulder[1]) / 2
    hip_mid_y = (left_hip[1] + right_hip[1]) / 2
    
    torso_height = abs(hip_mid_y - shoulder_mid_y)
    
    if torso_height == 0:
        return None
    
    x, y, z = point
    return (x / torso_height, y / torso_height, z / torso_height)


def get_body_center(landmarks: object) -> Optional[Tuple[float, float]]:
    """
    Get the center point of the body (midpoint of shoulders and hips).
    
    Args:
        landmarks: MediaPipe pose landmarks object
        
    Returns:
        (x, y) coordinates of body center, or None if not detected
    """
    left_shoulder = get_landmark_position(landmarks, LandmarkIndex.LEFT_SHOULDER)
    right_shoulder = get_landmark_position(landmarks, LandmarkIndex.RIGHT_SHOULDER)
    left_hip = get_landmark_position(landmarks, LandmarkIndex.LEFT_HIP)
    right_hip = get_landmark_position(landmarks, LandmarkIndex.RIGHT_HIP)
    
    if None in [left_shoulder, right_shoulder, left_hip, right_hip]:
        return None
    
    center_x = (left_shoulder[0] + right_shoulder[0] + left_hip[0] + right_hip[0]) / 4
    center_y = (left_shoulder[1] + right_shoulder[1] + left_hip[1] + right_hip[1]) / 4
    
    return (center_x, center_y)


