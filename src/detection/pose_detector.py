"""Pose detection using MediaPipe"""

import cv2
import mediapipe as mp
import numpy as np
from typing import Optional


class PoseDetector:
    """Wrapper for MediaPipe Pose detection"""
    
    def __init__(self, 
                 static_image_mode: bool = False,
                 model_complexity: int = 0,  # 0 = fastest, 1 = balanced, 2 = most accurate
                 smooth_landmarks: bool = True,
                 min_detection_confidence: float = 0.5,
                 min_tracking_confidence: float = 0.5):
        """
        Initialize MediaPipe Pose detector.
        
        Args:
            static_image_mode: If True, treats each image as independent
            model_complexity: Complexity of pose model (0, 1, or 2)
            smooth_landmarks: Whether to smooth landmarks across frames
            min_detection_confidence: Minimum confidence for person detection
            min_tracking_confidence: Minimum confidence for pose tracking
        """
        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        self.pose = self.mp_pose.Pose(
            static_image_mode=static_image_mode,
            model_complexity=model_complexity,
            smooth_landmarks=smooth_landmarks,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        
    def detect(self, frame: np.ndarray) -> Optional[object]:
        """
        Detect pose in a frame.
        
        Args:
            frame: BGR image from OpenCV
            
        Returns:
            Pose landmarks object if detected, None otherwise
        """
        if frame is None:
            return None
        
        # Convert BGR to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process the frame
        results = self.pose.process(rgb_frame)
        
        # Return landmarks if detected
        if results.pose_landmarks:
            return results.pose_landmarks
        
        return None
    
    def draw_landmarks(self, 
                       frame: np.ndarray, 
                       landmarks: object,
                       draw_connections: bool = True) -> np.ndarray:
        """
        Draw pose landmarks on frame.
        
        Args:
            frame: BGR image from OpenCV
            landmarks: Pose landmarks from detect()
            draw_connections: Whether to draw skeleton connections
            
        Returns:
            Frame with landmarks drawn
        """
        if landmarks is None:
            return frame
        
        # Create a copy to avoid modifying original
        annotated_frame = frame.copy()
        
        # Draw the pose landmarks
        if draw_connections:
            self.mp_drawing.draw_landmarks(
                annotated_frame,
                landmarks,
                self.mp_pose.POSE_CONNECTIONS,
                landmark_drawing_spec=self.mp_drawing_styles.get_default_pose_landmarks_style()
            )
        else:
            self.mp_drawing.draw_landmarks(
                annotated_frame,
                landmarks,
                None,
                landmark_drawing_spec=self.mp_drawing_styles.get_default_pose_landmarks_style()
            )
        
        return annotated_frame
    
    def close(self):
        """Release MediaPipe resources"""
        self.pose.close()
    
    def __del__(self):
        """Cleanup on object destruction"""
        try:
            self.close()
        except:
            pass


