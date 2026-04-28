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


# LLM hyperparameter configuration with rationale.
#
# temperature — controls randomness of output:
#   0.0 = fully deterministic, best for code generation and strict structured output
#   0.2–0.4 = slight creativity, good for analysis and planning with some flexibility
#   0.7+ = high creativity, suitable for free-form text generation
#
# max_tokens — hard cap on output length:
#   prevents runaway verbose responses and reduces cost on simple tasks
#
# Note: temperature and top_p cannot be specified simultaneously on most API providers.
# We use only temperature for explicit control; top_p remains at provider default.

LLM_CONFIGS = {
    # Orchestrator: needs creativity to plan and write readable final reports,
    # but must reliably output valid JSON → moderate temperature.
    "orchestrator": {
        "temperature": 0.2,
        "max_tokens": 4096,
    },
    # Data collector: purely functional — find and save a dataset.
    # Deterministic to avoid hallucinated URLs or invented dataset names.
    "data_collector": {
        "temperature": 0.0,
        "max_tokens": 2048,
    },
    # Data preprocessor: writes pandas/numpy code → must be deterministic.
    # Low temperature prevents creative but incorrect transformations.
    "data_preprocessor": {
        "temperature": 0.0,
        "max_tokens": 4096,
    },
    # Data validator: binary pass/fail decision + structured JSON → fully deterministic.
    "data_validator": {
        "temperature": 0.0,
        "max_tokens": 2048,
    },
    # Data analyzer: EDA requires analytical reasoning, not just code execution.
    # Slight temperature allows more insightful interpretations of distributions.
    "data_analyzer": {
        "temperature": 0.3,
        "max_tokens": 4096,
    },
    # Trainer: generates sklearn training code → deterministic to ensure correctness.
    # Higher max_tokens because training scripts can be long.
    "trainer": {
        "temperature": 0.0,
        "max_tokens": 8192,
    },
    # Model reviser: needs nuanced judgment (overfitting vs underfitting, business context).
    # Moderate temperature enables richer reasoning; extended thinking model amplifies this.
    "model_reviser": {
        "temperature": 0.4,
        "max_tokens": 4096,
    },
    # Summarizer: free-form markdown writing → higher temperature for readable prose.
    "summarizer": {
        "temperature": 0.5,
        "max_tokens": 2048,
    },
}


def make_llm(model, **kwargs):
    return ChatOpenAI(
        model=model,
        api_key=API_KEY,
        base_url=BASE_URL,
        **kwargs,
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
    cfg = LLM_CONFIGS.get(meta.NAME, {"temperature": 0.0})
    return create_react_agent(
        model=make_llm(meta.MODEL, **cfg),
        tools=meta.TOOLS,
        state_modifier=load_prompt(meta.NAME),
    )


agents = {meta.NAME: build_agent(meta) for meta in METAS}
