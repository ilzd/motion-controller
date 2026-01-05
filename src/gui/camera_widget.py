"""Camera widget for displaying video feed with pose overlay"""

import cv2
import numpy as np
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap
from typing import Optional, Dict


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
        
        # Store detector references (shared, not created each frame)
        self.pose_detector = pose_detector
        self.hand_detector = None  # Will be set separately
        
        # Visibility flags for skeleton overlays
        self.show_pose_skeleton = True
        self.show_hand_skeleton = True
        
    def set_pose_detector(self, pose_detector):
        """Set the pose detector instance for drawing landmarks"""
        self.pose_detector = pose_detector
    
    def set_hand_detector(self, hand_detector):
        """Set the hand detector instance for drawing hand landmarks"""
        self.hand_detector = hand_detector
    
    def set_show_pose_skeleton(self, show: bool):
        """Enable or disable pose skeleton overlay"""
        self.show_pose_skeleton = show
    
    def set_show_hand_skeleton(self, show: bool):
        """Enable or disable hand skeleton overlay"""
        self.show_hand_skeleton = show
        
    def update_frame(self, frame: Optional[np.ndarray], 
                    landmarks: Optional[object] = None,
                    hands: Optional[Dict] = None):
        """
        Update the displayed frame.
        
        Args:
            frame: BGR image from OpenCV
            landmarks: Optional MediaPipe pose landmarks to draw
            hands: Optional hand detection results dictionary
        """
        if frame is None:
            return
        
        # Draw landmarks if provided (use shared detector instances)
        # Only copy frame if we need to draw landmarks
        display_frame = frame
        needs_copy = False
        
        if landmarks is not None and self.pose_detector is not None and self.show_pose_skeleton:
            needs_copy = True
        
        if hands is not None and self.hand_detector is not None and self.show_hand_skeleton:
            needs_copy = True
        
        if needs_copy:
            display_frame = frame.copy()
            
            # Draw pose landmarks
            if landmarks is not None and self.pose_detector is not None and self.show_pose_skeleton:
                display_frame = self.pose_detector.draw_landmarks(display_frame, landmarks)
            
            # Draw hand landmarks
            if hands is not None and self.hand_detector is not None and self.show_hand_skeleton:
                display_frame = self.hand_detector.draw_landmarks(display_frame, hands)
        
        # Convert to Qt format (use display_frame which may be original or annotated)
        frame_rgb = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
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
        # self.current_frame = None  # No longer storing frame reference


