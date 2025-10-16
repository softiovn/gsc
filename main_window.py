import os
from PySide6.QtWidgets import (QMainWindow, QVBoxLayout, QWidget, QTabWidget, 
                            QMessageBox, QInputDialog, QStatusBar, QAction, QMenu)
from PySide6.QtCore import QSettings
from auth_manager import AuthManager
from gsc_client import GSCClient
from gemini_analyzer import GeminiAnalyzer
from config_manager import ConfigManager
from widgets.dashboard_widget import DashboardWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = QSettings()
        self.config_manager = ConfigManager()
        self.init_ui()
        self.init_services()
        
    def init_ui(self):
        self.setWindowTitle("Search Analytics Pro")
        self.setGeometry(100, 100, 1400, 900)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create tab widget
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # Set status bar
        self.setStatusBar(QStatusBar())
        
    def create_menu_bar(self):
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        settings_action = QAction('Settings', self)
        settings_action.triggered.connect(self.show_settings)
        file_menu.addAction(settings_action)
        
        # Help menu
        help_menu = menubar.addMenu('Help')
        
        api_key_action = QAction('Setup Gemini API Key', self)
        api_key_action.triggered.connect(self.setup_api_key)
        help_menu.addAction(api_key_action)
        
    def init_services(self):
        # Initialize Gemini first
        api_key = self.config_manager.get_gemini_api_key()
        self.gemini_analyzer = GeminiAnalyzer(api_key)
        
        # Connect Gemini status updates
        self.gemini_analyzer.status_update.connect(self.on_gemini_status_update)
        
        # Initialize authentication manager
        self.auth_manager = AuthManager()
        self.auth_manager.authenticated.connect(self.on_authenticated)
        self.auth_manager.error_occurred.connect(self.on_auth_error)
        
        # Start authentication
        self.statusBar().showMessage("Authenticating with Google...")
        self.auth_manager.authenticate()
    
    def on_gemini_status_update(self, message):
        """Update status bar with Gemini status"""
        self.statusBar().showMessage(message)
    
    def setup_api_key(self):
        """Setup Gemini API key"""
        success, api_key = self.config_manager.prompt_for_api_key(self)
        if success:
            self.gemini_analyzer.set_api_key(api_key)
            if self.gemini_analyzer.is_available():
                QMessageBox.information(self, "Success", "Gemini API key configured successfully!")
            else:
                QMessageBox.warning(self, "Warning", "API key saved but Gemini is not available.")
    
    def show_settings(self):
        """Show settings dialog"""
        self.setup_api_key()
    
    def on_authenticated(self, success):
        if success:
            self.statusBar().showMessage("Successfully authenticated with Google!")
            self.setup_application()
        else:
            self.statusBar().showMessage("Google authentication failed")
    
    def on_auth_error(self, error_message):
        QMessageBox.critical(self, "Authentication Error", error_message)
    
    def setup_application(self):
        """Setup application after successful authentication"""
        # Initialize GSC client
        credentials = self.auth_manager.get_credentials()
        self.gsc_client = GSCClient(credentials)
        
        # Create dashboard widget
        self.dashboard = DashboardWidget(self.gsc_client, self.gemini_analyzer)
        self.tabs.addTab(self.dashboard, "Dashboard")
        
        # Load sites
        self.dashboard.load_sites()
        
        # Check Gemini status
        if not self.gemini_analyzer.is_available():
            self.statusBar().showMessage("Ready - Gemini AI not available. Go to Settings to configure.")
        else:
            self.statusBar().showMessage("Ready - Gemini AI available!")