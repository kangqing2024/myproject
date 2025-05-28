import json
from typing import Any, Generator

from pydantic import BaseModel

from bpmn_assistant.config import logger
from bpmn_assistant.core.enums import MessageRole, OutputMode, Provider
from bpmn_assistant.core.llm_provider import LLMProvider
from bpmn_assistant.core.provider_factory import ProviderFactory


class LLMFacade:
    def __init__(
        self,
        provider: Provider,
        api_key: str,
        model: str,
        output_mode: OutputMode = OutputMode.JSON,
    ):
        self.provider: LLMProvider = ProviderFactory.get_provider(
            provider, api_key, output_mode
        )
        self.model = model
        self.output_mode = output_mode

        if not self.provider.check_model_compatibility(self.model):
            raise ValueError(f"Unsupported model for provider {provider}: {self.model}")

        self.messages = self.provider.get_initial_messages()

    def call(
        self,
        prompt: str,
        max_tokens: int = 999999,
        temperature: float = 0.3,
        structured_output: BaseModel | None = None,
    ) -> str | dict[str, Any]:
        logger.info(f"Calling LLM: {self.model}")
        response = self.provider.call(
            self.model,
            prompt,
            self.messages,
            max_tokens,
            temperature,
            structured_output,
        )
        if self.output_mode == OutputMode.JSON:
            self.provider.add_message(
                self.messages, MessageRole.ASSISTANT, json.dumps(response)
            )
        return response

    def stream(
        self, prompt: str, max_tokens: int = 999999, temperature: float = 0.3
    ) -> Generator[str, None, None]:
        logger.info(f"Calling LLM (streaming): {self.model}")
        return self.provider.stream(
            self.model, prompt, self.messages, max_tokens, temperature
        )

