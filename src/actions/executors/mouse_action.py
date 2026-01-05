"""Mouse action executor using pynput"""

from typing import Dict, Any
from pynput.mouse import Controller, Button
from src.actions.base_action import BaseAction
from src.actions.action_registry import ActionRegistry


@ActionRegistry.register("mouse")
class MouseAction(BaseAction):
    """Simulates mouse input"""
    
    BUTTONS = {
        "left": Button.left,
        "right": Button.right,
        "middle": Button.middle,
    }
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize mouse action.
        
        Config parameters:
            action: "move", "click", or "hold"
            button: "left", "right", or "middle" (for click/hold)
            x: X position (0.0-1.0, for move)
            y: Y position (0.0-1.0, for move)
            relative: Boolean, if True uses relative movement (for move)
        """
        super().__init__(config)
        self.mouse = Controller()
        self.action_type = self.get_config_param("action", "click").lower()
        self.button_str = self.get_config_param("button", "left").lower()
        self.button = self.BUTTONS.get(self.button_str, Button.left)
        self.x = self.get_config_param("x", 0.5)
        self.y = self.get_config_param("y", 0.5)
        self.relative = self.get_config_param("relative", False)
        
    def execute(self, trigger_value: float):
        """Execute mouse action"""
        if self.action_type == "click":
            # One-shot click
            if not self.is_executing:
                self.mouse.click(self.button, 1)
                self.is_executing = True
                
        elif self.action_type == "hold":
            # Hold button down
            if not self.is_executing:
                self.mouse.press(self.button)
                self.is_executing = True
                
        elif self.action_type == "move":
            # Move mouse (can use trigger_value for analog control)
            if self.relative:
                # Relative movement
                dx = int((self.x - 0.5) * 20 * trigger_value)
                dy = int((self.y - 0.5) * 20 * trigger_value)
                self.mouse.move(dx, dy)
            else:
                # Absolute position (requires screen size)
                # For now, just do relative movement
                # TODO: Implement absolute positioning with screen dimensions
                pass
            self.is_executing = True
    
    def release(self):
        """Release mouse button if held"""
        if self.is_executing and self.action_type == "hold":
            try:
                self.mouse.release(self.button)
            except:
                pass  # Ignore errors on release
        self.is_executing = False
    
    def get_name(self) -> str:
        """Get action type name"""
        return "mouse"


