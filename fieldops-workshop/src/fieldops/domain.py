"""Deterministic tools and authorization, independent of model decisions."""
from dataclasses import dataclass
from hashlib import sha256


@dataclass(frozen=True)
class Principal:
    subject: str
    role: str
    sites: tuple[str, ...]


EQUIPMENT = {
    "P-101": {"site": "WEST", "vibration_mm_s": 9.2, "temperature_c": 88,
              "alert": "High vibration; inspection required"},
    "P-202": {"site": "EAST", "vibration_mm_s": 2.1, "temperature_c": 55,
              "alert": "No active alert"},
}


def authorize(principal: Principal, action: str, site: str) -> None:
    permissions = {
        "technician": {"read_equipment", "draft_work_order"},
        "supervisor": {"read_equipment", "draft_work_order", "approve_work_order"},
    }
    if (not principal.subject or site not in principal.sites
            or action not in permissions.get(principal.role, set())):
        raise PermissionError(f"Denied: {action} for site {site}")


def read_equipment(principal: Principal, equipment_id: str) -> dict:
    # Do not expose existence or readings until authorization succeeds.
    record = EQUIPMENT.get(equipment_id)
    if record is None:
        raise ValueError("Unknown equipment ID")
    authorize(principal, "read_equipment", record["site"])
    return {"equipment_id": equipment_id, **record, "simulated": True}


def draft_work_order(principal: Principal, readings: dict, assessment: str) -> dict:
    # Re-read authoritative simulation data; never trust model-supplied site IDs.
    trusted = read_equipment(principal, readings["equipment_id"])
    authorize(principal, "draft_work_order", trusted["site"])
    if not assessment.strip():
        raise ValueError("Assessment must be nonempty")
    order_id = sha256((trusted["equipment_id"] + assessment).encode()).hexdigest()[:12]
    return {"id": order_id, "equipment_id": trusted["equipment_id"],
            "site": trusted["site"], "assessment": assessment,
            "status": "PENDING_APPROVAL", "simulated": True}


def approve_work_order(principal: Principal, draft: dict, approved: bool) -> dict:
    trusted = read_equipment(principal, draft["equipment_id"])
    if draft["site"] != trusted["site"] or draft["status"] != "PENDING_APPROVAL":
        raise ValueError("Invalid draft")
    authorize(principal, "approve_work_order", trusted["site"])
    if type(approved) is not bool:
        raise ValueError("Approval must be an explicit boolean")
    return {**draft, "status": "APPROVED_SIMULATION" if approved else "REJECTED",
            "reviewed_by": principal.subject}
