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
        self.api_key_input.textChanged.connect(self.on_api_key_changed)
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
    
    def on_api_key_changed(self):
        """Reset test results when API key changes"""
        self.test_result.setPlainText("")
        self.save_btn.setEnabled(False)
    
    def test_api_key(self):
        api_key = self.api_key_input.text().strip()
        if not api_key:
            self.test_result.setPlainText("❌ Please enter an API key first.")
            return
        
        self.test_btn.setEnabled(False)
        self.test_btn.setText("Testing...")
        self.test_result.setPlainText("🔧 Testing API key...")
        
        try:
            # Test the API key with better error handling
            genai.configure(api_key=api_key)
            
            # First, try to list available models to verify API access
            try:
                models = list(genai.list_models())
                gemini_models = [
                    model.name for model in models 
                    if 'gemini' in model.name.lower() 
                    and 'generateContent' in getattr(model, 'supported_generation_methods', [])
                ]
                
                if not gemini_models:
                    self.test_result.setPlainText(
                        "❌ API Key is valid but no Gemini models with generateContent support found.\n"
                        "This might be a temporary API issue. Try again later."
                    )
                    self.save_btn.setEnabled(False)
                    return
                
                # Try the most common Gemini models
                test_models = [
                    'models/gemini-1.5-pro-latest',
                    'models/gemini-1.5-pro',
                    'models/gemini-1.0-pro-latest',
                    'models/gemini-1.0-pro',
                    'models/gemini-pro'
                ]
                
                # Filter to only available models
                available_test_models = [model for model in test_models if any(gemini_model.endswith(model.split('/')[-1]) for gemini_model in gemini_models)]
                
                if not available_test_models:
                    available_test_models = gemini_models[:2]  # Use first available Gemini models
                
            except Exception as e:
                self.test_result.setPlainText(
                    f"⚠️ Could not fetch model list: {str(e)}\n"
                    "Trying direct model access..."
                )
                available_test_models = [
                    'models/gemini-1.5-pro-latest',
                    'models/gemini-1.0-pro-latest'
                ]
            
            # Test with available models
            successful_model = None
            last_error = None
            
            for model_name in available_test_models:
                try:
                    self.test_result.setPlainText(f"🔧 Testing model: {model_name}...")
                    
                    model = genai.GenerativeModel(model_name)
                    response = model.generate_content("Please respond with 'OK' if you can read this.")
                    
                    if response and response.text:
                        successful_model = model_name
                        break
                        
                except Exception as e:
                    last_error = str(e)
                    continue
            
            if successful_model:
                self.test_result.setPlainText(
                    f"✅ API Key is valid and working!\n"
                    f"✅ Connected to: {successful_model}\n"
                    f"✅ Response: '{response.text.strip()}'"
                )
                self.save_btn.setEnabled(True)
            else:
                error_msg = f"❌ Could not connect to any Gemini model.\n"
                if last_error:
                    error_msg += f"Last error: {last_error}\n"
                error_msg += "Please check:\n- Your API key permissions\n- Your internet connection\n- Try again later"
                self.test_result.setPlainText(error_msg)
                self.save_btn.setEnabled(False)
                
        except Exception as e:
            error_msg = str(e)
            if "API_KEY_INVALID" in error_msg:
                self.test_result.setPlainText("❌ Invalid API key. Please check and try again.")
            elif "PERMISSION_DENIED" in error_msg:
                self.test_result.setPlainText("❌ API key permission denied. Please check if the API is enabled.")
            elif "quota" in error_msg.lower():
                self.test_result.setPlainText("❌ API quota exceeded. Please check your Google AI Studio quota.")
            else:
                self.test_result.setPlainText(f"❌ API Key test failed:\n{error_msg}")
            self.save_btn.setEnabled(False)
        
        finally:
            self.test_btn.setEnabled(True)
            self.test_btn.setText("Test API Key")
    
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
            
            # Use a more robust verification approach
            try:
                # First try to list models
                models = list(genai.list_models())
                gemini_models = [
                    model.name for model in models 
                    if 'gemini' in model.name.lower() 
                    and 'generateContent' in getattr(model, 'supported_generation_methods', [])
                ]
                
                if not gemini_models:
                    return False, "No Gemini models available with generateContent support"
                
                # Try a simple test with the first available Gemini model
                test_model = gemini_models[0]
                model = genai.GenerativeModel(test_model)
                response = model.generate_content("Test connection")
                
                if response.text:
                    return True, f"API key valid. Connected to {test_model}"
                else:
                    return False, "No response from Gemini API"
                    
            except Exception as e:
                # Fallback: try direct model access
                try:
                    model = genai.GenerativeModel('models/gemini-1.5-pro-latest')
                    response = model.generate_content("Test")
                    if response.text:
                        return True, "API key valid. Connected to gemini-1.5-pro-latest"
                    else:
                        return False, "No response from Gemini API"
                except Exception as fallback_error:
                    return False, f"API verification failed: {str(fallback_error)}"
                
        except Exception as e:
            error_msg = str(e)
            if "API_KEY_INVALID" in error_msg:
                return False, "Invalid API key"
            elif "PERMISSION_DENIED" in error_msg:
                return False, "API permission denied. Please enable Gemini API in Google Cloud Console"
            elif "quota" in error_msg.lower():
                return False, "API quota exceeded. Please check your Google AI Studio quota."
            else:
                return False, f"API verification failed: {error_msg}"
    
    def prompt_for_api_key(self, parent=None):
        """Show dialog to get API key from user"""
        dialog = ApiKeyDialog(parent)
        result = dialog.exec()
        
        if result == QDialog.DialogCode.Accepted:
            api_key = dialog.get_api_key()
            if api_key:
                self.set_gemini_api_key(api_key)
                # Verify the saved key
                is_valid, message = self.verify_api_key(api_key)
                if is_valid:
                    QMessageBox.information(parent, "Success", f"API key saved and verified!\n{message}")
                else:
                    QMessageBox.warning(parent, "Verification Failed", 
                                      f"API key saved but verification failed:\n{message}\n\n"
                                      "You can still try to use the application.")
                return True, api_key
        
        return False, None
    
    def clear_api_key(self):
        """Clear the stored API key"""
        self.settings.remove('gemini_api_key')
    
    def has_api_key(self):
        """Check if an API key is stored"""
        return bool(self.get_gemini_api_key())