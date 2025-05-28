import pytest

from bpmn_assistant.services.validate_bpmn import validate_bpmn


class TestValidateBpmn:

    def test_validate_bpmn_duplicate_id(self, duplicate_id_process):
        with pytest.raises(ValueError) as exc_info:
            validate_bpmn(duplicate_id_process)

        assert str(exc_info.value) == "Duplicate element ID found: task1"
