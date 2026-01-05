"""Pose hold trigger - detects holding a pose for a duration"""

import time
from typing import Dict, Any
from src.recognition.base_trigger import BaseTrigger
from src.recognition.trigger_registry import TriggerRegistry


@TriggerRegistry.register("pose_hold")
class PoseHoldTrigger(BaseTrigger):
    """Detects when another trigger is held for a specified duration"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize pose hold trigger.
        
        Config parameters:
            trigger: Nested trigger configuration (dict with 'type' and 'params')
            duration_ms: Duration in milliseconds to hold (default 1000)
        """
        super().__init__(config)
        self.duration_ms = self.get_config_param("duration_ms", 1000)
        self.inner_trigger_config = self.get_config_param("trigger", {})
        
        # Create the inner trigger
        self.inner_trigger = None
        if self.inner_trigger_config:
            trigger_type = self.inner_trigger_config.get("type")
            trigger_params = self.inner_trigger_config.get("params", {})
            if trigger_type:
                self.inner_trigger = TriggerRegistry.create(trigger_type, trigger_params)
        
        self.hold_start_time = None
        self.hold_elapsed_ms = 0
        
    def detect(self, landmarks: object, frame_data: Dict[str, Any]) -> bool:
        """Detect if inner trigger is held for duration"""
        if self.inner_trigger is None or landmarks is None:
            self.is_active = False
            self.current_value = 0.0
            self.hold_start_time = None
            return False
        
        # Check inner trigger
        inner_active = self.inner_trigger.detect(landmarks, frame_data)
        current_time = time.time() * 1000  # Convert to milliseconds
        
        if inner_active:
            # Start timing if not already started
            if self.hold_start_time is None:
                self.hold_start_time = current_time
            
            # Calculate elapsed time
            self.hold_elapsed_ms = current_time - self.hold_start_time
            
            # Update value (0.0 to 1.0 based on progress)
            self.current_value = min(1.0, self.hold_elapsed_ms / self.duration_ms)
            
            # Trigger activates once duration is reached
            self.is_active = self.hold_elapsed_ms >= self.duration_ms
        else:
            # Reset if inner trigger deactivated
            self.hold_start_time = None
            self.hold_elapsed_ms = 0
            self.current_value = 0.0
            self.is_active = False
        
        return self.is_active
    
    def get_value(self) -> float:
        """Get trigger value (0.0-1.0 representing hold progress)"""
        return self.current_value
    
    def get_name(self) -> str:
        """Get trigger type name"""
        return "pose_hold"
    
    def reset(self):
        """Reset trigger state"""
        super().reset()
        self.hold_start_time = None
        self.hold_elapsed_ms = 0
        if self.inner_trigger:
            self.inner_trigger.reset()


