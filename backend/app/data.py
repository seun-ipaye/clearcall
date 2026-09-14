import json
from functools import lru_cache
from pathlib import Path
from typing import List

from app.models import CallRecord

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "calls.json"


@lru_cache(maxsize=1)
def load_calls() -> List[CallRecord]:
    with open(DATA_PATH) as f:
        raw = json.load(f)
    return [CallRecord.model_validate(record) for record in raw]
