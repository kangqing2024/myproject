from pydantic import ValidationError

from bpmn_assistant.core.enums import BPMNElementType
from bpmn_assistant.core.schemas import BPMNTask, ExclusiveGateway, ParallelGateway


def validate_bpmn(process: list) -> None:
    """
    Validate the BPMN process.
    Args:
        process: The BPMN process in JSON format.
    Raises:
        ValueError: If the BPMN process, or any of its elements, is invalid.
    """
    seen_ids = set()
    for element in process:
        validate_element(element)
        
        if element["id"] in seen_ids:
            raise ValueError(f"Duplicate element ID found: {element['id']}")
        seen_ids.add(element["id"])

        if element["type"] == BPMNElementType.EXCLUSIVE_GATEWAY.value:
            for branch in element["branches"]:
                validate_bpmn(branch["path"])
        if element["type"] == BPMNElementType.PARALLEL_GATEWAY.value:
            for branch in element["branches"]:
                validate_bpmn(branch)


def validate_element(element: dict) -> None:
    """
    Validate the BPMN element.
    Args:
        element: The BPMN element in JSON format.
    Raises:
        ValueError: If the BPMN element is invalid.
    """
    if "id" not in element:
        raise ValueError(f"Element is missing an ID: {element}")
    elif "type" not in element:
        raise ValueError(f"Element is missing a type: {element}")

    supported_elements = [e.value for e in BPMNElementType]

    if element["type"] not in supported_elements:
        raise ValueError(
            f"Unsupported element type: {element['type']}. Supported types: {supported_elements}"
        )

    if element["type"] in [
        BPMNElementType.TASK.value,
        BPMNElementType.USER_TASK.value,
        BPMNElementType.SERVICE_TASK.value,
    ]:
        _validate_task(element)

    elif element["type"] == BPMNElementType.EXCLUSIVE_GATEWAY.value:
        _validate_exclusive_gateway(element)

    elif element["type"] == BPMNElementType.PARALLEL_GATEWAY.value:
        _validate_parallel_gateway(element)


def _validate_task(element: dict) -> None:
    if "label" not in element:
        raise ValueError(f"Task element is missing a label: {element}")

    try:
        BPMNTask.model_validate(element)
    except ValidationError:
        raise ValueError(f"Invalid task element: {element}")


def _validate_exclusive_gateway(element: dict) -> None:
    if "label" not in element:
        raise ValueError(f"Exclusive gateway is missing a label: {element}")
    if "branches" not in element or not isinstance(element["branches"], list):
        raise ValueError(
            f"Exclusive gateway is missing or has invalid 'branches': {element}"
        )
    for branch in element["branches"]:
        if "condition" not in branch or "path" not in branch:
            raise ValueError(f"Invalid branch in exclusive gateway: {branch}")

    try:
        ExclusiveGateway.model_validate(element)
    except ValidationError:
        raise ValueError(f"Invalid exclusive gateway element: {element}")


def _validate_parallel_gateway(element: dict) -> None:
    if "branches" not in element or not isinstance(element["branches"], list):
        raise ValueError(
            f"Parallel gateway has missing or invalid 'branches': {element}"
        )

    try:
        ParallelGateway.model_validate(element)
    except ValidationError:
        raise ValueError(f"Invalid parallel gateway element: {element}")
