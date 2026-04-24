import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from agents import (
    data_analyzer,
    data_collector,
    data_preprocessor,
    data_validator,
    model_reviser,
    trainer,
)

load_dotenv()

API_KEY = os.getenv("AIHUBMIX_API_KEY")
BASE_URL = os.getenv("AIHUBMIX_BASE_URL")


def create_agent(model, temperature=0.0):
    return ChatOpenAI(
        model=model,
        api_key=API_KEY,
        base_url=BASE_URL,
        temperature=temperature,
    )


METAS = [
    data_collector,
    data_preprocessor,
    data_validator,
    data_analyzer,
    trainer,
    model_reviser,
]

agents = {meta.NAME: create_agent(meta.MODEL) for meta in METAS}
