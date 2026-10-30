import unittest
from fieldops.domain import Principal


class WorkflowTests(unittest.TestCase):
    def test_review_interrupt_and_explicit_resume(self):
        from fieldops.workflow import build_workflow
        from langgraph.types import Command
        graph = build_workflow(Principal("supervisor1", "supervisor", ("WEST",)))
        config = {"configurable": {"thread_id": "test-review"}}
        graph.invoke({"equipment_id": "P-101"}, config)
        snapshot = graph.get_state(config)
        self.assertEqual(snapshot.values["draft"]["status"], "PENDING_APPROVAL")
        self.assertNotIn("result", snapshot.values)
        result = graph.invoke(Command(resume=True), config)
        self.assertEqual(result["result"]["status"], "APPROVED_SIMULATION")

    def test_cross_site_denied_before_model_call(self):
        from fieldops.workflow import build_workflow
        graph = build_workflow(Principal("tech1", "technician", ("WEST",)))
        with self.assertRaises(PermissionError):
            graph.invoke({"equipment_id": "P-202"},
                         {"configurable": {"thread_id": "test-denied"}})
