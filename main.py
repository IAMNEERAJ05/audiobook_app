# main.py
import sys
import os
from PyQt5.QtWidgets import QApplication, QMessageBox, QDialog
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
        # Show API key setup dialog with proper parent
        api_dialog = APIKeyDialog(parent=None, is_first_run=True)
        
        # Use a flag to track if setup was completed
        setup_completed = False
        
        def on_api_key_saved(api_key):
            nonlocal setup_completed
            try:
                if api_key:
                    config_manager.set_api_key(api_key)
                    # Set environment variable for immediate use
                    os.environ['GOOGLE_API_KEY'] = api_key
                    print("✅ API key saved successfully")
                else:
                    config_manager.mark_setup_completed()
                    print("✅ Setup completed without API key")
                setup_completed = True
            except Exception as e:
                print(f"❌ Error saving API key: {e}")
                setup_completed = True  # Continue anyway
                
        api_dialog.api_key_saved.connect(on_api_key_saved)
        
        # Show dialog and wait for completion
        print("🔑 Showing API key setup dialog...")
        result = api_dialog.exec_()
        
        # Ensure dialog is properly closed
        api_dialog.close()
        api_dialog.deleteLater()
        
        # Check if setup was completed
        if not setup_completed:
            print("❌ Setup was not completed, exiting...")
            sys.exit(0)
        else:
            print("✅ Setup completed successfully")
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

