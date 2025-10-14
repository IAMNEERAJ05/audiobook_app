# main.py
import sys
import os
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt
from gui.home_window import HomeWindow
from gui.api_key_dialog import APIKeyDialog
from backend.config_manager import ConfigManager

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Audiobook Generator")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("IAMNEERAJ05")
    
    # Set application style
    app.setStyle('Fusion')
    
    # Check if this is the first run
    config_manager = ConfigManager()
    
    if not config_manager.is_setup_completed():
        # Show API key setup dialog
        api_dialog = APIKeyDialog()
        
        def on_api_key_saved(api_key):
            if api_key:
                config_manager.set_api_key(api_key)
                # Set environment variable for immediate use
                os.environ['GOOGLE_API_KEY'] = api_key
            else:
                config_manager.mark_setup_completed()
                
        api_dialog.api_key_saved.connect(on_api_key_saved)
        
        if api_dialog.exec_() != APIKeyDialog.Accepted:
            # User cancelled, exit application
            sys.exit(0)
    else:
        # Load existing API key
        existing_key = config_manager.get_api_key()
        if existing_key:
            os.environ['GOOGLE_API_KEY'] = existing_key
    
    # Create and show main window
    home = HomeWindow()
    home.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

