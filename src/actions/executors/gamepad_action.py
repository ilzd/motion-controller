"""Gamepad action executor using vgamepad"""

from typing import Dict, Any
import vgamepad as vg
from src.actions.base_action import BaseAction
from src.actions.action_registry import ActionRegistry


@ActionRegistry.register("gamepad")
class GamepadAction(BaseAction):
    """Simulates Xbox 360 controller input"""
    
    # Shared gamepad instance (singleton pattern)
    _gamepad = None
    
    # Button mappings
    BUTTONS = {
        "a": vg.XUSB_BUTTON.XUSB_GAMEPAD_A,
        "button_a": vg.XUSB_BUTTON.XUSB_GAMEPAD_A,
        "b": vg.XUSB_BUTTON.XUSB_GAMEPAD_B,
        "button_b": vg.XUSB_BUTTON.XUSB_GAMEPAD_B,
        "x": vg.XUSB_BUTTON.XUSB_GAMEPAD_X,
        "button_x": vg.XUSB_BUTTON.XUSB_GAMEPAD_X,
        "y": vg.XUSB_BUTTON.XUSB_GAMEPAD_Y,
        "button_y": vg.XUSB_BUTTON.XUSB_GAMEPAD_Y,
        "lb": vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER,
        "left_bumper": vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER,
        "rb": vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER,
        "right_bumper": vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER,
        "back": vg.XUSB_BUTTON.XUSB_GAMEPAD_BACK,
        "start": vg.XUSB_BUTTON.XUSB_GAMEPAD_START,
        "left_thumb": vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_THUMB,
        "right_thumb": vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_THUMB,
        "dpad_up": vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP,
        "dpad_down": vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN,
        "dpad_left": vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT,
        "dpad_right": vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT,
    }
    
    @classmethod
    def get_gamepad(cls):
        """Get or create the shared gamepad instance"""
        if cls._gamepad is None:
            cls._gamepad = vg.VX360Gamepad()
        return cls._gamepad
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize gamepad action.
        
        Config parameters:
            control: Button name, "left_stick_x", "left_stick_y", 
                    "right_stick_x", "right_stick_y", "left_trigger", "right_trigger"
            value: Value for analog controls (-1.0 to 1.0 for sticks, 0.0-1.0 for triggers)
        """
        super().__init__(config)
        self.gamepad = self.get_gamepad()
        self.control = self.get_config_param("control", "button_a").lower()
        self.value = self.get_config_param("value", 1.0)
        
    def execute(self, trigger_value: float):
        """Execute gamepad action"""
        if not self.is_executing:
            if self.control in self.BUTTONS:
                # Button press
                self.gamepad.press_button(self.BUTTONS[self.control])
                self.gamepad.update()
                
            elif self.control == "left_stick_x":
                # Scale value (-1.0 to 1.0) to vgamepad range (-32768 to 32767)
                scaled_value = int(self.value * trigger_value * 32767)
                self.gamepad.left_joystick(x_value=scaled_value, y_value=0)
                self.gamepad.update()
                
            elif self.control == "left_stick_y":
                scaled_value = int(self.value * trigger_value * 32767)
                self.gamepad.left_joystick(x_value=0, y_value=scaled_value)
                self.gamepad.update()
                
            elif self.control == "right_stick_x":
                scaled_value = int(self.value * trigger_value * 32767)
                self.gamepad.right_joystick(x_value=scaled_value, y_value=0)
                self.gamepad.update()
                
            elif self.control == "right_stick_y":
                scaled_value = int(self.value * trigger_value * 32767)
                self.gamepad.right_joystick(x_value=0, y_value=scaled_value)
                self.gamepad.update()
                
            elif self.control == "left_trigger":
                # Scale 0.0-1.0 to 0-255
                scaled_value = int(self.value * trigger_value * 255)
                self.gamepad.left_trigger(scaled_value)
                self.gamepad.update()
                
            elif self.control == "right_trigger":
                scaled_value = int(self.value * trigger_value * 255)
                self.gamepad.right_trigger(scaled_value)
                self.gamepad.update()
            
            self.is_executing = True
    
    def release(self):
        """Release gamepad control"""
        if self.is_executing:
            if self.control in self.BUTTONS:
                # Release button
                self.gamepad.release_button(self.BUTTONS[self.control])
                self.gamepad.update()
                
            elif "stick" in self.control:
                # Reset stick to center
                if "left" in self.control:
                    self.gamepad.left_joystick(x_value=0, y_value=0)
                else:
                    self.gamepad.right_joystick(x_value=0, y_value=0)
                self.gamepad.update()
                
            elif "trigger" in self.control:
                # Reset trigger to 0
                if "left" in self.control:
                    self.gamepad.left_trigger(0)
                else:
                    self.gamepad.right_trigger(0)
                self.gamepad.update()
            
        self.is_executing = False
    
    def get_name(self) -> str:
        """Get action type name"""
        return "gamepad"


