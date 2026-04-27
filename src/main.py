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
            "plan": [],
            "step": 0,
            "current_step": "start",
            "next": "",
            "session_log": [],
            "code_outputs": [],
            "notes": {},
            "dataset_path": None,
            "target_column": None,
            "task_type": None,
            "dataset_info": None,
            "validation_info": None,
            "preprocessing_info": None,
            "feature_engineering_info": None,
            "created_features": [],
            "llm_decisions": [],
            "training_results": None,
            "best_model_name": None,
            "best_model_path": None,
            "metrics": None,
            "long_term_memory": {"history": memory},
            "error": None,
            "retry_count": 0,
            "final_report": None,
        })

        print(result.get("final_report", "(no report)"))
        print(f"\n[Session: {session_id} | Dir: {session_dir}]\n")


main()
