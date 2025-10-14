"""
config_manager.py
Manages application configuration and API key storage.
"""
import os
import json
import base64
from pathlib import Path
from typing import Optional, Dict, Any

class ConfigManager:
    """Manages application configuration and secure API key storage."""
    
    def __init__(self):
        self.config_dir = Path.home() / ".audiobook_generator"
        self.config_file = self.config_dir / "config.json"
        self._config_cache = None
        
    def ensure_config_dir(self):
        """Ensure the config directory exists."""
        self.config_dir.mkdir(exist_ok=True)
        
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        if self._config_cache is not None:
            return self._config_cache
            
        self.ensure_config_dir()
        
        if not self.config_file.exists():
            return {
                'setup_completed': False,
                'version': '1.0.0',
                'api_key': None
            }
            
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            self._config_cache = config
            return config
        except Exception:
            return {
                'setup_completed': False,
                'version': '1.0.0',
                'api_key': None
            }
            
    def save_config(self, config: Dict[str, Any]):
        """Save configuration to file."""
        self.ensure_config_dir()
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            # Set secure permissions
            try:
                os.chmod(self.config_file, 0o600)
            except:
                pass
                
            self._config_cache = config
        except Exception as e:
            raise Exception(f"Failed to save configuration: {str(e)}")
            
    def get_api_key(self) -> Optional[str]:
        """Get the stored API key."""
        config = self.load_config()
        
        if not config.get('api_key'):
            return None
            
        try:
            # Decode the stored key
            encoded_key = config['api_key']
            return base64.b64decode(encoded_key).decode('utf-8')
        except Exception:
            return None
            
    def set_api_key(self, api_key: str):
        """Set and save the API key."""
        config = self.load_config()
        
        if api_key:
            # Encode the key for basic obfuscation
            encoded_key = base64.b64encode(api_key.encode('utf-8')).decode('utf-8')
            config['api_key'] = encoded_key
        else:
            config['api_key'] = None
            
        config['setup_completed'] = True
        self.save_config(config)
        
    def is_setup_completed(self) -> bool:
        """Check if initial setup is completed."""
        config = self.load_config()
        return config.get('setup_completed', False)
        
    def mark_setup_completed(self):
        """Mark initial setup as completed."""
        config = self.load_config()
        config['setup_completed'] = True
        self.save_config(config)
        
    def get_version(self) -> str:
        """Get the application version."""
        config = self.load_config()
        return config.get('version', '1.0.0')
        
    def has_api_key(self) -> bool:
        """Check if API key is available."""
        return self.get_api_key() is not None
        
    def clear_config(self):
        """Clear all configuration (for testing/reset)."""
        try:
            if self.config_file.exists():
                self.config_file.unlink()
            self._config_cache = None
        except Exception:
            pass
