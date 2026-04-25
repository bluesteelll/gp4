import sys

from graph.builder import build_graph
from session import create_session, load_long_term_memory

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def main():
    app = build_graph()
    print("Multi-agent ML pipeline. Type 'exit' to quit.\n")

    while True:
        user_input = input("You: ").strip()
        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit"):
            break

        session_id, session_dir = create_session()
        memory = load_long_term_memory()

        result = app.invoke({
            "messages": [],
            "task": user_input,
            "session_id": session_id,
            "session_dir": str(session_dir),
            "session_log": [],
            "code_outputs": [],
            "notes": {},
            "plan": [],
            "step": 0,
            "long_term_memory": {"history": memory},
            "retry_count": 0,
        })

        print(result.get("final_report", "(no report)"))
        print(f"\n[Session: {session_id} | Dir: {session_dir}]\n")


main()
