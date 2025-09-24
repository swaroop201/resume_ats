import json, os
from typing import Dict, List

DEFAULT_PATHS = [
    os.path.join("app","resources","resources_catalog.json"),
    "resources_catalog.json"
]

def _load_catalog() -> Dict:
    for p in DEFAULT_PATHS:
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8") as f:
                return json.load(f)
    return {}

def recommend_for_gaps(gaps: List[str], max_items:int=3) -> Dict[str, Dict[str, List[Dict[str,str]]]]:
    cat = _load_catalog()
    out = {}
    for g in gaps:
        if g in cat:
            entry = cat[g]
            out[g] = {
                "micro_projects": entry.get("micro_projects", [])[:max_items],
                "open_source": entry.get("open_source", [])[:max_items],
                "learn": entry.get("learn", [])[:max_items]
            }
    return out
