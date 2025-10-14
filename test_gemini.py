import google.generativeai as genai

def test_gemini_api(api_key):
    try:
        genai.configure(api_key=api_key)
        print("✅ API key configured successfully")
        
        # Try different model names
        model_names = [
            'gemini-1.5-pro-latest',
            'models/gemini-1.5-pro-latest',
            'gemini-1.0-pro-latest',
            'models/gemini-1.0-pro-latest',
            'gemini-pro',
            'models/gemini-pro'
        ]
        
        for model_name in model_names:
            try:
                print(f"🔍 Testing model: {model_name}")
                model = genai.GenerativeModel(model_name)
                response = model.generate_content("Hello, are you working?")
                print(f"✅ Success with {model_name}: {response.text}")
                return True
            except Exception as e:
                print(f"❌ {model_name} failed: {e}")
                continue
        
        print("❌ No working Gemini models found")
        return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    api_key = input("Enter your Gemini API key: ").strip()
    test_gemini_api(api_key)