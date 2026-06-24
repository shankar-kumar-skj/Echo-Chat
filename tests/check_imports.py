# check_imports.py
import sys
import subprocess
import importlib

def check_import(module_name, display_name=None):
    """Try to import a module and print result."""
    if display_name is None:
        display_name = module_name
    try:
        importlib.import_module(module_name)
        print(f"✅ {display_name} imported successfully.")
        return True
    except ImportError as e:
        print(f"❌ {display_name} import FAILED: {e}")
        return False

def check_project_file(filename, module_name):
    """Try to import a local Python file."""
    try:
        importlib.import_module(module_name)
        print(f"✅ {filename} imported successfully.")
        return True
    except ImportError as e:
        print(f"❌ {filename} import FAILED: {e}")
        return False

def main():
    print("=" * 60)
    print("Checking Python environment and project imports...")
    print("=" * 60)

    # --- 1. Check required packages ---
    packages = [
        ("pandas", "pandas"),
        ("kagglehub", "kagglehub"),
        ("dotenv", "python-dotenv"),
        ("google.generativeai", "google-generativeai"),
        ("langchain", "langchain"),
        ("langchain_community", "langchain-community"),
        ("langchain_google_genai", "langchain-google-genai"),
        ("faiss", "faiss-cpu"),
        ("tiktoken", "tiktoken"),
        ("streamlit", "streamlit (optional)"),
        ("pytest", "pytest (optional)"),
    ]
    print("\n[Package imports]")
    all_packages_ok = True
    for mod, name in packages:
        if not check_import(mod, name):
            all_packages_ok = False

    # --- 2. Check project files ---
    project_files = [
        ("tools.py", "tools"),
        ("agent.py", "agent"),
        ("gemini_agent.py", "gemini_agent"),
        ("langchain_agent.py", "langchain_agent"),
        ("main.py", "main"),
    ]
    print("\n[Project file imports]")
    all_files_ok = True
    for filename, modname in project_files:
        if not check_project_file(filename, modname):
            all_files_ok = False

    # --- 3. Check Gemini API key ---
    print("\n[Gemini API key]")
    try:
        from dotenv import load_dotenv
        import os
        load_dotenv()
        api_key = os.getenv("GOOGLE_API_KEY")
        if api_key:
            print("✅ GOOGLE_API_KEY found in .env or environment.")
        else:
            print("❌ GOOGLE_API_KEY not set. Please add it to .env.")
    except Exception as e:
        print(f"❌ Could not check API key: {e}")

    # --- 4. Summary ---
    print("\n" + "=" * 60)
    if all_packages_ok and all_files_ok:
        print("✅ All required imports succeeded! Your environment is ready.")
    else:
        print("⚠️ Some imports failed. Check the errors above.")
    print("=" * 60)

if __name__ == "__main__":
    main()