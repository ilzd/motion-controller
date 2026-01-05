"""Main application window"""

import sys
import time
import cv2
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                              QPushButton, QLabel, QFileDialog, QMessageBox,
                              QMenuBar, QMenu, QToolBar, QStatusBar, QCheckBox)
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QAction
from typing import Optional

from src.capture.camera_capture import CameraCapture
from src.detection.pose_detector import PoseDetector
from src.detection.hand_detector import HandDetector
from src.recognition.gesture_engine import GestureEngine
from src.actions.action_dispatcher import ActionDispatcher
from src.config.profile_manager import ProfileManager
from src.config.profile_schema import Profile
from src.gui.camera_widget import CameraWidget
from src.gui.gesture_monitor import GestureMonitor


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        """Initialize main window"""
        super().__init__()
        
        # Initialize components
        self.camera = CameraCapture()
        self.pose_detector = PoseDetector()
        self.hand_detector = HandDetector(max_num_hands=2)  # Detect both hands
        self.gesture_engine = GestureEngine()
        self.action_dispatcher = ActionDispatcher()
        self.profile_manager = ProfileManager()
        
        # State
        self.current_profile: Optional[Profile] = None
        self.is_running = False
        self.frame_count = 0
        self.fps = 0.0
        self.last_fps_update = time.time()
        self._camera_disconnect_warning_shown = False  # Prevent multiple disconnect dialogs
        
        # Setup UI
        self.setup_ui()
        
        # Setup processing timer
        from src.utils.constants import PROCESSING_TIMER_INTERVAL_MS
        self.processing_timer = QTimer()
        self.processing_timer.timeout.connect(self.process_frame)
        
        # Performance optimization: skip frame if still processing
        self.is_processing = False
        self.frame_skip_counter = 0
        
        # Load example profile if available
        self.try_load_example_profile()
    
    def setup_ui(self):
        """Setup the user interface"""
        self.setWindowTitle("Motion Controller")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create toolbar
        self.create_toolbar()
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Left panel - Camera feed (60% width)
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        left_panel.setLayout(left_layout)
        
        self.camera_widget = CameraWidget()
        self.camera_widget.set_pose_detector(self.pose_detector)
        self.camera_widget.set_hand_detector(self.hand_detector)
        left_layout.addWidget(self.camera_widget)
        
        # Right panel - Control panel (40% width)
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        right_panel.setLayout(right_layout)
        
        # Profile info
        profile_label = QLabel("Profile Information")
        profile_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        right_layout.addWidget(profile_label)
        
        self.profile_name_label = QLabel("No profile loaded")
        self.profile_name_label.setWordWrap(True)
        right_layout.addWidget(self.profile_name_label)
        
        # Gesture monitor
        self.gesture_monitor = GestureMonitor()
        right_layout.addWidget(self.gesture_monitor)
        
        # Status info
        status_label = QLabel("Status")
        status_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        right_layout.addWidget(status_label)
        
        self.fps_label = QLabel("FPS: 0")
        right_layout.addWidget(self.fps_label)
        
        self.status_label = QLabel("Camera: Stopped")
        right_layout.addWidget(self.status_label)
        
        # Skeleton visibility controls
        skeleton_label = QLabel("Skeleton Overlay")
        skeleton_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        right_layout.addWidget(skeleton_label)
        
        # Pose skeleton checkbox
        self.show_pose_checkbox = QCheckBox("Show Pose Skeleton")
        self.show_pose_checkbox.setChecked(True)
        self.show_pose_checkbox.toggled.connect(self.on_pose_skeleton_toggled)
        right_layout.addWidget(self.show_pose_checkbox)
        
        # Hand skeleton checkbox
        self.show_hand_checkbox = QCheckBox("Show Hand Skeleton")
        self.show_hand_checkbox.setChecked(True)
        self.show_hand_checkbox.toggled.connect(self.on_hand_skeleton_toggled)
        right_layout.addWidget(self.show_hand_checkbox)
        
        # Add stretch to push everything to top
        right_layout.addStretch()
        
        # Add panels to main layout with stretch factors
        main_layout.addWidget(left_panel, 60)
        main_layout.addWidget(right_panel, 40)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
    
    def create_menu_bar(self):
        """Create menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        load_action = QAction("&Load Profile", self)
        load_action.setShortcut("Ctrl+O")
        load_action.triggered.connect(self.load_profile)
        file_menu.addAction(load_action)
        
        save_action = QAction("&Save Profile", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_profile)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        new_profile_action = QAction("&New Profile", self)
        new_profile_action.setShortcut("Ctrl+N")
        new_profile_action.triggered.connect(self.new_profile)
        file_menu.addAction(new_profile_action)
        
        edit_profile_action = QAction("&Edit Profile", self)
        edit_profile_action.setShortcut("Ctrl+E")
        edit_profile_action.triggered.connect(self.edit_profile)
        file_menu.addAction(edit_profile_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def create_toolbar(self):
        """Create toolbar"""
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        # Start/Stop camera button
        self.start_stop_button = QPushButton("Start Camera")
        self.start_stop_button.clicked.connect(self.toggle_camera)
        # Prevent button from being triggered by keyboard shortcuts when camera is running
        self.start_stop_button.setAutoDefault(False)
        self.start_stop_button.setDefault(False)
        toolbar.addWidget(self.start_stop_button)
        
        toolbar.addSeparator()
        
        # Load profile button
        load_button = QPushButton("Load Profile")
        load_button.clicked.connect(self.load_profile)
        toolbar.addWidget(load_button)
    
    def toggle_camera(self):
        """Start or stop camera capture"""
        if not self.is_running:
            self.start_camera()
        else:
            self.stop_camera()
    
    def start_camera(self):
        """Start camera and processing"""
        if self.current_profile is None:
            QMessageBox.warning(self, "No Profile", 
                              "Please load a profile before starting the camera.")
            return
        
        # Start camera
        if self.camera.start():
            self.is_running = True
            self.start_stop_button.setText("Stop Camera")
            self.status_label.setText("Camera: Running")
            self.status_bar.showMessage("Camera started")
            
            # Reset processing state
            self.is_processing = False
            self.frame_count = 0
            self.frame_skip_counter = 0
            self.last_fps_update = time.time()
            
            # Prevent keyboard shortcuts from interfering with actions
            # Focus on the camera widget so buttons don't get keyboard events
            self.camera_widget.setFocus()
            
            # Start processing timer
            from src.utils.constants import PROCESSING_TIMER_INTERVAL_MS
            self.processing_timer.start(PROCESSING_TIMER_INTERVAL_MS)
        else:
            QMessageBox.critical(
                self, 
                "Camera Error", 
                "Failed to start camera.\n\n"
                "Possible causes:\n"
                "- Camera is already in use by another application\n"
                "- Camera is not connected\n"
                "- No camera permissions granted\n\n"
                "Please check your webcam and try again."
            )
    
    def stop_camera(self):
        """Stop camera and processing"""
        self.processing_timer.stop()
        self.camera.stop()
        self.is_running = False
        
        # Release all active actions
        self.action_dispatcher.release_all()
        
        self.start_stop_button.setText("Start Camera")
        self.status_label.setText("Camera: Stopped")
        self.status_bar.showMessage("Camera stopped")
        self.camera_widget.clear()
    
    def process_frame(self):
        """Process a single frame (called by timer)"""
        # Skip if still processing previous frame
        if self.is_processing:
            self.frame_skip_counter += 1
            return
        
        self.is_processing = True
        try:
            # 1. Capture frame
            frame = self.camera.get_frame()
            if frame is None:
                # Camera may have disconnected
                if not self.camera.is_running and not self._camera_disconnect_warning_shown:
                    self._camera_disconnect_warning_shown = True
                    self.stop_camera()
                    QMessageBox.warning(
                        self,
                        "Camera Disconnected",
                        "Camera was disconnected. Please reconnect and restart."
                    )
                self.is_processing = False
                return
            
            # Reset disconnect warning flag if camera is working
            if self._camera_disconnect_warning_shown and self.camera.is_running:
                self._camera_disconnect_warning_shown = False
            
            # Flip frame horizontally for mirror-like display (more intuitive for testing)
            frame = cv2.flip(frame, 1)
            
            # 2. Detect pose and hands
            landmarks = self.pose_detector.detect(frame)
            hands = self.hand_detector.detect(frame)
            
            # 3. Recognize gestures and execute actions
            # Prepare frame data with both pose and hands for triggers that need hand data
            frame_data = {
                "hands": hands,
                "frame": frame
            }
            
            if landmarks is not None:
                try:
                    active_gestures = self.gesture_engine.process(landmarks, frame_data)
                    self.action_dispatcher.dispatch(active_gestures)
                    
                    # Update gesture monitor (throttled for performance)
                    from src.utils.constants import GESTURE_MONITOR_UPDATE_INTERVAL
                    if self.frame_count % GESTURE_MONITOR_UPDATE_INTERVAL == 0:
                        self.gesture_monitor.update_status(active_gestures)
                except Exception as e:
                    print(f"Warning: Error processing gestures: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                # No person detected - release all actions
                try:
                    self.action_dispatcher.release_all()
                except Exception as e:
                    print(f"Warning: Error releasing actions: {e}")
            
            # 4. Update GUI with pose and hands
            self.camera_widget.update_frame(frame, landmarks, hands)
            
            # Update FPS
            self.frame_count += 1
            current_time = time.time()
            if current_time - self.last_fps_update >= 1.0:
                self.fps = self.frame_count / (current_time - self.last_fps_update)
                self.fps_label.setText(f"FPS: {self.fps:.1f}")
                from src.utils.constants import MAX_FRAME_SKIP_COUNT
                if self.frame_skip_counter > 0:
                    if self.frame_skip_counter > MAX_FRAME_SKIP_COUNT:
                        self.status_bar.showMessage(
                            f"FPS: {self.fps:.1f} (Warning: Skipped {self.frame_skip_counter} frames - performance degraded)",
                            5000  # Show for 5 seconds
                        )
                    else:
                        self.status_bar.showMessage(f"FPS: {self.fps:.1f} (Skipped {self.frame_skip_counter} frames")
                self.frame_count = 0
                self.frame_skip_counter = 0
                self.last_fps_update = current_time
                
        except Exception as e:
            print(f"Error processing frame: {e}")
            import traceback
            traceback.print_exc()
            # Ensure processing flag is reset even on error
            self.is_processing = False
            # Don't let errors stop the camera - continue processing
        finally:
            # Always reset processing flag
            if self.is_processing:
                self.is_processing = False
    
    def load_profile(self):
        """Load a profile from file"""
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "Load Profile",
            "profiles",
            "YAML Files (*.yaml *.yml)"
        )
        
        if filepath:
            profile = self.profile_manager.load_profile(filepath)
            if profile:
                self.set_profile(profile)
                self.status_bar.showMessage(f"Loaded profile: {profile.name}")
            else:
                QMessageBox.critical(self, "Error", "Failed to load profile")
    
    def save_profile(self):
        """Save current profile to file"""
        if self.current_profile is None:
            QMessageBox.warning(self, "No Profile", "No profile to save")
            return
        
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Save Profile",
            "profiles",
            "YAML Files (*.yaml)"
        )
        
        if filepath:
            if self.profile_manager.save_profile(self.current_profile, filepath):
                self.status_bar.showMessage(f"Saved profile: {self.current_profile.name}")
            else:
                QMessageBox.critical(self, "Error", "Failed to save profile")
    
    def set_profile(self, profile: Profile):
        """Set the current profile"""
        # Stop camera if running
        was_running = self.is_running
        if was_running:
            self.stop_camera()
        
        self.current_profile = profile
        
        # Update UI
        self.profile_name_label.setText(
            f"<b>{profile.name}</b><br>"
            f"{profile.description}<br>"
            f"Game: {profile.game}"
        )
        
        # Load gestures into engine
        gestures_config = [g.model_dump() for g in profile.gestures]
        self.gesture_engine.load_gestures(gestures_config)
        
        # Update gesture monitor
        gesture_names = self.gesture_engine.get_gesture_names()
        self.gesture_monitor.set_gestures(gesture_names)
        
        # Restart camera if it was running
        if was_running:
            self.start_camera()
    
    def try_load_example_profile(self):
        """Try to load the example profile on startup"""
        example_path = self.profile_manager.get_profile_path("example_profile")
        profile = self.profile_manager.load_profile(example_path)
        if profile:
            self.set_profile(profile)
    
    def new_profile(self):
        """Create a new profile"""
        from src.gui.profile_editor import ProfileEditor
        from src.config.profile_schema import Profile
        
        # Create empty profile
        new_profile = Profile(name="New Profile", description="", game="", gestures=[])
        
        dialog = ProfileEditor(new_profile, self)
        if dialog.exec() == ProfileEditor.DialogCode.Accepted:
            profile = dialog.get_profile()
            self.set_profile(profile)
            self.status_bar.showMessage(f"Created new profile: {profile.name}")
    
    def edit_profile(self):
        """Edit the current profile"""
        from src.gui.profile_editor import ProfileEditor
        
        if self.current_profile is None:
            QMessageBox.warning(self, "No Profile", "No profile to edit. Please load or create a profile first.")
            return
        
        dialog = ProfileEditor(self.current_profile, self)
        if dialog.exec() == ProfileEditor.DialogCode.Accepted:
            profile = dialog.get_profile()
            self.set_profile(profile)
            self.status_bar.showMessage(f"Updated profile: {profile.name}")
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "About Motion Controller",
            "<h2>Motion Controller</h2>"
            "<p>Version 0.1.0</p>"
            "<p>Control games with body movements using your webcam.</p>"
            "<p>Built with MediaPipe, OpenCV, and PyQt6</p>"
        )
    
    def on_pose_skeleton_toggled(self, checked: bool):
        """Handle pose skeleton visibility toggle"""
        self.camera_widget.set_show_pose_skeleton(checked)
    
    def on_hand_skeleton_toggled(self, checked: bool):
        """Handle hand skeleton visibility toggle"""
        self.camera_widget.set_show_hand_skeleton(checked)
    
    def closeEvent(self, event):
        """Handle window close event"""
        if self.is_running:
            self.stop_camera()
        
        # Cleanup
        self.pose_detector.close()
        self.hand_detector.close()
        
        event.accept()

