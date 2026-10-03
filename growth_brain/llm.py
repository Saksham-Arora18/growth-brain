import json, os, re
from dotenv import load_dotenv
load_dotenv()

def ask_json(system: str, user: str, retries: int = 2):
    from langchain_groq import ChatGroq
    llm = ChatGroq(model=os.getenv("MODEL", "llama-3.3-70b-versatile"), temperature=0.4)
    for _ in range(retries + 1):
        txt = llm.invoke([("system", system + "\nReturn ONLY valid JSON, no prose."), ("user", user)]).content
        m = re.search(r"\{.*\}|\[.*\]", txt, re.S)
        try:
            return json.loads(m.group(0))
        except Exception:
            continue
    raise ValueError("LLM did not return valid JSON")
