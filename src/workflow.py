import os
from pathlib import Path

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
PROMPT_DIR = Path(__file__).parents[1] / "system_prompts"


def create_agent(meta, temperature=0.0):
    return ChatOpenAI(
        model=meta.MODEL,
        api_key=API_KEY,
        base_url=BASE_URL,
        temperature=temperature,
    )


def load_prompt(name):
    return (PROMPT_DIR / f"{name}.md").read_text(encoding="utf-8")


METAS = [
    data_collector,
    data_preprocessor,
    data_validator,
    data_analyzer,
    trainer,
    model_reviser,
]

agents = {meta.NAME: create_agent(meta) for meta in METAS}
prompts = {meta.NAME: load_prompt(meta.NAME) for meta in METAS}
