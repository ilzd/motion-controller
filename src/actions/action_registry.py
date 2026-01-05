"""Registry for action types using plugin pattern"""

from typing import Dict, Type, Any
from src.actions.base_action import BaseAction


class ActionRegistry:
    """Registry for managing action types"""
    
    _actions: Dict[str, Type[BaseAction]] = {}
    
    @classmethod
    def register(cls, name: str):
        """
        Decorator to register an action type.
        
        Args:
            name: Unique identifier for this action type
            
        Returns:
            Decorator function
            
        Example:
            @ActionRegistry.register("keyboard")
            class KeyboardAction(BaseAction):
                ...
        """
        def decorator(action_class: Type[BaseAction]):
            cls._actions[name] = action_class
            return action_class
        return decorator
    
    @classmethod
    def create(cls, name: str, config: Dict[str, Any]) -> BaseAction:
        """
        Create an action instance by name.
        
        Args:
            name: Action type name
            config: Configuration dictionary
            
        Returns:
            Action instance
            
        Raises:
            KeyError: If action type not registered
        """
        if name not in cls._actions:
            raise KeyError(f"Action type '{name}' not registered. Available: {list(cls._actions.keys())}")
        
        action_class = cls._actions[name]
        return action_class(config)
    
    @classmethod
    def get_available_actions(cls) -> list:
        """
        Get list of all registered action types.
        
        Returns:
            List of action type names
        """
        return list(cls._actions.keys())
    
    @classmethod
    def is_registered(cls, name: str) -> bool:
        """
        Check if an action type is registered.
        
        Args:
            name: Action type name
            
        Returns:
            True if registered, False otherwise
        """
        return name in cls._actions


