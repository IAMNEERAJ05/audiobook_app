# main.py
import sys
from PyQt5.QtWidgets import QApplication
from gui.home_window import HomeWindow

def main():
    app = QApplication(sys.argv)
    home = HomeWindow()
    home.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

