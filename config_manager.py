import os
import json
from PyQt5.QtCore import QObject, pyqtSignal, QSettings
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QTextEdit
import google.generativeai as genai

class ApiKeyDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gemini API Key Setup")
        self.setModal(True)
        self.setFixedSize(500, 400)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Instructions
        instructions = QLabel(
            "To use AI analysis features, you need a Google Gemini API key.\n\n"
            "How to get your API key:\n"
            "1. Go to https://aistudio.google.com/app/apikey\n"
            "2. Sign in with your Google account\n"
            "3. Click 'Create API Key'\n"
            "4. Copy the key and paste it below"
        )
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        # API Key input
        layout.addWidget(QLabel("API Key:"))
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("Paste your Gemini API key here...")
        layout.addWidget(self.api_key_input)
        
        # Test button
        self.test_btn = QPushButton("Test API Key")
        self.test_btn.clicked.connect(self.test_api_key)
        layout.addWidget(self.test_btn)
        
        # Test result
        self.test_result = QTextEdit()
        self.test_result.setMaximumHeight(100)
        self.test_result.setReadOnly(True)
        layout.addWidget(self.test_result)
        
        # Buttons
        button_layout = QVBoxLayout()
        self.save_btn = QPushButton("Save API Key")
        self.save_btn.clicked.connect(self.accept)
        self.save_btn.setEnabled(False)
        button_layout.addWidget(self.save_btn)
        
        self.cancel_btn = QPushButton("Skip for Now")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def test_api_key(self):
        api_key = self.api_key_input.text().strip()
        if not api_key:
            self.test_result.setPlainText("Please enter an API key first.")
            return
        
        try:
            # Test the API key
            genai.configure(api_key=api_key)
            
            # Try to use a model directly instead of listing all models
            model_names = [
                'gemini-1.5-pro-latest',
                'models/gemini-1.5-pro-latest',
                'gemini-1.0-pro-latest', 
                'models/gemini-1.0-pro-latest'
            ]
            
            successful_model = None
            for model_name in model_names:
                try:
                    model = genai.GenerativeModel(model_name)
                    response = model.generate_content("Test")
                    if response.text:
                        successful_model = model_name
                        break
                except:
                    continue
            
            if successful_model:
                self.test_result.setPlainText(
                    f"✅ API Key is valid!\n"
                    f"Connected to: {successful_model}"
                )
                self.save_btn.setEnabled(True)
            else:
                self.test_result.setPlainText("❌ API Key is valid but no working Gemini models found.")
                self.save_btn.setEnabled(False)
                
        except Exception as e:
            self.test_result.setPlainText(f"❌ API Key test failed:\n{str(e)}")
            self.save_btn.setEnabled(False)
    
    def get_api_key(self):
        return self.api_key_input.text().strip()

class ConfigManager(QObject):
    api_key_verified = pyqtSignal(bool)
    
    def __init__(self):
        super().__init__()
        self.settings = QSettings()
    
    def get_gemini_api_key(self):
        return self.settings.value('gemini_api_key', '')
    
    def set_gemini_api_key(self, api_key):
        self.settings.setValue('gemini_api_key', api_key)
    
    def verify_api_key(self, api_key=None):
        """Verify if the API key works"""
        if not api_key:
            api_key = self.get_gemini_api_key()
        
        if not api_key:
            return False, "No API key provided"
        
        try:
            genai.configure(api_key=api_key)
            
            # Test with a direct model approach
            model = genai.GenerativeModel('gemini-1.5-pro-latest')
            response = model.generate_content("Hello")
            
            if response.text:
                return True, "API key is valid and working"
            else:
                return False, "No response from Gemini API"
                
        except Exception as e:
            return False, f"API verification failed: {str(e)}"
    
    def prompt_for_api_key(self, parent=None):
        """Show dialog to get API key from user"""
        dialog = ApiKeyDialog(parent)
        result = dialog.exec()
        
        if result == QDialog.DialogCode.Accepted:
            api_key = dialog.get_api_key()
            if api_key:
                self.set_gemini_api_key(api_key)
                return True, api_key
        
        return False, None