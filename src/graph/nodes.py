import json
from datetime import datetime
from pathlib import Path

from session import (
    append_to_long_term_memory,
    save_conversations,
    session_paths,
    update_meta,
)
from workflow import agents


MARKER = "AGENT_RESULT_DATA:"
DATA_AGENTS = [
    "data_collector",
    "data_preprocessor",
    "data_validator",
    "data_analyzer",
    "trainer",
    "model_reviser",
    "summarizer",
]


def parse_final_result(text):
    idx = text.rfind(MARKER)
    if idx == -1:
        return {}
    payload = text[idx + len(MARKER):].strip()
    if payload.startswith("```"):
        payload = payload.strip("`").strip()
        if payload.lower().startswith("json"):
            payload = payload[4:].strip()
    try:
        return json.loads(payload)
    except json.JSONDecodeError:
        return {}


def incoming_note(state, agent_name):
    return state.get("notes", {}).get(agent_name, "")


def compose_task(base_task, note):
    if not note:
        return base_task
    return f"Notes from prior agents:\n{note}\n\n---\n\n{base_task}"


def info_from_result(result, fallback_text):
    payload = {k: v for k, v in result.items() if k != "notes"}
    return payload or {"summary": fallback_text}


def run_agent(name, task):
    print(f"\n--- {name} START ---", flush=True)
    response = agents[name].invoke({"messages": [("user", task)]})
    messages = response["messages"]
    final = messages[-1].content
    print(f"--- {name} END ---\n{final[:800]}\n", flush=True)
    return messages, final, parse_final_result(final)


def advance_step(state):
    return state.get("step", 0) + 1


def get_next_step(state):
    plan = state.get("plan", [])
    step = state.get("step", 0)
    if step >= len(plan):
        return "orchestrator_respond"
    next_name = plan[step]
    if next_name not in DATA_AGENTS:
        return "orchestrator_respond"
    return next_name


def orchestrator_plan_node(state):
    task = state["task"]
    history = state.get("long_term_memory", {}).get("history", [])

    user_msg = f"User task: {task}\n\nDecide which agents to run for this task."
    if history:
        user_msg += f"\n\nPast sessions for context:\n{json.dumps(history[-5:], indent=2)}"

    messages, final, result = run_agent("orchestrator", user_msg)
    plan = result.get("plan", [])

    return {
        "messages": messages,
        "plan": plan,
        "step": 0,
        "session_log": [f"orchestrator: planned {plan}"],
    }


