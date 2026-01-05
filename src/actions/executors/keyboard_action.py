"""Keyboard action executor using pynput"""

from typing import Dict, Any
from pynput.keyboard import Controller, Key
from src.actions.base_action import BaseAction
from src.actions.action_registry import ActionRegistry


@ActionRegistry.register("keyboard")
class KeyboardAction(BaseAction):
    """Simulates keyboard input"""
    
    # Map string keys to pynput Key enum
    SPECIAL_KEYS = {
        "space": Key.space,
        "enter": Key.enter,
        "tab": Key.tab,
        "backspace": Key.backspace,
        "delete": Key.delete,
        "esc": Key.esc,
        "escape": Key.esc,
        "up": Key.up,
        "down": Key.down,
        "left": Key.left,
        "right": Key.right,
        "shift": Key.shift,
        "ctrl": Key.ctrl,
        "control": Key.ctrl,
        "alt": Key.alt,
        "cmd": Key.cmd,
        "win": Key.cmd,
        "f1": Key.f1, "f2": Key.f2, "f3": Key.f3, "f4": Key.f4,
        "f5": Key.f5, "f6": Key.f6, "f7": Key.f7, "f8": Key.f8,
        "f9": Key.f9, "f10": Key.f10, "f11": Key.f11, "f12": Key.f12,
    }
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize keyboard action.
        
        Config parameters:
            key: Key to press (string)
            mode: "press" (tap) or "hold" (continuous)
        """
        super().__init__(config)
        self.keyboard = Controller()
        self.key_str = self.get_config_param("key", "space").lower()
        self.mode = self.get_config_param("mode", "press").lower()
        
        # Convert string to key
        if self.key_str in self.SPECIAL_KEYS:
            self.key = self.SPECIAL_KEYS[self.key_str]
        else:
            # Regular character key
            self.key = self.key_str
        
    def execute(self, trigger_value: float):
        """Execute keyboard action"""
        try:
            if self.mode == "press":
                # One-shot press (tap) - execute on edge (transition from inactive to active)
                # Track previous state to detect edge
                if not hasattr(self, '_was_active'):
                    self._was_active = False
                
                # Only execute if transitioning from inactive to active (edge detection)
                if not self._was_active:
                    self.keyboard.press(self.key)
                    self.keyboard.release(self.key)
                    self._was_active = True
                    self.is_executing = True
            elif self.mode == "hold":
                # Continuous hold - only press once, release when gesture ends
                if not self.is_executing:
                    self.keyboard.press(self.key)
                    self.is_executing = True
                    if not hasattr(self, '_was_active'):
                        self._was_active = True
        except Exception as e:
            print(f"Warning: Keyboard action failed for key '{self.key_str}': {e}")
            import traceback
            traceback.print_exc()
            # Don't set is_executing if it failed
    
    def reset_state(self):
        """Reset internal state (called when gesture becomes inactive)"""
        self._was_active = False
        self.is_executing = False
    
    def release(self):
        """Release key if held"""
        try:
            if self.is_executing and self.mode == "hold":
                self.keyboard.release(self.key)
        except Exception as e:
            print(f"Warning: Keyboard release failed: {e}")
        finally:
            self.is_executing = False
            # Reset state for next activation
            if hasattr(self, '_was_active'):
                self._was_active = False
    
    def get_name(self) -> str:
        """Get action type name"""
        return "keyboard"


