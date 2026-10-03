from typing import TypedDict, List, Dict, Any

class State(TypedDict):
    niche: str
    trends: List[Dict[str, Any]]
    strategy: Dict[str, Any]
    scripts: List[Dict[str, Any]]
    reviews: List[Dict[str, Any]]
    history: List[Dict[str, Any]]   # critique/revision log
    round: int
    approved: bool
