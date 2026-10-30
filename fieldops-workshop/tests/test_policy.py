import unittest
from fieldops.domain import (Principal, authorize, read_equipment,
                             draft_work_order, approve_work_order)


class PolicyTests(unittest.TestCase):
    def setUp(self):
        self.tech = Principal("t1", "technician", ("WEST",))
        self.supervisor = Principal("s1", "supervisor", ("WEST",))

    def test_cross_site_read_is_denied(self):
        with self.assertRaises(PermissionError):
            read_equipment(self.tech, "P-202")

    def test_unknown_role_and_action_are_denied(self):
        for principal, action in [(Principal("x", "admin", ("WEST",)), "read_equipment"),
                                  (self.supervisor, "shutdown_equipment")]:
            with self.assertRaises(PermissionError):
                authorize(principal, action, "WEST")

    def test_technician_cannot_self_approve(self):
        draft = draft_work_order(self.tech, read_equipment(self.tech, "P-101"), "Inspect")
        with self.assertRaises(PermissionError):
            approve_work_order(self.tech, draft, True)

    def test_explicit_supervisor_decision(self):
        draft = draft_work_order(self.tech, read_equipment(self.tech, "P-101"), "Inspect")
        self.assertEqual(approve_work_order(self.supervisor, draft, True)["status"],
                         "APPROVED_SIMULATION")
        self.assertEqual(approve_work_order(self.supervisor, draft, False)["status"], "REJECTED")
        with self.assertRaises(ValueError):
            approve_work_order(self.supervisor, draft, "true")

    def test_forged_site_rejected(self):
        draft = draft_work_order(self.tech, read_equipment(self.tech, "P-101"), "Inspect")
        draft["site"] = "EAST"
        with self.assertRaises(ValueError):
            approve_work_order(self.supervisor, draft, True)


if __name__ == "__main__":
    unittest.main()
