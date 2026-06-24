# check_gemini.py
import os
import sys
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    print("❌ GOOGLE_API_KEY not found in .env")
    sys.exit(1)

try:
    import google.generativeai as genai
    genai.configure(api_key=API_KEY)
except ImportError:
    print("❌ google-generativeai package not installed")
    sys.exit(1)

print("🔍 Checking Gemini API access...")

# Try to list available models (no cost)
try:
    models = genai.list_models()
    available = []
    for m in models:
        if "generateContent" in m.supported_generation_methods:
            available.append(m.name.split("/")[-1])
    if available:
        print(f"✅ Found {len(available)} model(s) supporting generateContent:")
        for name in available[:5]:
            print(f"   - {name}")
        if len(available) > 5:
            print(f"   ... and {len(available)-5} more")
    else:
        print("⚠️ No model with generateContent support found.")
        print("   Please check your API key and project permissions.")
except Exception as e:
    print(f"❌ Failed to list models: {e}")
    sys.exit(1)

# Try a minimal generation (costs a tiny amount)
try:
    model = genai.GenerativeModel(available[0] if available else "gemini-1.5-flash")
    response = model.generate_content("Hello, world!")
    if response.text:
        print("✅ Minimal generation test passed.")
        print(f"   Response preview: {response.text[:60]}...")
    else:
        print("⚠️ Generation returned empty response.")
except Exception as e:
    print(f"❌ Generation test failed: {e}")
    sys.exit(1)

print("\n✨ Gemini API is ready and working.")