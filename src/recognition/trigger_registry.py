"""Registry for trigger types using plugin pattern"""

from typing import Dict, Type, Any
from src.recognition.base_trigger import BaseTrigger


class TriggerRegistry:
    """Registry for managing trigger types"""
    
    _triggers: Dict[str, Type[BaseTrigger]] = {}
    
    @classmethod
    def register(cls, name: str):
        """
        Decorator to register a trigger type.
        
        Args:
            name: Unique identifier for this trigger type
            
        Returns:
            Decorator function
            
        Example:
            @TriggerRegistry.register("hand_raise")
            class HandRaiseTrigger(BaseTrigger):
                ...
        """
        def decorator(trigger_class: Type[BaseTrigger]):
            cls._triggers[name] = trigger_class
            return trigger_class
        return decorator
    
    @classmethod
    def create(cls, name: str, config: Dict[str, Any]) -> BaseTrigger:
        """
        Create a trigger instance by name.
        
        Args:
            name: Trigger type name
            config: Configuration dictionary
            
        Returns:
            Trigger instance
            
        Raises:
            KeyError: If trigger type not registered
        """
        if name not in cls._triggers:
            raise KeyError(f"Trigger type '{name}' not registered. Available: {list(cls._triggers.keys())}")
        
        trigger_class = cls._triggers[name]
        return trigger_class(config)
    
    @classmethod
    def get_available_triggers(cls) -> list:
        """
        Get list of all registered trigger types.
        
        Returns:
            List of trigger type names
        """
        return list(cls._triggers.keys())
    
    @classmethod
    def is_registered(cls, name: str) -> bool:
        """
        Check if a trigger type is registered.
        
        Args:
            name: Trigger type name
            
        Returns:
            True if registered, False otherwise
        """
        return name in cls._triggers


