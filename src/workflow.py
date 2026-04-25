import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from agents import (
    data_analyzer,
    data_collector,
    data_preprocessor,
    data_validator,
    model_reviser,
    orchestrator,
    summarizer,
    trainer,
)

load_dotenv()

API_KEY = os.getenv("AIHUBMIX_API_KEY")
BASE_URL = os.getenv("AIHUBMIX_BASE_URL")
ROOT = Path(__file__).parents[1]
PROMPT_DIR = ROOT / "system_prompts"


def load_prompt(name):
    return (PROMPT_DIR / f"{name}.md").read_text(encoding="utf-8")


def make_llm(model, temperature=0.0):
    return ChatOpenAI(
        model=model,
        api_key=API_KEY,
        base_url=BASE_URL,
        temperature=temperature,
    )


METAS = [
    orchestrator,
    data_collector,
    data_preprocessor,
    data_validator,
    data_analyzer,
    trainer,
    model_reviser,
    summarizer,
]


def build_agent(meta):
    return create_react_agent(
        model=make_llm(meta.MODEL),
        tools=meta.TOOLS,
        prompt=load_prompt(meta.NAME),
        name=meta.NAME,
    )


agents = {meta.NAME: build_agent(meta) for meta in METAS}
