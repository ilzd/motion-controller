"""Profile editor dialog for creating and editing profiles"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                              QLineEdit, QTextEdit, QPushButton, QListWidget,
                              QListWidgetItem, QGroupBox, QFormLayout, 
                              QComboBox, QSpinBox, QDoubleSpinBox, QMessageBox,
                              QCheckBox, QScrollArea, QWidget, QSizePolicy, QApplication)
from PyQt6.QtCore import Qt
from typing import Optional, Dict, Any

from src.config.profile_schema import Profile, GestureConfig, TriggerConfig, ActionConfig
from src.recognition.trigger_registry import TriggerRegistry
from src.actions.action_registry import ActionRegistry


class GestureEditorDialog(QDialog):
    """Dialog for editing a single gesture"""
    
    def __init__(self, gesture: Optional[GestureConfig] = None, parent=None):
        """
        Initialize gesture editor dialog.
        
        Args:
            gesture: Existing gesture to edit, or None to create new
            parent: Parent widget
        """
        super().__init__(parent)
        self.gesture = gesture
        self.setWindowTitle("Edit Gesture" if gesture else "New Gesture")
        self.setModal(True)
        self.setMinimumSize(550, 700)
        self.resize(550, 700)
        
        self.scroll_area = None
        self.content_widget = None
        
        self.setup_ui()
        
        if gesture:
            self.load_gesture(gesture)
    
    def setup_ui(self):
        """Setup the user interface"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        self.setLayout(main_layout)
        
        # Create scroll area for content
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setMinimumHeight(500)
        
        # Create content widget
        self.content_widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        self.content_widget.setLayout(layout)
        
        # Gesture name
        name_group = QGroupBox("Gesture Name")
        name_layout = QFormLayout()
        name_group.setLayout(name_layout)
        
        self.name_input = QLineEdit()
        name_layout.addRow("Name:", self.name_input)
        
        self.enabled_checkbox = QCheckBox("Enabled")
        self.enabled_checkbox.setChecked(True)
        name_layout.addRow("", self.enabled_checkbox)
        
        layout.addWidget(name_group)
        
        # Trigger configuration
        trigger_group = QGroupBox("Trigger")
        trigger_layout = QVBoxLayout()
        trigger_layout.setSpacing(5)
        trigger_group.setLayout(trigger_layout)
        
        # Trigger type label and combo - ensure they stay visible
        trigger_type_label = QLabel("Trigger Type:")
        trigger_type_label.setMinimumHeight(20)
        trigger_layout.addWidget(trigger_type_label)
        
        self.trigger_type_combo = QComboBox()
        self.trigger_type_combo.addItems(TriggerRegistry.get_available_triggers())
        self.trigger_type_combo.currentTextChanged.connect(self.on_trigger_type_changed)
        self.trigger_type_combo.setMinimumHeight(30)  # Ensure minimum height
        self.trigger_type_combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        trigger_layout.addWidget(self.trigger_type_combo)
        
        # Add some spacing
        trigger_layout.addSpacing(5)
        
        # Parameters layout - this is what gets cleared/rebuilt
        self.trigger_params_layout = QFormLayout()
        self.trigger_params_layout.setSpacing(5)
        trigger_params_widget = QWidget()
        trigger_params_widget.setLayout(self.trigger_params_layout)
        trigger_layout.addWidget(trigger_params_widget)
        
        layout.addWidget(trigger_group)
        
        # Action configuration
        action_group = QGroupBox("Action")
        action_layout = QVBoxLayout()
        action_layout.setSpacing(5)
        action_group.setLayout(action_layout)
        
        # Action type label and combo - ensure they stay visible
        action_type_label = QLabel("Action Type:")
        action_type_label.setMinimumHeight(20)
        action_layout.addWidget(action_type_label)
        
        self.action_type_combo = QComboBox()
        self.action_type_combo.addItems(ActionRegistry.get_available_actions())
        self.action_type_combo.currentTextChanged.connect(self.on_action_type_changed)
        self.action_type_combo.setMinimumHeight(30)  # Ensure minimum height
        self.action_type_combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        action_layout.addWidget(self.action_type_combo)
        
        # Add some spacing
        action_layout.addSpacing(5)
        
        # Parameters layout - this is what gets cleared/rebuilt
        self.action_params_layout = QFormLayout()
        self.action_params_layout.setSpacing(5)
        action_params_widget = QWidget()
        action_params_widget.setLayout(self.action_params_layout)
        action_layout.addWidget(action_params_widget)
        
        layout.addWidget(action_group)
        
        # Set size policy for content widget to allow proper sizing
        size_policy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
        self.content_widget.setSizePolicy(size_policy)
        
        # Set content widget to scroll area
        self.scroll_area.setWidget(self.content_widget)
        main_layout.addWidget(self.scroll_area)
        
        # Buttons (outside scroll area)
        button_layout = QHBoxLayout()
        
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.accept)
        button_layout.addWidget(save_button)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        main_layout.addLayout(button_layout)
        
        # Initialize parameter forms
        self.on_trigger_type_changed(self.trigger_type_combo.currentText())
        self.on_action_type_changed(self.action_type_combo.currentText())
    
    def on_trigger_type_changed(self, trigger_type: str):
        """Handle trigger type change"""
        # Clear existing parameters
        self.clear_layout(self.trigger_params_layout)
        
        # Add parameters based on trigger type
        if trigger_type == "hand_raise":
            self.add_trigger_param("hand", QComboBox(), ["right", "left", "both"])
            self.add_trigger_param("threshold", QDoubleSpinBox(), (0.0, 1.0, 0.2))
        elif trigger_type == "body_lean":
            self.add_trigger_param("direction", QComboBox(), ["forward", "back", "left", "right"])
            self.add_trigger_param("threshold", QSpinBox(), (0, 90, 15))
        elif trigger_type == "pose_hold":
            self.add_trigger_param("duration_ms", QSpinBox(), (100, 10000, 1000))
            # Note: Nested trigger not supported in simple editor
        elif trigger_type == "hand_gesture":
            self.add_trigger_param("hand", QComboBox(), ["right", "left", "both"])
            self.add_trigger_param("gesture", QComboBox(), ["open", "closed"])
            self.add_trigger_param("confidence", QDoubleSpinBox(), (0.0, 1.0, 0.7))
        
        # Update content widget size
        self.update_content_size()
    
    def on_action_type_changed(self, action_type: str):
        """Handle action type change"""
        # Clear existing parameters
        self.clear_layout(self.action_params_layout)
        
        # Add parameters based on action type
        if action_type == "keyboard":
            self.add_action_param("key", QLineEdit(), "space")
            self.add_action_param("mode", QComboBox(), ["press", "hold"])
        elif action_type == "mouse":
            self.add_action_param("action", QComboBox(), ["click", "hold", "move"])
            self.add_action_param("button", QComboBox(), ["left", "right", "middle"])
        elif action_type == "gamepad":
            controls = ["button_a", "button_b", "button_x", "button_y", 
                       "left_bumper", "right_bumper", "left_stick_x", "left_stick_y",
                       "right_stick_x", "right_stick_y", "left_trigger", "right_trigger"]
            self.add_action_param("control", QComboBox(), controls)
            self.add_action_param("value", QDoubleSpinBox(), (-1.0, 1.0, 1.0))
        
        # Update content widget size
        self.update_content_size()
    
    def add_trigger_param(self, name: str, widget, default_value):
        """Add a trigger parameter widget"""
        if isinstance(widget, QComboBox) and isinstance(default_value, list):
            widget.addItems(default_value)
        elif isinstance(widget, QSpinBox) and isinstance(default_value, tuple):
            widget.setMinimum(default_value[0])
            widget.setMaximum(default_value[1])
            widget.setValue(default_value[2])
        elif isinstance(widget, QDoubleSpinBox) and isinstance(default_value, tuple):
            widget.setMinimum(default_value[0])
            widget.setMaximum(default_value[1])
            widget.setValue(default_value[2])
            widget.setDecimals(2)
            widget.setSingleStep(0.1)
        elif isinstance(widget, QLineEdit):
            widget.setText(str(default_value))
        
        self.trigger_params_layout.addRow(f"{name}:", widget)
    
    def add_action_param(self, name: str, widget, default_value):
        """Add an action parameter widget"""
        if isinstance(widget, QComboBox) and isinstance(default_value, list):
            widget.addItems(default_value)
        elif isinstance(widget, QSpinBox) and isinstance(default_value, tuple):
            widget.setMinimum(default_value[0])
            widget.setMaximum(default_value[1])
            widget.setValue(default_value[2])
        elif isinstance(widget, QDoubleSpinBox) and isinstance(default_value, tuple):
            widget.setMinimum(default_value[0])
            widget.setMaximum(default_value[1])
            widget.setValue(default_value[2])
            widget.setDecimals(2)
            widget.setSingleStep(0.1)
        elif isinstance(widget, QLineEdit):
            widget.setText(str(default_value))
        
        self.action_params_layout.addRow(f"{name}:", widget)
    
    def clear_layout(self, layout):
        """Clear all widgets from a layout"""
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                widget = item.widget()
                # Don't delete if it's a label or combo box that should stay
                if not isinstance(widget, (QLabel, QComboBox)):
                    widget.deleteLater()
            elif item.layout():
                # Recursively clear nested layouts
                self.clear_layout(item.layout())
    
    def update_content_size(self):
        """Update the content widget size to fit its contents"""
        if self.content_widget and self.scroll_area:
            # Force layout update
            self.content_widget.layout().update()
            # Update size hint - this ensures the widget knows its proper size
            self.content_widget.adjustSize()
            # Get the size hint and set minimum size
            size_hint = self.content_widget.sizeHint()
            if size_hint.isValid():
                # Set minimum height to ensure all content is accessible
                current_min = self.content_widget.minimumSize()
                self.content_widget.setMinimumSize(
                    max(current_min.width(), size_hint.width()),
                    max(current_min.height(), size_hint.height())
                )
            # Ensure scroll area updates its viewport
            self.scroll_area.updateGeometry()
            # Process events to allow UI to update immediately
            QApplication.processEvents()
    
    def load_gesture(self, gesture: GestureConfig):
        """Load gesture data into the form"""
        self.name_input.setText(gesture.name)
        self.enabled_checkbox.setChecked(gesture.enabled)
        
        # Temporarily disconnect signals to prevent layout changes during loading
        self.trigger_type_combo.blockSignals(True)
        self.action_type_combo.blockSignals(True)
        
        try:
            # First, set the combo box indices WITHOUT triggering signals
            trigger_index = self.trigger_type_combo.findText(gesture.trigger.type)
            if trigger_index >= 0:
                self.trigger_type_combo.setCurrentIndex(trigger_index)
            
            action_index = self.action_type_combo.findText(gesture.action.type)
            if action_index >= 0:
                self.action_type_combo.setCurrentIndex(action_index)
            
            # Now manually rebuild the parameter layouts
            self.on_trigger_type_changed(gesture.trigger.type)
            self.on_action_type_changed(gesture.action.type)
            
            # Set trigger parameters after layout is rebuilt
            for i in range(self.trigger_params_layout.rowCount()):
                label = self.trigger_params_layout.itemAt(i, QFormLayout.ItemRole.LabelRole)
                if label:
                    param_name = label.widget().text().rstrip(':')
                    widget = self.trigger_params_layout.itemAt(i, QFormLayout.ItemRole.FieldRole).widget()
                    value = gesture.trigger.params.get(param_name)
                    
                    if isinstance(widget, QComboBox) and value:
                        index = widget.findText(str(value))
                        if index >= 0:
                            widget.setCurrentIndex(index)
                    elif isinstance(widget, (QSpinBox, QDoubleSpinBox)) and value is not None:
                        widget.setValue(value)
                    elif isinstance(widget, QLineEdit) and value:
                        widget.setText(str(value))
            
            # Set action parameters after layout is rebuilt
            for i in range(self.action_params_layout.rowCount()):
                label = self.action_params_layout.itemAt(i, QFormLayout.ItemRole.LabelRole)
                if label:
                    param_name = label.widget().text().rstrip(':')
                    widget = self.action_params_layout.itemAt(i, QFormLayout.ItemRole.FieldRole).widget()
                    value = gesture.action.params.get(param_name)
                    
                    if isinstance(widget, QComboBox) and value:
                        index = widget.findText(str(value))
                        if index >= 0:
                            widget.setCurrentIndex(index)
                    elif isinstance(widget, (QSpinBox, QDoubleSpinBox)) and value is not None:
                        widget.setValue(value)
                    elif isinstance(widget, QLineEdit) and value:
                        widget.setText(str(value))
        finally:
            # Re-enable signals
            self.trigger_type_combo.blockSignals(False)
            self.action_type_combo.blockSignals(False)
        
        # Force layout update and ensure combo boxes are visible and properly sized
        QApplication.processEvents()  # Process any pending events first
        
        # Explicitly ensure combo boxes are visible and have proper size
        self.trigger_type_combo.setVisible(True)
        self.trigger_type_combo.show()
        self.action_type_combo.setVisible(True)
        self.action_type_combo.show()
        
        # Force update of all layouts
        self.content_widget.layout().update()
        self.trigger_type_combo.parent().layout().update()
        self.action_type_combo.parent().layout().update()
        
        # Update content widget size after loading
        self.update_content_size()
        
        # Ensure dialog is large enough
        self.resize(550, 700)
        
        # Process events again to ensure UI updates
        QApplication.processEvents()
        
        # Scroll to top to ensure all content is accessible
        if self.scroll_area:
            self.scroll_area.verticalScrollBar().setValue(0)
            QApplication.processEvents()
    
    def get_gesture(self) -> GestureConfig:
        """Get the edited gesture configuration"""
        # Get trigger parameters
        trigger_params = {}
        for i in range(self.trigger_params_layout.rowCount()):
            label = self.trigger_params_layout.itemAt(i, QFormLayout.ItemRole.LabelRole)
            if label:
                param_name = label.widget().text().rstrip(':')
                widget = self.trigger_params_layout.itemAt(i, QFormLayout.ItemRole.FieldRole).widget()
                
                if isinstance(widget, QComboBox):
                    trigger_params[param_name] = widget.currentText()
                elif isinstance(widget, (QSpinBox, QDoubleSpinBox)):
                    trigger_params[param_name] = widget.value()
                elif isinstance(widget, QLineEdit):
                    trigger_params[param_name] = widget.text()
        
        # Get action parameters
        action_params = {}
        for i in range(self.action_params_layout.rowCount()):
            label = self.action_params_layout.itemAt(i, QFormLayout.ItemRole.LabelRole)
            if label:
                param_name = label.widget().text().rstrip(':')
                widget = self.action_params_layout.itemAt(i, QFormLayout.ItemRole.FieldRole).widget()
                
                if isinstance(widget, QComboBox):
                    action_params[param_name] = widget.currentText()
                elif isinstance(widget, (QSpinBox, QDoubleSpinBox)):
                    action_params[param_name] = widget.value()
                elif isinstance(widget, QLineEdit):
                    action_params[param_name] = widget.text()
        
        return GestureConfig(
            name=self.name_input.text(),
            enabled=self.enabled_checkbox.isChecked(),
            trigger=TriggerConfig(
                type=self.trigger_type_combo.currentText(),
                params=trigger_params
            ),
            action=ActionConfig(
                type=self.action_type_combo.currentText(),
                params=action_params
            )
        )


