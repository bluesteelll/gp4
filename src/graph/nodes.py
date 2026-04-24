from workflow import agents, prompts


def collector_node(state):
    response = agents["data_collector"].invoke([
        ("system", prompts["data_collector"]),
        ("user", "Collect raw data"),
    ])
    return {"data": response.content}


def preprocessor_node(state):
    response = agents["data_preprocessor"].invoke([
        ("system", prompts["data_preprocessor"]),
        ("user", f"Preprocess: {state['data']}"),
    ])
    return {"data": response.content}


def validator_node(state):
    response = agents["data_validator"].invoke([
        ("system", prompts["data_validator"]),
        ("user", f"Validate: {state['data']}"),
    ])
    return {"data": response.content}


def analyzer_node(state):
    response = agents["data_analyzer"].invoke([
        ("system", prompts["data_analyzer"]),
        ("user", f"Analyze: {state['data']}"),
    ])
    return {"data": response.content}


def trainer_node(state):
    response = agents["trainer"].invoke([
        ("system", prompts["trainer"]),
        ("user", f"Train the model on: {state['data']}"),
    ])
    return {"data": response.content}


def reviser_node(state):
    response = agents["model_reviser"].invoke([
        ("system", prompts["model_reviser"]),
        ("user", f"Evaluate the result: {state['data']}"),
    ])
    return {"data": response.content}
