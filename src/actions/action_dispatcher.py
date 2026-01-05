"""Action dispatcher to manage and route actions"""

from typing import Dict, List, Tuple
from src.actions.base_action import BaseAction


class ActionDispatcher:
    """Manages execution and lifecycle of actions"""
    
    def __init__(self):
        """Initialize action dispatcher"""
        self.active_actions: Dict[str, Tuple[BaseAction, float]] = {}
        
    def dispatch(self, gesture_activations: List[Tuple[str, BaseAction, bool, float]]):
        """
        Dispatch actions based on gesture activations.
        
        Args:
            gesture_activations: List of (gesture_name, action, is_active, trigger_value) tuples
        """
        # Track which gestures are currently active
        current_active = set()
        
        for gesture_name, action, is_active, trigger_value in gesture_activations:
            if is_active:
                current_active.add(gesture_name)
                
                if gesture_name not in self.active_actions:
                    # New activation - execute action
                    try:
                        action.execute(trigger_value)
                        self.active_actions[gesture_name] = (action, trigger_value)
                    except Exception as e:
                        print(f"Warning: Failed to execute action for gesture '{gesture_name}': {e}")
                else:
                    # Already active - update if it's a continuous action
                    existing_action, existing_value = self.active_actions[gesture_name]
                    # For continuous actions (analog sticks/triggers), re-execute with new value
                    action_name = action.get_name()
                    
                    # Check if this is a continuous action that needs updates
                    is_continuous = False
                    if action_name == "gamepad":
                        # Gamepad analog controls need continuous updates
                        is_continuous = ("stick" in action.control or "trigger" in action.control)
                    elif action_name == "mouse":
                        # Mouse move needs continuous updates
                        is_continuous = (hasattr(action, 'action_type') and action.action_type == "move")
                    
                    if is_continuous:
                        # Only update if value changed significantly (avoid unnecessary updates)
                        if abs(existing_value - trigger_value) > 0.01:
                            try:
                                action.execute(trigger_value)
                            except Exception as e:
                                print(f"Warning: Failed to update action for gesture '{gesture_name}': {e}")
                    
                    self.active_actions[gesture_name] = (action, trigger_value)
        
        # Release actions that are no longer active
        gestures_to_release = []
        for gesture_name in self.active_actions.keys():
            if gesture_name not in current_active:
                gestures_to_release.append(gesture_name)
        
        for gesture_name in gestures_to_release:
            action, _ = self.active_actions[gesture_name]
            try:
                action.release()
                # Reset state for press-mode actions to allow re-triggering
                # Only reset if method exists (optional method)
                if hasattr(action, 'reset_state'):
                    try:
                        action.reset_state()
                    except Exception as e:
                        print(f"Warning: reset_state failed for '{gesture_name}': {e}")
            except Exception as e:
                print(f"Warning: Failed to release action for gesture '{gesture_name}': {e}")
            del self.active_actions[gesture_name]
    
    def release_all(self):
        """Release all active actions"""
        for gesture_name, (action, _) in list(self.active_actions.items()):
            try:
                action.release()
                # Reset state if method exists
                if hasattr(action, 'reset_state'):
                    try:
                        action.reset_state()
                    except Exception:
                        pass  # Ignore reset errors during cleanup
            except Exception as e:
                print(f"Warning: Failed to release action '{gesture_name}': {e}")
        self.active_actions.clear()
    
    def get_active_count(self) -> int:
        """Get number of currently active actions"""
        return len(self.active_actions)


