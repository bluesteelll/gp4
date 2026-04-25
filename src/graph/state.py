import operator
from typing import TypedDict, Annotated, Optional, List, Dict, Any

from langgraph.graph.message import add_messages


def merge_notes(existing, new):
    if not existing:
        return new or {}
    if not new:
        return existing
    result = dict(existing)
    for key, value in new.items():
        if key in result:
            result[key] = result[key] + "\n\n" + value
        else:
            result[key] = value
    return result


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]

    session_id: str
    session_dir: str

    task: str
    plan: List[str]
    step: int
    final_report: Optional[str]

    next: str

    session_log: Annotated[List[str], operator.add]
    code_outputs: Annotated[List[str], operator.add]
    notes: Annotated[Dict[str, str], merge_notes]

    dataset_path: Optional[str]
    dataset_info: Optional[Dict[str, Any]]
    preprocessing_info: Optional[Dict[str, Any]]
    training_results: Optional[Dict[str, Any]]
    best_model_name: Optional[str]
    metrics: Optional[Dict[str, Any]]

    long_term_memory: Optional[Dict[str, Any]]

    error: Optional[str]
    retry_count: int
