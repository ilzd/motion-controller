"""Gesture monitor widget showing real-time gesture status"""

from PyQt6.QtWidgets import (QWidget, QTableWidget, QTableWidgetItem, 
                              QVBoxLayout, QHeaderView, QLabel)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from typing import List, Tuple, Dict
from src.actions.base_action import BaseAction


class GestureMonitor(QWidget):
    """Widget for displaying active gestures in real-time"""
    
    def __init__(self, parent=None):
        """Initialize gesture monitor"""
        super().__init__(parent)
        
        # Create title label
        title_label = QLabel("Active Gestures")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        
        # Create table
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Gesture", "Status", "Value"])
        
        # Configure table
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        
        # Layout
        layout = QVBoxLayout()
        layout.addWidget(title_label)
        layout.addWidget(self.table)
        self.setLayout(layout)
        
        # Store gesture data
        self.gesture_rows: Dict[str, int] = {}
        
    def set_gestures(self, gesture_names: List[str]):
        """
        Initialize the table with gesture names.
        
        Args:
            gesture_names: List of gesture names to display
        """
        self.table.setRowCount(len(gesture_names))
        self.gesture_rows.clear()
        
        for i, name in enumerate(gesture_names):
            self.gesture_rows[name] = i
            
            # Gesture name
            name_item = QTableWidgetItem(name)
            self.table.setItem(i, 0, name_item)
            
            # Status
            status_item = QTableWidgetItem("Inactive")
            status_item.setBackground(QColor(200, 200, 200))
            self.table.setItem(i, 1, status_item)
            
            # Value
            value_item = QTableWidgetItem("0%")
            self.table.setItem(i, 2, value_item)
    
    def update_status(self, active_gestures: List[Tuple[str, BaseAction, bool, float]]):
        """
        Update the status of gestures.
        
        Args:
            active_gestures: List of (gesture_name, action, is_active, trigger_value) tuples
        """
        # First, mark all as inactive
        for row in range(self.table.rowCount()):
            status_item = self.table.item(row, 1)
            value_item = self.table.item(row, 2)
            
            if status_item:
                status_item.setText("Inactive")
                status_item.setBackground(QColor(200, 200, 200))
            
            if value_item:
                value_item.setText("0%")
        
        # Update active gestures
        for gesture_name, action, is_active, trigger_value in active_gestures:
            if gesture_name in self.gesture_rows:
                row = self.gesture_rows[gesture_name]
                
                # Validate row index
                if row < 0 or row >= self.table.rowCount():
                    continue
                
                status_item = self.table.item(row, 1)
                value_item = self.table.item(row, 2)
                
                if status_item:
                    if is_active:
                        status_item.setText("Active")
                        status_item.setBackground(QColor(100, 255, 100))
                    else:
                        status_item.setText("Inactive")
                        status_item.setBackground(QColor(200, 200, 200))
                
                if value_item:
                    # Update value
                    value_percent = int(trigger_value * 100)
                    value_item.setText(f"{value_percent}%")
    
    def clear(self):
        """Clear all gesture data"""
        self.table.setRowCount(0)
        self.gesture_rows.clear()


