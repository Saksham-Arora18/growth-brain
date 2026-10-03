import argparse, json, pathlib, random
from growth_brain.graph import build
from growth_brain.agents import learn

OUT = pathlib.Path("outputs"); OUT.mkdir(exist_ok=True)

def plan(niche):
    s = build().invoke({"niche": niche, "history": [], "round": 0, "approved": False})
    (OUT / "trends.json").write_text(json.dumps(s["trends"], indent=2))
    (OUT / "strategy.json").write_text(json.dumps(s["strategy"], indent=2))
    (OUT / "scripts_final.json").write_text(json.dumps(s["scripts"], indent=2))
    (OUT / "revision_history.json").write_text(json.dumps(s["history"], indent=2))
    md = ["# Weekly strategy\n"]
    for b in s["strategy"]["buckets"]:
        md.append(f"- **{b['name']}** ({b['share_pct']}%): {b['goal']}")
    md.append("\n## Plan")
    for d in s["strategy"]["weekly_plan"]:
        md.append(f"- {d['day']}: [{d['bucket']}] {d['idea']} ({d.get('format','')})")
    (OUT / "strategy.md").write_text("\n".join(md))
    print(f"Done. Revision rounds: {s['round']}, approved: {s['approved']}. See outputs/")

def feedback(simulate):
    f = pathlib.Path("data/feedback.json")
    if simulate:
        buckets = [b["name"] for b in json.loads((OUT / "strategy.json").read_text())["buckets"]]
        random.seed(7)
        posts = [{"bucket": b, "views": random.randint(800, 5000), "likes": 0, "comments": 0, "saves": 0, "shares": 0}
                 for b in buckets for _ in range(4)]
        boost = buckets[0]  # demo: first bucket outperforms
        for p in posts:
            m = 0.12 if p["bucket"] == boost else 0.03
            p["likes"] = int(p["views"] * m); p["comments"] = int(p["views"] * m / 8)
            p["saves"] = int(p["views"] * m / 3); p["shares"] = int(p["views"] * m / 4)
        f.write_text(json.dumps(posts, indent=2))
    print(json.dumps(learn(json.loads(f.read_text())), indent=2))
    print("Memory updated. Re-run `python run.py plan` to see the strategy shift.")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["plan", "feedback"])
    ap.add_argument("--niche", default="AI & tech education creator")
    ap.add_argument("--simulate", action="store_true")
    a = ap.parse_args()
    plan(a.niche) if a.cmd == "plan" else feedback(a.simulate)
