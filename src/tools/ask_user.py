from langchain_core.tools import tool


@tool
def ask_user(question):
    """Ask the user a clarifying question via console. Blocks until they respond. Returns their answer as a string."""
    print(f"\n[Orchestrator]: {question}")
    return input("You: ")
