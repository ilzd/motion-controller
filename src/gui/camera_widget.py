"""Camera widget for displaying video feed with pose overlay"""

import cv2
import numpy as np
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap
from typing import Optional


class CameraWidget(QWidget):
    """Widget for displaying camera feed with pose landmarks"""
    
    def __init__(self, parent=None, pose_detector=None):
        """
        Initialize camera widget.
        
        Args:
            parent: Parent widget
            pose_detector: Shared PoseDetector instance (for drawing landmarks)
        """
        super().__init__(parent)
        
        # Create label to display video
        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setStyleSheet("background-color: black;")
        self.video_label.setMinimumSize(640, 480)
        
        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.video_label)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        
        # Store current frame
        self.current_frame = None
        
        # Store pose detector reference (shared, not created each frame)
        self.pose_detector = pose_detector
        
    def set_pose_detector(self, pose_detector):
        """Set the pose detector instance for drawing landmarks"""
        self.pose_detector = pose_detector
        
    def update_frame(self, frame: Optional[np.ndarray], landmarks: Optional[object] = None):
        """
        Update the displayed frame.
        
        Args:
            frame: BGR image from OpenCV
            landmarks: Optional MediaPipe pose landmarks to draw
        """
        if frame is None:
            return
        
        # Store frame
        self.current_frame = frame.copy()
        
        # Draw landmarks if provided (use shared detector instance)
        if landmarks is not None and self.pose_detector is not None:
            frame = self.pose_detector.draw_landmarks(frame.copy(), landmarks)
        
        # Convert to Qt format
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame_rgb.shape
        bytes_per_line = ch * w
        
        qt_image = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        
        # Scale to fit widget while maintaining aspect ratio
        scaled_pixmap = QPixmap.fromImage(qt_image).scaled(
            self.video_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        
        self.video_label.setPixmap(scaled_pixmap)
    
    def clear(self):
        """Clear the video display"""
        self.video_label.clear()
        self.video_label.setText("No camera feed")
        self.current_frame = None


