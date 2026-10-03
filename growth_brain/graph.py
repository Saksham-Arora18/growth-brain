from langgraph.graph import StateGraph, END
from .state import State
from . import agents as A

MAX_REVISIONS = 2

def _route(s):
    return "revise" if (not s["approved"] and s["round"] < MAX_REVISIONS) else "done"

def build():
    g = StateGraph(State)
    for name, fn in [("trends", A.trend_node), ("strategy", A.strategy_node), ("write", A.write_node),
                     ("critique", A.critique_node), ("revise", A.revise_node)]:
        g.add_node(name, fn)
    g.set_entry_point("trends")
    g.add_edge("trends", "strategy")
    g.add_edge("strategy", "write")
    g.add_edge("write", "critique")
    g.add_conditional_edges("critique", _route, {"revise": "revise", "done": END})
    g.add_edge("revise", "critique")
    return g.compile()
