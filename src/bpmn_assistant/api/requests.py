from typing import Any

from pydantic import BaseModel, model_validator

from bpmn_assistant.core import MessageItem

class MessageItem(BaseModel):
    content: str
    role: str

class BpmnToJsonRequest(BaseModel):
    bpmn_xml: str  # The BPMN XML to be converted to JSON


class DetermineIntentRequest(BaseModel):
    message_history: list[MessageItem]  # The message history
    model: str  # The model to be used


class ModifyBpmnRequest(BaseModel):
    message_history: list[MessageItem]  # The message history
    process: list[dict[str, any]] | None  # The process to be updated (if it exists)
    model: str  # The model to be used

    @model_validator(mode="before")
    @classmethod
    def ensure_data_validity(cls, data: dict[str, any]) -> dict[str, any]:
        # 可以在这里添加更多的数据验证逻辑
        if not isinstance(data.get("message_history"), list):
            raise ValueError("message_history must be a list")
        for message in data.get("message_history", []):
            if not isinstance(message, dict) or 'content' not in message or 'role' not in message:
                raise ValueError("Each message in message_history must have 'content' and 'role' fields")
        if data.get("process") and not isinstance(data.get("process"), list):
            raise ValueError("process must be a list")
        if not isinstance(data.get("model"), str):
            raise ValueError("model must be a string")
        return data


class ConversationalRequest(BaseModel):
    message_history: list[MessageItem]  # The message history
    process: list[dict[str, Any]] | None  # The current process (if it exists)
    model: str  # The model to be used
    needs_to_be_final_comment: bool  # Whether the response needs to be a comment after the process is created/edited

    @model_validator(mode="before")
    @classmethod
    def ensure_bpmn_json_presence(cls, data: dict[str, Any]) -> dict[str, Any]:
        if data.get("needs_to_be_final_comment") and not data.get("process"):
            raise ValueError(
                "Process must be present when needs_to_be_final_comment is True"
            )
        return data

class PhoneLoginRequest(BaseModel):
    phone_number: str
    password: str

# 重置密码请求模型
class ResetPasswordRequest(BaseModel):
    email: str
    token: str
    new_password: str



class PhoneRegisterRequest(BaseModel):
    username: str
    password: str
    phone_number: str
    verification_code: str