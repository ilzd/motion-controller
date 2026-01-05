"""Base class for all trigger types"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseTrigger(ABC):
    """Abstract base class for gesture triggers"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize trigger with configuration.
        
        Args:
            config: Dictionary containing trigger-specific parameters
        """
        self.config = config
        self.is_active = False
        self.previous_state: Dict[str, Any] = {}
        self.current_value = 0.0
        
        # Debouncing: track consecutive active/inactive frames
        self._consecutive_active_frames = 0
        self._consecutive_inactive_frames = 0
        self._debounce_frames = self.get_config_param("debounce_frames", 2)  # Require 2 frames for state change
        self._debounced_active = False
        
    @abstractmethod
    def detect(self, landmarks: object, frame_data: Dict[str, Any]) -> bool:
        """
        Detect if trigger condition is met.
        
        Args:
            landmarks: MediaPipe pose landmarks
            frame_data: Additional frame information (timestamp, frame_number, etc)
            
        Returns:
            True if trigger is active, False otherwise
        """
        pass
    
    @abstractmethod
    def get_value(self) -> float:
        """
        Get the current value of the trigger.
        
        Returns:
            Value between 0.0 and 1.0 for analog triggers, 1.0 for digital triggers
        """
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """
        Get the type name of this trigger.
        
        Returns:
            String identifier for this trigger type
        """
        pass
    
    def reset(self):
        """Reset trigger state"""
        self.is_active = False
        self.previous_state.clear()
        self.current_value = 0.0
        self._consecutive_active_frames = 0
        self._consecutive_inactive_frames = 0
        self._debounced_active = False
    
    def _apply_debouncing(self, raw_active: bool) -> bool:
        """
        Apply debouncing to prevent rapid state changes.
        
        Args:
            raw_active: Raw detection result
            
        Returns:
            Debounced active state
        """
        if raw_active:
            self._consecutive_active_frames += 1
            self._consecutive_inactive_frames = 0
        else:
            self._consecutive_inactive_frames += 1
            self._consecutive_active_frames = 0
        
        # Only change state after debounce_frames consecutive frames
        if self._consecutive_active_frames >= self._debounce_frames:
            self._debounced_active = True
        elif self._consecutive_inactive_frames >= self._debounce_frames:
            self._debounced_active = False
        
        return self._debounced_active
    
    def get_config_param(self, key: str, default: Any = None) -> Any:
        """
        Safely get a configuration parameter.
        
        Args:
            key: Parameter key
            default: Default value if key not found
            
        Returns:
            Parameter value or default
        """
        return self.config.get(key, default)


