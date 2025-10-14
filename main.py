import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QSettings
from main_window import MainWindow

def main():
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("Search Analytics Pro")
    app.setOrganizationName("AnalyticsCorp")
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Run application
    sys.exit(app.exec())

if __name__ == '__main__':
    main()