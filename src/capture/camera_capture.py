"""Camera capture module for webcam input"""

import cv2
import numpy as np
from typing import Optional, Tuple


class CameraCapture:
    """Handles webcam video capture using OpenCV"""
    
    def __init__(self, camera_id: int = 0, resolution: Tuple[int, int] = (640, 480)):
        """
        Initialize camera capture.
        
        Args:
            camera_id: Camera device ID (default 0 for primary webcam)
            resolution: Desired resolution as (width, height)
        """
        self.camera_id = camera_id
        self.resolution = resolution
        self.capture: Optional[cv2.VideoCapture] = None
        self.is_running = False
        
    def start(self) -> bool:
        """
        Start camera capture.
        
        Returns:
            True if camera started successfully, False otherwise
        """
        if self.is_running:
            return True
            
        self.capture = cv2.VideoCapture(self.camera_id)
        
        if not self.capture.isOpened():
            return False
        
        # Set resolution
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])
        
        # Set FPS to 30
        self.capture.set(cv2.CAP_PROP_FPS, 30)
        
        self.is_running = True
        return True
    
    def stop(self):
        """Stop camera capture and release resources"""
        if self.capture is not None:
            self.capture.release()
            self.capture = None
        self.is_running = False
    
    def get_frame(self) -> Optional[np.ndarray]:
        """
        Capture a single frame from the camera.
        
        Returns:
            BGR image as numpy array, or None if capture failed
        """
        if not self.is_running or self.capture is None:
            return None
        
        ret, frame = self.capture.read()
        
        if not ret:
            return None
        
        return frame
    
    def get_frame_size(self) -> Optional[Tuple[int, int]]:
        """
        Get the actual frame size being captured.
        
        Returns:
            (width, height) tuple, or None if camera not started
        """
        if not self.is_running or self.capture is None:
            return None
        
        width = int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        return (width, height)
    
    def get_fps(self) -> Optional[float]:
        """
        Get the current FPS of the camera.
        
        Returns:
            FPS value, or None if camera not started
        """
        if not self.is_running or self.capture is None:
            return None
        
        return self.capture.get(cv2.CAP_PROP_FPS)
    
    def __del__(self):
        """Cleanup on object destruction"""
        self.stop()


