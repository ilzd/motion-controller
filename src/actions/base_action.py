"""Base class for all action types"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseAction(ABC):
    """Abstract base class for actions"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize action with configuration.
        
        Args:
            config: Dictionary containing action-specific parameters
        """
        self.config = config
        self.is_executing = False
        
    @abstractmethod
    def execute(self, trigger_value: float):
        """
        Execute the action.
        
        Args:
            trigger_value: Value from trigger (0.0-1.0) for analog actions
        """
        pass
    
    @abstractmethod
    def release(self):
        """Release/stop the action"""
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """
        Get the type name of this action.
        
        Returns:
            String identifier for this action type
        """
        pass
    
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


