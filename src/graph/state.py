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
    current_step: str
    final_report: Optional[str]

    next: str

    session_log: Annotated[List[str], operator.add]
    code_outputs: Annotated[List[str], operator.add]
    notes: Annotated[Dict[str, str], merge_notes]

    dataset_path: Optional[str]
    target_column: Optional[str]
    task_type: Optional[str]

    dataset_info: Optional[Dict[str, Any]]
    validation_info: Optional[Dict[str, Any]]
    preprocessing_info: Optional[Dict[str, Any]]
    feature_engineering_info: Optional[Dict[str, Any]]
    created_features: Annotated[List[str], operator.add]

    llm_decisions: Annotated[List[Dict[str, Any]], operator.add]

    training_results: Optional[Dict[str, Any]]
    best_model_name: Optional[str]
    best_model_path: Optional[str]
    test_dataset_path: Optional[str]
    metrics: Optional[Dict[str, Any]]

    long_term_memory: Optional[Dict[str, Any]]

    error: Optional[str]
    retry_count: int
