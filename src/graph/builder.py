from langgraph.graph import END, START, StateGraph

from graph.nodes import (
    DATA_AGENTS,
    analyzer_node,
    collector_node,
    get_next_step,
    orchestrator_plan_node,
    orchestrator_respond_node,
    preprocessor_node,
    reviser_node,
    summarizer_node,
    trainer_node,
    validator_node,
)
from graph.state import AgentState


NODE_FUNCS = {
    "data_collector": collector_node,
    "data_preprocessor": preprocessor_node,
    "data_validator": validator_node,
    "data_analyzer": analyzer_node,
    "trainer": trainer_node,
    "model_reviser": reviser_node,
    "summarizer": summarizer_node,
}


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("orchestrator_plan", orchestrator_plan_node)
    graph.add_node("orchestrator_respond", orchestrator_respond_node)
    for name, func in NODE_FUNCS.items():
        graph.add_node(name, func)

    graph.add_edge(START, "orchestrator_plan")

    routes = {name: name for name in DATA_AGENTS}
    routes["orchestrator_respond"] = "orchestrator_respond"

    graph.add_conditional_edges("orchestrator_plan", get_next_step, routes)
    for name in DATA_AGENTS:
        graph.add_conditional_edges(name, get_next_step, routes)

    graph.add_edge("orchestrator_respond", END)

    return graph.compile()
