"""
test_api_key_management.py
Simple test script to verify API key management functionality.
"""
import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from backend.config_manager import ConfigManager

def test_config_manager():
    """Test the configuration manager functionality."""
    print("🧪 Testing Configuration Manager...")
    
    # Create config manager
    config_manager = ConfigManager()
    
    # Test initial state
    print(f"Initial setup completed: {config_manager.is_setup_completed()}")
    print(f"Has API key: {config_manager.has_api_key()}")
    
    # Test setting API key
    test_key = "test_api_key_12345"
    config_manager.set_api_key(test_key)
    
    print(f"After setting key - Has API key: {config_manager.has_api_key()}")
    print(f"Retrieved key matches: {config_manager.get_api_key() == test_key}")
    
    # Test clearing key
    config_manager.set_api_key("")
    print(f"After clearing key - Has API key: {config_manager.has_api_key()}")
    
    # Test marking setup as completed
    config_manager.mark_setup_completed()
    print(f"Setup completed: {config_manager.is_setup_completed()}")
    
    # Clean up test config
    config_manager.clear_config()
    print("✅ Configuration Manager tests completed!")

if __name__ == "__main__":
    test_config_manager()
