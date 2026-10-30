import argparse
import json
from uuid import uuid4
from .domain import Principal


def main():
    parser = argparse.ArgumentParser(description="FieldOps simulation; --live makes a billable Bedrock call")
    parser.add_argument("--equipment", default="P-101")
    parser.add_argument("--role", choices=["technician", "supervisor"], default="technician")
    parser.add_argument("--site", choices=["WEST", "EAST"], default="WEST")
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--guardrail-id")
    parser.add_argument("--guardrail-version")
    args = parser.parse_args()
    from langgraph.types import Command
    from .workflow import build_workflow
    principal = Principal("local-demo-user", args.role, (args.site,))
    graph = build_workflow(principal, args.live, args.guardrail_id, args.guardrail_version)
    config = {"configurable": {"thread_id": str(uuid4())}}
    try:
        graph.invoke({"equipment_id": args.equipment}, config)
        pending = graph.get_state(config).values
        print(json.dumps(pending["draft"], indent=2))
        if args.role != "supervisor":
            print("Paused: technician may draft but cannot approve. No work order was committed.")
            return
        answer = input("Approve this SIMULATED work order? Type approve or reject: ").strip()
        if answer not in {"approve", "reject"}:
            print("No explicit decision; leaving pending.")
            return
        result = graph.invoke(Command(resume=answer == "approve"), config)
        print(json.dumps(result["result"], indent=2))
    except (PermissionError, ValueError, RuntimeError) as exc:
        parser.exit(1, f"Stopped: {exc}\n")


if __name__ == "__main__":
    main()
