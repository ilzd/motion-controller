"""Profile manager for loading, saving, and managing profiles"""

import os
import yaml
from typing import List, Optional
from pathlib import Path
from src.config.profile_schema import Profile, GestureConfig, TriggerConfig, ActionConfig


class ProfileManager:
    """Manages loading and saving of profiles"""
    
    def __init__(self, profiles_dir: str = "profiles"):
        """
        Initialize profile manager.
        
        Args:
            profiles_dir: Directory where profiles are stored
        """
        self.profiles_dir = Path(profiles_dir)
        self.profiles_dir.mkdir(exist_ok=True)
        
    def load_profile(self, filepath: str) -> Optional[Profile]:
        """
        Load a profile from a YAML file.
        
        Args:
            filepath: Path to the profile file
            
        Returns:
            Profile object, or None if loading failed
        """
        try:
            with open(filepath, 'r') as f:
                data = yaml.safe_load(f)
            
            # Validate and create profile
            profile = Profile.from_dict(data)
            return profile
            
        except Exception as e:
            print(f"Error loading profile from {filepath}: {e}")
            return None
    
    def save_profile(self, profile: Profile, filepath: str) -> bool:
        """
        Save a profile to a YAML file.
        
        Args:
            profile: Profile object to save
            filepath: Path where to save the profile
            
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            # Ensure directory exists
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            
            # Convert to dict and save
            data = profile.to_dict()
            with open(filepath, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            return True
            
        except Exception as e:
            print(f"Error saving profile to {filepath}: {e}")
            return False
    
    def list_available_profiles(self) -> List[str]:
        """
        List all available profile files in the profiles directory.
        
        Returns:
            List of profile filenames (without path)
        """
        try:
            profiles = []
            for file in self.profiles_dir.glob("*.yaml"):
                profiles.append(file.name)
            return sorted(profiles)
        except Exception as e:
            print(f"Error listing profiles: {e}")
            return []
    
    def get_profile_path(self, filename: str) -> str:
        """
        Get full path for a profile filename.
        
        Args:
            filename: Profile filename
            
        Returns:
            Full path to profile file
        """
        if not filename.endswith('.yaml'):
            filename += '.yaml'
        return str(self.profiles_dir / filename)
    
    def delete_profile(self, filepath: str) -> bool:
        """
        Delete a profile file.
        
        Args:
            filepath: Path to the profile file
            
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            Path(filepath).unlink()
            return True
        except Exception as e:
            print(f"Error deleting profile {filepath}: {e}")
            return False
    
    def validate_profile(self, profile: Profile) -> tuple[bool, Optional[str]]:
        """
        Validate a profile configuration.
        
        Args:
            profile: Profile to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Check basic fields
            if not profile.name:
                return False, "Profile name is required"
            
            if not profile.gestures:
                return False, "Profile must have at least one gesture"
            
            # Check each gesture
            for i, gesture in enumerate(profile.gestures):
                if not gesture.name:
                    return False, f"Gesture {i+1} is missing a name"
                
                if not gesture.trigger.type:
                    return False, f"Gesture '{gesture.name}' is missing trigger type"
                
                if not gesture.action.type:
                    return False, f"Gesture '{gesture.name}' is missing action type"
            
            return True, None
            
        except Exception as e:
            return False, str(e)
    
    def create_empty_profile(self, name: str) -> Profile:
        """
        Create a new empty profile.
        
        Args:
            name: Profile name
            
        Returns:
            New empty Profile object
        """
        return Profile(
            name=name,
            description="",
            game="",
            gestures=[]
        )


