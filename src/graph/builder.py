from langgraph.graph import END, START, StateGraph

from graph.nodes import (
    analyzer_node,
    collector_node,
    preprocessor_node,
    reviser_node,
    trainer_node,
    validator_node,
)


def build_graph():
    graph = StateGraph(dict)

    graph.add_node("collector", collector_node)
    graph.add_node("preprocessor", preprocessor_node)
    graph.add_node("validator", validator_node)
    graph.add_node("analyzer", analyzer_node)
    graph.add_node("trainer", trainer_node)
    graph.add_node("reviser", reviser_node)

    graph.add_edge(START, "collector")
    graph.add_edge("collector", "preprocessor")
    graph.add_edge("preprocessor", "validator")
    graph.add_edge("validator", "analyzer")
    graph.add_edge("analyzer", "trainer")
    graph.add_edge("trainer", "reviser")
    graph.add_edge("reviser", END)

    return graph.compile()
