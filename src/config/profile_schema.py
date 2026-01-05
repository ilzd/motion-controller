"""Pydantic models for profile configuration and validation"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


class TriggerConfig(BaseModel):
    """Configuration for a trigger"""
    type: str = Field(..., description="Type of trigger (e.g., 'hand_raise', 'body_lean')")
    params: Dict[str, Any] = Field(default_factory=dict, description="Trigger-specific parameters")
    
    class Config:
        extra = "allow"


class ActionConfig(BaseModel):
    """Configuration for an action"""
    type: str = Field(..., description="Type of action (e.g., 'keyboard', 'mouse', 'gamepad')")
    params: Dict[str, Any] = Field(default_factory=dict, description="Action-specific parameters")
    
    class Config:
        extra = "allow"


class GestureConfig(BaseModel):
    """Configuration for a gesture (trigger + action pair)"""
    name: str = Field(..., description="Human-readable name for the gesture")
    trigger: TriggerConfig = Field(..., description="Trigger configuration")
    action: ActionConfig = Field(..., description="Action configuration")
    enabled: bool = Field(default=True, description="Whether this gesture is enabled")
    
    class Config:
        extra = "allow"


class Profile(BaseModel):
    """Complete profile configuration"""
    name: str = Field(..., description="Profile name")
    description: str = Field(default="", description="Profile description")
    game: str = Field(default="", description="Target game or application")
    gestures: List[GestureConfig] = Field(default_factory=list, description="List of gestures")
    
    class Config:
        extra = "allow"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert profile to dictionary"""
        return self.model_dump()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Profile":
        """Create profile from dictionary"""
        return cls(**data)