def orchestrator_respond_node(state):
    session_dir = Path(state["session_dir"])
    summary_info = {
        "task": state.get("task", ""),
        "plan": state.get("plan", []),
        "preprocessing_info": state.get("preprocessing_info"),
        "dataset_info": state.get("dataset_info"),
        "training_results": state.get("training_results"),
        "metrics": state.get("metrics"),
        "best_model_name": state.get("best_model_name"),
        "error": state.get("error"),
        "session_log": state.get("session_log", []),
        "session_dir": str(session_dir),
    }

    user_msg = (
        f"The pipeline has finished. Here are the results:\n\n"
        f"{json.dumps(summary_info, indent=2, ensure_ascii=False, default=str)}\n\n"
        f"Generate the final markdown report for the user and the structured artifact."
    )
    messages, final, result = run_agent("orchestrator", user_msg)

    final_report = result.get("final_report", final)
    artifact = result.get("artifact", {})

    (session_dir / "final_report.md").write_text(final_report, encoding="utf-8")
    (session_dir / "final_artifact.json").write_text(
        json.dumps(artifact, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )
    update_meta(session_dir, status="completed")

    return {
        "messages": messages,
        "final_report": final_report,
        "session_log": ["orchestrator: report ready"],
    }


def collector_node(state):
    paths = session_paths(state["session_dir"])
    raw_path = paths["raw_data"]

    task = compose_task(
        f"Collect a dataset for ML training and save it to: {raw_path}",
        incoming_note(state, "data_collector"),
    )
    messages, final, result = run_agent("data_collector", task)

    return {
        "messages": messages,
        "dataset_path": str(raw_path),
        "notes": result.get("notes", {}),
        "step": advance_step(state),
        "session_log": ["collector: raw data saved"],
    }


def preprocessor_node(state):
    paths = session_paths(state["session_dir"])
    raw_path = state.get("dataset_path", "")
    processed_path = paths["processed_data"]

    task = compose_task(
        f"Raw dataset: {raw_path}\nClean it and save the processed version to: {processed_path}",
        incoming_note(state, "data_preprocessor"),
    )
    messages, final, result = run_agent("data_preprocessor", task)

    return {
        "messages": messages,
        "dataset_path": str(processed_path),
        "preprocessing_info": info_from_result(result, final),
        "notes": result.get("notes", {}),
        "step": advance_step(state),
        "session_log": ["preprocessor: cleaned"],
    }


def validator_node(state):
    paths = session_paths(state["session_dir"])
    dataset_path = state.get("dataset_path", "")
    report_path = paths["validation_report"]

    task = compose_task(
        f"Dataset to validate: {dataset_path}\nSave the validation report to: {report_path}",
        incoming_note(state, "data_validator"),
    )
    messages, final, result = run_agent("data_validator", task)
    verdict = result.get("verdict", "")
    passed = verdict == "pass"

    return {
        "messages": messages,
        "error": None if passed else (result.get("summary") or final),
        "notes": result.get("notes", {}),
        "step": advance_step(state),
        "session_log": [f"validator: {verdict or 'unknown'}"],
    }


def analyzer_node(state):
    paths = session_paths(state["session_dir"])
    dataset_path = state.get("dataset_path", "")
    report_path = paths["analysis_report"]

    task = compose_task(
        f"Dataset to analyze: {dataset_path}\nSave the analysis report to: {report_path}",
        incoming_note(state, "data_analyzer"),
    )
    messages, final, result = run_agent("data_analyzer", task)

    return {
        "messages": messages,
        "dataset_info": info_from_result(result, final),
        "notes": result.get("notes", {}),
        "step": advance_step(state),
        "session_log": ["analyzer: done"],
    }


def trainer_node(state):
    paths = session_paths(state["session_dir"])
    dataset_path = state.get("dataset_path", "")
    model_path = paths["model"]

    task = compose_task(
        f"Training dataset: {dataset_path}\nSave the trained model to: {model_path}",
        incoming_note(state, "trainer"),
    )
    messages, final, result = run_agent("trainer", task)

    return {
        "messages": messages,
        "best_model_name": result.get("model_name", "model.pkl"),
        "training_results": info_from_result(result, final),
        "notes": result.get("notes", {}),
        "step": advance_step(state),
        "session_log": ["trainer: model saved"],
    }


def reviser_node(state):
    paths = session_paths(state["session_dir"])
    dataset_path = state.get("dataset_path", "")
    model_path = paths["model_dir"] / state.get("best_model_name", "model.pkl")
    eval_path = paths["evaluation_report"]

    task = compose_task(
        f"Model to evaluate: {model_path}\nTest dataset: {dataset_path}\nSave the evaluation report to: {eval_path}",
        incoming_note(state, "model_reviser"),
    )
    messages, final, result = run_agent("model_reviser", task)

    return {
        "messages": messages,
        "metrics": info_from_result(result, final),
        "notes": result.get("notes", {}),
        "step": advance_step(state),
        "session_log": [f"reviser: {result.get('verdict', 'unknown')}"],
    }


def summarizer_node(state):
    session_id = state["session_id"]
    session_dir = Path(state["session_dir"])
    paths = session_paths(session_dir)
    conversations_path = save_conversations(session_dir, state["messages"])
    summary_path = paths["summary"]

    task = compose_task(
        f"Read the agent conversations from: {conversations_path}\n"
        f"Write a concise markdown summary of this pipeline run to: {summary_path}",
        incoming_note(state, "summarizer"),
    )
    messages, final, result = run_agent("summarizer", task)

    append_to_long_term_memory({
        "session_id": session_id,
        "timestamp": datetime.now().isoformat(),
        "summary_path": str(summary_path),
    })
    update_meta(session_dir, summary_path=str(summary_path))

    return {
        "messages": messages,
        "step": advance_step(state),
        "session_log": ["summarizer: done"],
    }