class ProfileEditor(QDialog):
    """Dialog for editing a complete profile"""
    
    def __init__(self, profile: Optional[Profile] = None, parent=None):
        """
        Initialize profile editor.
        
        Args:
            profile: Existing profile to edit, or None to create new
            parent: Parent widget
        """
        super().__init__(parent)
        self.profile = profile if profile else Profile(name="New Profile", gestures=[])
        self.setWindowTitle(f"Edit Profile: {self.profile.name}")
        self.setModal(True)
        self.resize(700, 600)
        
        self.setup_ui()
        self.load_profile()
    
    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Profile metadata
        metadata_group = QGroupBox("Profile Information")
        metadata_layout = QFormLayout()
        metadata_group.setLayout(metadata_layout)
        
        self.name_input = QLineEdit()
        metadata_layout.addRow("Name:", self.name_input)
        
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(60)
        metadata_layout.addRow("Description:", self.description_input)
        
        self.game_input = QLineEdit()
        metadata_layout.addRow("Game:", self.game_input)
        
        layout.addWidget(metadata_group)
        
        # Gestures list
        gestures_group = QGroupBox("Gestures")
        gestures_layout = QVBoxLayout()
        gestures_group.setLayout(gestures_layout)
        
        self.gestures_list = QListWidget()
        gestures_layout.addWidget(self.gestures_list)
        
        # Gesture buttons
        gesture_buttons_layout = QHBoxLayout()
        
        add_button = QPushButton("Add Gesture")
        add_button.clicked.connect(self.add_gesture)
        gesture_buttons_layout.addWidget(add_button)
        
        edit_button = QPushButton("Edit Gesture")
        edit_button.clicked.connect(self.edit_gesture)
        gesture_buttons_layout.addWidget(edit_button)
        
        remove_button = QPushButton("Remove Gesture")
        remove_button.clicked.connect(self.remove_gesture)
        gesture_buttons_layout.addWidget(remove_button)
        
        gestures_layout.addLayout(gesture_buttons_layout)
        
        layout.addWidget(gestures_group)
        
        # Dialog buttons
        button_layout = QHBoxLayout()
        
        save_button = QPushButton("Save Profile")
        save_button.clicked.connect(self.accept)
        button_layout.addWidget(save_button)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
    
    def load_profile(self):
        """Load profile data into the form"""
        self.name_input.setText(self.profile.name)
        self.description_input.setPlainText(self.profile.description)
        self.game_input.setText(self.profile.game)
        
        self.update_gestures_list()
    
    def update_gestures_list(self):
        """Update the gestures list widget"""
        self.gestures_list.clear()
        for gesture in self.profile.gestures:
            status = "✓" if gesture.enabled else "✗"
            item = QListWidgetItem(f"{status} {gesture.name}")
            item.setData(Qt.ItemDataRole.UserRole, gesture)
            self.gestures_list.addItem(item)
    
    def add_gesture(self):
        """Add a new gesture"""
        dialog = GestureEditorDialog(parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            gesture = dialog.get_gesture()
            self.profile.gestures.append(gesture)
            self.update_gestures_list()
    
    def edit_gesture(self):
        """Edit selected gesture"""
        current_item = self.gestures_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Selection", "Please select a gesture to edit")
            return
        
        gesture = current_item.data(Qt.ItemDataRole.UserRole)
        dialog = GestureEditorDialog(gesture, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            updated_gesture = dialog.get_gesture()
            index = self.profile.gestures.index(gesture)
            self.profile.gestures[index] = updated_gesture
            self.update_gestures_list()
    
    def remove_gesture(self):
        """Remove selected gesture"""
        current_item = self.gestures_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Selection", "Please select a gesture to remove")
            return
        
        gesture = current_item.data(Qt.ItemDataRole.UserRole)
        reply = QMessageBox.question(
            self,
            "Confirm Removal",
            f"Remove gesture '{gesture.name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.profile.gestures.remove(gesture)
            self.update_gestures_list()
    
    def get_profile(self) -> Profile:
        """Get the edited profile"""
        self.profile.name = self.name_input.text()
        self.profile.description = self.description_input.toPlainText()
        self.profile.game = self.game_input.text()
        return self.profile


