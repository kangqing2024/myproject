from bpmn_assistant.services.bpmn_process_transformer import BpmnProcessTransformer


class TestBpmnProcessTransformer:

    def test_transform_exclusive_gateway_with_empty_path(
        self, empty_gateway_path_process
    ):

        self.transformer = BpmnProcessTransformer()

        result = self.transformer.transform(empty_gateway_path_process)

        expected = {
            "elements": [
                {
                    "id": "start",
                    "type": "startEvent",
                    "label": None,
                    "incoming": [],
                    "outgoing": ["start-task1"],
                },
                {
                    "id": "task1",
                    "type": "task",
                    "label": "Perform a simple task",
                    "incoming": ["start-task1"],
                    "outgoing": ["task1-task2"],
                },
                {
                    "id": "task2",
                    "type": "task",
                    "label": "Perform a second task",
                    "incoming": ["task1-task2"],
                    "outgoing": ["task2-exclusive1"],
                },
                {
                    "id": "exclusive1",
                    "type": "exclusiveGateway",
                    "label": "Decision Point",
                    "incoming": ["task2-exclusive1"],
                    "outgoing": ["exclusive1-task3", "exclusive1-end"],
                },
                {
                    "id": "task3",
                    "type": "task",
                    "label": "Perform a third task",
                    "incoming": ["exclusive1-task3"],
                    "outgoing": ["task3-end"],
                },
                {
                    "id": "end",
                    "type": "endEvent",
                    "label": None,
                    "incoming": ["task3-end", "exclusive1-end"],
                    "outgoing": [],
                },
            ],
            "flows": [
                {
                    "id": "start-task1",
                    "sourceRef": "start",
                    "targetRef": "task1",
                    "condition": None,
                },
                {
                    "id": "task1-task2",
                    "sourceRef": "task1",
                    "targetRef": "task2",
                    "condition": None,
                },
                {
                    "id": "task2-exclusive1",
                    "sourceRef": "task2",
                    "targetRef": "exclusive1",
                    "condition": None,
                },
                {
                    "id": "task3-end",
                    "sourceRef": "task3",
                    "targetRef": "end",
                    "condition": None,
                },
                {
                    "id": "exclusive1-task3",
                    "sourceRef": "exclusive1",
                    "targetRef": "task3",
                    "condition": "Condition A",
                },
                {
                    "id": "exclusive1-end",
                    "sourceRef": "exclusive1",
                    "targetRef": "end",
                    "condition": "Condition B",
                },
            ],
        }

        assert result == expected

    def test_transform_exclusive_gateway_with_end_event_in_path(
        self, eg_end_event_in_path_process
    ):

        self.transformer = BpmnProcessTransformer()

        result = self.transformer.transform(eg_end_event_in_path_process)

        expected = {
            "elements": [
                {
                    "id": "start",
                    "type": "startEvent",
                    "label": None,
                    "incoming": [],
                    "outgoing": ["start-exclusive1"],
                },
                {
                    "id": "exclusive1",
                    "type": "exclusiveGateway",
                    "label": "Decision Point",
                    "incoming": ["start-exclusive1"],
                    "outgoing": ["exclusive1-task1", "exclusive1-end1"],
                },
                {
                    "id": "task1",
                    "type": "task",
                    "label": "Perform the first task",
                    "incoming": ["exclusive1-task1"],
                    "outgoing": ["task1-task2"],
                },
                {
                    "id": "end1",
                    "type": "endEvent",
                    "label": None,
                    "incoming": ["exclusive1-end1"],
                    "outgoing": [],
                },
                {
                    "id": "task2",
                    "type": "task",
                    "label": "Perform the second task",
                    "incoming": ["task1-task2"],
                    "outgoing": ["task2-end2"],
                },
                {
                    "id": "end2",
                    "type": "endEvent",
                    "label": None,
                    "incoming": ["task2-end2"],
                    "outgoing": [],
                },
            ],
            "flows": [
                {
                    "id": "start-exclusive1",
                    "sourceRef": "start",
                    "targetRef": "exclusive1",
                    "condition": None,
                },
                {
                    "id": "task1-task2",
                    "sourceRef": "task1",
                    "targetRef": "task2",
                    "condition": None,
                },
                {
                    "id": "exclusive1-task1",
                    "sourceRef": "exclusive1",
                    "targetRef": "task1",
                    "condition": "Condition A",
                },
                {
                    "id": "exclusive1-end1",
                    "sourceRef": "exclusive1",
                    "targetRef": "end1",
                    "condition": "Condition B",
                },
                {
                    "id": "task2-end2",
                    "sourceRef": "task2",
                    "targetRef": "end2",
                    "condition": None,
                },
            ],
        }

        assert result == expected
