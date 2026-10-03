import datetime, json, copy
from .llm import ask_json
from . import memory

# ---- Layer 1: Trend Intelligence (live web search + LLM extraction) ----
def trend_node(s):
    snippets = []
    try:
        from ddgs import DDGS
        year = datetime.date.today().year
        with DDGS() as d:
            for q in (f"{s['niche']} instagram reels trends {year}", f"trending instagram formats audio {year}"):
                snippets += [r["title"] + ": " + r["body"] for r in d.text(q, max_results=5)]
    except Exception as e:
        snippets = [f"(live search unavailable: {e})"]
    out = ask_json(
        "You are an Instagram trend analyst.",
        f"Niche: {s['niche']}\nLive search snippets:\n" + "\n".join(snippets) +
        '\nExtract 5 actionable trends as {"trends":[{"topic":"","why_it_works":"","format":""}]}')
    return {"trends": out["trends"]}

# ---- Layer 2: Strategy (buckets + weekly plan, reads learned memory) ----
def strategy_node(s):
    mem = memory.load()
    out = ask_json(
        "You are a social media growth strategist.",
        f"Niche: {s['niche']}\nTrends: {json.dumps(s['trends'])}\n"
        f"Learned from past performance (bucket engagement scores + insights, weight winners higher): {json.dumps(mem)}\n"
        'Return {"buckets":[{"name":"","goal":"","share_pct":0,"ideas":[""]}],'
        '"weekly_plan":[{"day":"","bucket":"","idea":"","format":""}]}. '
        "3-4 buckets, share_pct sums to 100, 7-day plan.")
    return {"strategy": out}

# ---- Layer 3a: Script writer ----
def write_node(s):
    items = s["strategy"]["weekly_plan"][:3]
    out = ask_json(
        "You write short-form Instagram Reel scripts.",
        f"Plan items: {json.dumps(items)}\nTrends: {json.dumps(s['trends'])}\n"
        'Return {"scripts":[{"id":0,"bucket":"","hook":"","body":"","cta":""}]} one per item.')
    return {"scripts": out["scripts"], "round": 0}

# ---- Layer 3b: Critic (scores, decides approval) ----
def critique_node(s):
    out = ask_json(
        "You are a harsh but fair content critic. Score 1-10 on hook strength, clarity, trend fit.",
        f"Scripts: {json.dumps(s['scripts'])}\n"
        'Return {"reviews":[{"id":0,"score":0,"notes":""}]}. Be specific in notes.')
    reviews = out["reviews"]
    approved = all(r["score"] >= 8 for r in reviews)
    hist = s.get("history", []) + [{"round": s["round"], "scripts": copy.deepcopy(s["scripts"]),
                                    "reviews": reviews, "approved": approved}]
    return {"reviews": reviews, "approved": approved, "history": hist}

# ---- Layer 3c: Reviser ----
def revise_node(s):
    out = ask_json(
        "You revise scripts using critic notes. Fix every note.",
        f"Scripts: {json.dumps(s['scripts'])}\nReviews: {json.dumps(s['reviews'])}\n"
        'Return {"scripts":[{"id":0,"bucket":"","hook":"","body":"","cta":""}]}.')
    return {"scripts": out["scripts"], "round": s["round"] + 1}

# ---- Layer 4: Feedback learning ----
def learn(posts):
    agg = {}
    for p in posts:
        a = agg.setdefault(p["bucket"], {"score": 0.0, "n": 0})
        a["score"] += (p["likes"] + 2 * p["comments"] + 3 * p["saves"] + 3 * p["shares"]) / max(p["views"], 1)
        a["n"] += 1
    scores = {b: round(v["score"] / v["n"], 4) for b, v in agg.items()}
    insights = ask_json(
        "You analyse Instagram performance.",
        f"Avg weighted engagement rate per bucket: {json.dumps(scores)}\n"
        'Return {"insights":["3 short, actionable lessons for next week\'s plan"]}')["insights"]
    mem = {"bucket_scores": scores, "insights": insights}
    memory.save(mem)
    return mem
