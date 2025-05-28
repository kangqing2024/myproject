import json
import traceback

from bpmn_assistant.config import logger
from bpmn_assistant.core import LLMFacade, MessageItem
from bpmn_assistant.prompts import PromptTemplateProcessor
from bpmn_assistant.services.process_editing import (
    BpmnEditingService,
    define_change_request,
)
from bpmn_assistant.utils import message_history_to_string

from .validate_bpmn import validate_bpmn


class BpmnModelingService:
    """
    Service for creating and editing BPMN processes.
    """

    def __init__(self):
        self.prompt_processor = PromptTemplateProcessor()

    def create_bpmn(
        self,
        llm_facade: LLMFacade,
        message_history: list[MessageItem],
        max_retries: int = 3,
    ) -> list:
        """
        Create a BPMN process.
        Args:
            llm_facade: The LLMFacade object.
            message_history: The message history.
            max_retries: The maximum number of retries in case of failure.
        Returns:
            list: The BPMN process.
        """
        logger.info('Starting to create BPMN process. Message history: %s', message_history)
        prompt = self.prompt_processor.render_template(
            "create_bpmn.jinja2",
            message_history=message_history_to_string(message_history),
        )

        attempts = 0

        while attempts < max_retries:
            attempts += 1
            try:
                logger.info('Making LLM call (attempt %d) with prompt: %s', attempts, prompt)
                response = llm_facade.call(prompt)
                logger.info('LLM response: %s', response)
                process = response["process"]
                validate_bpmn(process)
                logger.debug(
                    f"Generated BPMN process:\n{json.dumps(process, indent=2)}"
                )
                return process  # Return the process if it's valid
            except (ValueError, Exception) as e:
                logger.warning(
                    f"Error (attempt {attempts}): {str(e)}\n"
                    f"Traceback: {traceback.format_exc()}"
                )
                prompt = f"Error: {str(e)}. Try again."

        raise Exception(
            "Max number of retries reached. Could not create the BPMN process."
        )

    def edit_bpmn(
        self,
        llm_facade: LLMFacade,
        text_llm_facade: LLMFacade,
        process: list[dict],
        message_history: list[MessageItem],
    ) -> list:
        logger.info('Starting to edit BPMN process. Process: %s, Message history: %s', process, message_history)
        change_request = define_change_request(
            text_llm_facade, process, message_history
        )

        bpmn_editor_service = BpmnEditingService(llm_facade, process, change_request)

        result = bpmn_editor_service.edit_bpmn()
        logger.info('Edited BPMN process: %s', result)
        return result
