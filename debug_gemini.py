import google.generativeai as genai
import sys

def debug_gemini_api(api_key):
    print("🔍 Starting Gemini API Debug...")
    print(f"API Key: {api_key[:10]}...{api_key[-10:] if len(api_key) > 20 else ''}")
    
    try:
        # Configure the API
        print("1. Configuring API...")
        genai.configure(api_key=api_key)
        print("   ✅ API configured successfully")
        
        # List available models
        print("2. Listing available models...")
        models = genai.list_models()
        
        # Convert generator to list to see what's available
        model_list = list(models)
        print(f"   ✅ Found {len(model_list)} total models")
        
        # Filter for Gemini models
        gemini_models = [model for model in model_list if 'gemini' in model.name.lower()]
        print(f"   🔍 Found {len(gemini_models)} Gemini models:")
        
        for model in gemini_models:
            supported_methods = []
            if 'generateContent' in model.supported_generation_methods:
                supported_methods.append('generateContent')
            if 'embedContent' in model.supported_generation_methods:
                supported_methods.append('embedContent')
            
            print(f"      - {model.name} (Supports: {', '.join(supported_methods)})")
        
        # Test each Gemini model
        print("3. Testing Gemini models...")
        working_models = []
        
        for model in gemini_models:
            if 'generateContent' in model.supported_generation_methods:
                try:
                    print(f"   Testing: {model.name}...")
                    gen_model = genai.GenerativeModel(model.name)
                    response = gen_model.generate_content("Hello, please respond with 'OK' if you're working.")
                    
                    if response and response.text:
                        print(f"      ✅ {model.name}: SUCCESS - '{response.text.strip()}'")
                        working_models.append(model.name)
                    else:
                        print(f"      ❌ {model.name}: No response text")
                        
                except Exception as e:
                    print(f"      ❌ {model.name}: ERROR - {str(e)}")
        
        if working_models:
            print(f"\n🎉 SUCCESS! Working models: {working_models}")
            return True
        else:
            print("\n❌ No working Gemini models found")
            return False
            
    except Exception as e:
        print(f"❌ Critical error: {str(e)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        api_key = sys.argv[1]
    else:
        api_key = input("Enter your Gemini API key: ").strip()
    
    debug_gemini_api(api_key)