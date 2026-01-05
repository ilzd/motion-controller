"""Mathematical utility functions for pose calculations"""

import numpy as np
from typing import Tuple


def calculate_angle_2d(point1: Tuple[float, float], 
                       point2: Tuple[float, float], 
                       point3: Tuple[float, float]) -> float:
    """
    Calculate angle at point2 formed by three points in 2D space.
    
    Args:
        point1: First point (x, y)
        point2: Vertex point (x, y)
        point3: Third point (x, y)
        
    Returns:
        Angle in degrees (0-180)
    """
    x1, y1 = point1
    x2, y2 = point2
    x3, y3 = point3
    
    # Create vectors
    vector1 = np.array([x1 - x2, y1 - y2])
    vector2 = np.array([x3 - x2, y3 - y2])
    
    # Calculate angle using dot product
    dot_product = np.dot(vector1, vector2)
    magnitude1 = np.linalg.norm(vector1)
    magnitude2 = np.linalg.norm(vector2)
    
    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0
    
    cos_angle = dot_product / (magnitude1 * magnitude2)
    cos_angle = np.clip(cos_angle, -1.0, 1.0)  # Handle floating point errors
    
    angle_radians = np.arccos(cos_angle)
    angle_degrees = np.degrees(angle_radians)
    
    return angle_degrees


def calculate_distance_2d(point1: Tuple[float, float], 
                          point2: Tuple[float, float]) -> float:
    """
    Calculate Euclidean distance between two points in 2D space.
    
    Args:
        point1: First point (x, y)
        point2: Second point (x, y)
        
    Returns:
        Distance between points
    """
    x1, y1 = point1
    x2, y2 = point2
    return np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def calculate_distance_3d(point1: Tuple[float, float, float], 
                          point2: Tuple[float, float, float]) -> float:
    """
    Calculate Euclidean distance between two points in 3D space.
    
    Args:
        point1: First point (x, y, z)
        point2: Second point (x, y, z)
        
    Returns:
        Distance between points
    """
    x1, y1, z1 = point1
    x2, y2, z2 = point2
    return np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2)


def normalize_point(point: Tuple[float, float], 
                    reference_length: float) -> Tuple[float, float]:
    """
    Normalize a point by a reference length.
    
    Args:
        point: Point to normalize (x, y)
        reference_length: Length to normalize by
        
    Returns:
        Normalized point (x, y)
    """
    if reference_length == 0:
        return point
    
    x, y = point
    return (x / reference_length, y / reference_length)


def calculate_lean_angle(top_point: Tuple[float, float], 
                        bottom_point: Tuple[float, float]) -> float:
    """
    Calculate lean angle from vertical (y-axis).
    
    Args:
        top_point: Upper reference point (x, y)
        bottom_point: Lower reference point (x, y)
        
    Returns:
        Angle in degrees from vertical. Positive = right, Negative = left
    """
    x_top, y_top = top_point
    x_bottom, y_bottom = bottom_point
    
    dx = x_top - x_bottom
    dy = y_bottom - y_top  # Invert because y increases downward in images
    
    if dy == 0:
        return 0.0
    
    angle_radians = np.arctan2(dx, dy)
    angle_degrees = np.degrees(angle_radians)
    
    return angle_degrees


