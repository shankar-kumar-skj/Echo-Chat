# check_langchain.py
import sys

print("Python version:", sys.version)
print("=" * 60)

try:
    import langchain
    print(f"LangChain version: {langchain.__version__}")
except ImportError:
    print("LangChain not installed")
    sys.exit(1)

print("\nChecking langchain.agents imports...")
import langchain.agents as agents
available = [name for name in dir(agents) if not name.startswith("_")]
print("Available in langchain.agents:", available)

print("\nTrying specific imports for LangChain 1.x...")

# New API: create_agent (LangGraph-based)
try:
    from langchain.agents import create_agent
    print("✅ create_agent imported (LangChain 1.x)")
except ImportError as e:
    print(f"❌ create_agent: {e}")

# Check legacy imports
print("\nChecking legacy imports (should fail in LangChain >=1.0):")
try:
    from langchain.agents import create_react_agent
    print("   create_react_agent exists (legacy)")
except ImportError:
    print("   create_react_agent: Not available (expected)")

try:
    from langchain.agents import AgentExecutor
    print("   AgentExecutor exists (legacy)")
except ImportError:
    print("   AgentExecutor: Not available (expected)")

try:
    from langchain.agents import initialize_agent
    print("   initialize_agent exists (legacy)")
except ImportError:
    print("   initialize_agent: Not available (expected)")

# Check LangGraph (optional but recommended for create_agent)
print("\nChecking LangGraph (optional but recommended for create_agent):")
try:
    import langgraph
    version = getattr(langgraph, '__version__', 'unknown')
    print(f"✅ LangGraph installed (version: {version})")
except ImportError:
    print("⚠️ LangGraph not installed. The `create_agent` may still work, but if you see errors, run: pip install langgraph")

print("\n" + "=" * 60)
print("💡 Summary for your LangChain version:")
if "create_agent" in available:
    print("✅ You have LangChain 1.x with `create_agent` – use the LangChain agent.")
    if "langgraph" not in sys.modules:
        print("⚠️ LangGraph is not installed. You may need it for `create_agent` to work properly.")
        print("   Run: pip install langgraph")
else:
    print("❌ `create_agent` not available – fallback to direct Gemini agent.")
print("=" * 60)
print("✅ Diagnostics complete.")