"""Gesture recognition engine that coordinates triggers and actions"""

import time
from typing import List, Tuple, Optional, Dict, Any
from src.recognition.trigger_registry import TriggerRegistry
from src.actions.action_registry import ActionRegistry
from src.recognition.base_trigger import BaseTrigger
from src.actions.base_action import BaseAction


class GestureDefinition:
    """Represents a single gesture with trigger and action"""
    
    def __init__(self, name: str, trigger: BaseTrigger, action: BaseAction):
        """
        Initialize gesture definition.
        
        Args:
            name: Human-readable name for the gesture
            trigger: Trigger instance that detects the gesture
            action: Action instance to execute when triggered
        """
        self.name = name
        self.trigger = trigger
        self.action = action
        self.last_triggered_time = None
        

class GestureEngine:
    """Manages gesture recognition and coordinates triggers"""
    
    def __init__(self):
        """Initialize gesture engine"""
        self.gestures: List[GestureDefinition] = []
        self.frame_number = 0
        
    def load_gestures(self, gestures_config: List[Dict[str, Any]]):
        """
        Load gestures from configuration.
        
        Args:
            gestures_config: List of gesture configuration dictionaries
                Each containing: {name, trigger: {type, params}, action: {type, params}}
        """
        self.gestures.clear()
        
        for gesture_config in gestures_config:
            try:
                name = gesture_config.get("name", "Unnamed")
                
                # Create trigger
                trigger_config = gesture_config.get("trigger", {})
                trigger_type = trigger_config.get("type")
                trigger_params = trigger_config.get("params", {})
                trigger = TriggerRegistry.create(trigger_type, trigger_params)
                
                # Create action
                action_config = gesture_config.get("action", {})
                action_type = action_config.get("type")
                action_params = action_config.get("params", {})
                action = ActionRegistry.create(action_type, action_params)
                
                # Add gesture
                gesture_def = GestureDefinition(name, trigger, action)
                self.gestures.append(gesture_def)
                
            except KeyError as e:
                print(f"Error: Failed to load gesture '{gesture_config.get('name', 'unknown')}': "
                      f"Missing required field: {e}")
            except Exception as e:
                print(f"Warning: Failed to load gesture '{gesture_config.get('name', 'unknown')}': {e}")
                import traceback
                traceback.print_exc()
    
    def process(self, landmarks: object, additional_data: Optional[Dict[str, Any]] = None) -> List[Tuple[str, BaseAction, bool, float]]:
        """
        Process a frame and detect active gestures.
        
        Args:
            landmarks: MediaPipe pose landmarks
            additional_data: Additional frame data (optional)
            
        Returns:
            List of tuples: (gesture_name, action, is_active, trigger_value)
        """
        if additional_data is None:
            additional_data = {}
        
        # Add frame metadata
        additional_data["frame_number"] = self.frame_number
        additional_data["timestamp"] = time.time()
        self.frame_number += 1
        
        results = []
        
        # Evaluate all gestures
        for gesture in self.gestures:
            try:
                # Check if trigger is active
                is_active = gesture.trigger.detect(landmarks, additional_data)
                trigger_value = gesture.trigger.get_value()
                
                # Update last triggered time if active
                if is_active:
                    gesture.last_triggered_time = time.time()
                
                # Add to results
                results.append((
                    gesture.name,
                    gesture.action,
                    is_active,
                    trigger_value
                ))
                
            except Exception as e:
                print(f"Warning: Error processing gesture '{gesture.name}': {e}")
        
        return results
    
    def reset_all(self):
        """Reset all gesture triggers"""
        for gesture in self.gestures:
            gesture.trigger.reset()
            gesture.last_triggered_time = None
        self.frame_number = 0
    
    def get_gesture_count(self) -> int:
        """Get number of loaded gestures"""
        return len(self.gestures)
    
    def get_gesture_names(self) -> List[str]:
        """Get list of all gesture names"""
        return [gesture.name for gesture in self.gestures]
    
    def get_active_gestures(self, landmarks: object) -> List[str]:
        """
        Get list of currently active gesture names.
        
        Args:
            landmarks: MediaPipe pose landmarks
            
        Returns:
            List of active gesture names
        """
        active = []
        for gesture in self.gestures:
            if gesture.trigger.detect(landmarks, {}):
                active.append(gesture.name)
        return active


