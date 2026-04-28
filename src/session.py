import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parents[1]
DATA_DIR = ROOT / "data"
SESSIONS_DIR = DATA_DIR / "sessions"
LONG_TERM_MEMORY_PATH = DATA_DIR / "long_term_memory.json"
SUBFOLDERS = ["raw", "processed", "reports", "models"]


def create_session():
    session_id = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    session_dir = SESSIONS_DIR / session_id
    for sub in SUBFOLDERS:
        (session_dir / sub).mkdir(parents=True, exist_ok=True)

    update_meta(
        session_dir,
        session_id=session_id,
        started_at=datetime.now().isoformat(),
        status="running",
    )
    return session_id, session_dir


def update_meta(session_dir, **fields):
    meta_path = session_dir / "session.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
    meta.update(fields)
    meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    return meta


def session_paths(session_dir):
    p = Path(session_dir)
    return {
        "raw_data": p / "raw" / "dataset.csv",
        "processed_data": p / "processed" / "clean.csv",
        "test_data": p / "processed" / "test.csv",
        "validation_report": p / "reports" / "validation.json",
        "analysis_report": p / "reports" / "analysis.json",
        "evaluation_report": p / "reports" / "evaluation.json",
        "predictions": p / "reports" / "predictions.csv",
        "model": p / "models" / "model.pkl",
        "model_dir": p / "models",
        "summary": p / "summary.md",
        "conversations": p / "conversations.json",
    }


def save_artifact(session_dir, subfolder, filename, content):
    path = session_dir / subfolder / filename
    if isinstance(content, bytes):
        path.write_bytes(content)
    else:
        path.write_text(str(content), encoding="utf-8")
    return path


def serialize_message(msg):
    if hasattr(msg, "model_dump"):
        return msg.model_dump()
    if hasattr(msg, "dict"):
        return msg.dict()
    if isinstance(msg, dict):
        return msg
    return {"content": str(msg)}


def save_conversations(session_dir, messages):
    path = session_dir / "conversations.json"
    serialized = [serialize_message(m) for m in messages]
    path.write_text(
        json.dumps(serialized, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )
    return path


def load_long_term_memory():
    if LONG_TERM_MEMORY_PATH.exists():
        return json.loads(LONG_TERM_MEMORY_PATH.read_text(encoding="utf-8"))
    return []


def append_to_long_term_memory(entry):
    memory = load_long_term_memory()
    memory.append(entry)
    LONG_TERM_MEMORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    LONG_TERM_MEMORY_PATH.write_text(
        json.dumps(memory, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return memory
