"""Explicit workflow: authorize/read -> assess -> draft -> human review."""
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt
from .domain import Principal, read_equipment, draft_work_order, approve_work_order
from .model import assess


class State(TypedDict, total=False):
    equipment_id: str
    readings: dict
    assessment: str
    draft: dict
    result: dict


def build_workflow(principal: Principal, live: bool = False,
                   guardrail_id: str | None = None, guardrail_version: str | None = None):
    # Principal comes from the application boundary, not graph/model payloads.
    def read(state):
        return {"readings": read_equipment(principal, state["equipment_id"])}

    def analyze(state):
        return {"assessment": assess(state["readings"], live, guardrail_id, guardrail_version)}

    def draft(state):
        return {"draft": draft_work_order(principal, state["readings"], state["assessment"])}

    def review(state):
        decision = interrupt({"review_required": True, "draft": state["draft"]})
        return {"result": approve_work_order(principal, state["draft"], decision)}

    graph = StateGraph(State)
    for name, node in [("read", read), ("assess", analyze), ("draft", draft), ("review", review)]:
        graph.add_node(name, node)
    for a, b in [(START, "read"), ("read", "assess"), ("assess", "draft"),
                 ("draft", "review"), ("review", END)]:
        graph.add_edge(a, b)
    return graph.compile(checkpointer=InMemorySaver())
