import json, pathlib
P = pathlib.Path("data/memory.json")

def load():
    return json.loads(P.read_text()) if P.exists() else {"bucket_scores": {}, "insights": []}

def save(m):
    P.parent.mkdir(exist_ok=True)
    P.write_text(json.dumps(m, indent=2))
