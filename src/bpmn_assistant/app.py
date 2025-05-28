from fastapi import FastAPI, Depends,Body, Request
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware  
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware
from .login_router import login_router, get_db  # 新增
from sqlalchemy.orm import Session
import logging
from fastapi import APIRouter, Depends, HTTPException
from .core.user_model import User, Conversation, Message

from bpmn_assistant.core.user_model import User
from bpmn_assistant.api.requests import (
    BpmnToJsonRequest,
    ConversationalRequest,
    DetermineIntentRequest,
    ModifyBpmnRequest,
)
from bpmn_assistant.core import handle_exceptions
from bpmn_assistant.core.enums import OutputMode
from bpmn_assistant.services import (
    BpmnJsonGenerator,
    BpmnModelingService,
    BpmnXmlGenerator,
    ConversationalService,
    determine_intent,
    save_conversation,
    get_conversations,
    get_messages,
)
from bpmn_assistant.utils import (
    replace_reasoning_model,
    get_available_providers,
    get_llm_facade,
)


# 配置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


app = FastAPI()
origins = ["http://localhost:8080"]  # 前端地址 

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

bpmn_modeling_service = BpmnModelingService()
bpmn_xml_generator = BpmnXmlGenerator()

# 挂载登录路由
app.include_router(login_router, prefix="/api")  # 新增


@app.post("/bpmn_to_json")
@handle_exceptions
async def _bpmn_to_json(request: BpmnToJsonRequest) -> JSONResponse:
    """
    Convert the BPMN XML to its JSON representation
    """
    bpmn_json_generator = BpmnJsonGenerator()
    result = bpmn_json_generator.create_bpmn_json(request.bpmn_xml)
    return JSONResponse(content=result)


@app.get("/available_providers")
@handle_exceptions
async def _available_providers() -> JSONResponse:
    """
    Get the available LLM providers
    """
    providers = get_available_providers()
    return JSONResponse(content=providers)


@app.post("/determine_intent")
@handle_exceptions
async def _determine_intent(request: DetermineIntentRequest) -> JSONResponse:
    """
    Determine the intent of the user query
    """
    model = replace_reasoning_model(request.model)
    llm_facade = get_llm_facade(model)
    intent = determine_intent(llm_facade, request.message_history)
    return JSONResponse(content=intent)


@app.post("/modify")
@handle_exceptions
async def _modify(request: ModifyBpmnRequest) -> JSONResponse:
    """
    Modify the BPMN process based on the user query. If the request does not contain a BPMN JSON,
    then create a new BPMN process. Otherwise, edit the existing BPMN process.
    """
    llm_facade = get_llm_facade(request.model)
    text_llm_facade = get_llm_facade(request.model, OutputMode.TEXT)

    if request.process:
        process = bpmn_modeling_service.edit_bpmn(
            llm_facade, text_llm_facade, request.process, request.message_history
        )
    else:
        process = bpmn_modeling_service.create_bpmn(
            llm_facade,
            request.message_history,
        )

    bpmn_xml_string = bpmn_xml_generator.create_bpmn_xml(process)
    return JSONResponse(content={"bpmn_xml": bpmn_xml_string, "bpmn_json": process})


@app.post("/talk")
async def _talk(request: ConversationalRequest) -> StreamingResponse:
    model = replace_reasoning_model(request.model)
    conversational_service = ConversationalService(model)

    if request.needs_to_be_final_comment:
        response_generator = conversational_service.make_final_comment(
            request.message_history, request.process
        )
    else:
        response_generator = conversational_service.respond_to_query(
            request.message_history, request.process
        )

    return StreamingResponse(response_generator)


@app.post("/save_conversation")
async def _save_conversation(payload: dict = Body(...), db: Session = Depends(get_db)):
    user_id = payload.get("user_id")
    messages = payload.get("messages")
    name = payload.get("name")
    
    logger.info(f"Received save conversation request with user_id: {user_id}, messages: {messages}, name: {name}")
    try:
        conversation = save_conversation(db, user_id, messages, name)
        logger.info("Conversation saved successfully")
        return {"message": "Conversation saved successfully", "conversation_id": conversation.id}
    except Exception as e:
        logger.error(f"Error saving conversation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error saving conversation: {str(e)}")




@app.get("/update_conversation_name")
async def _update_conversation_name_api(conversation_id: int, name: str, db: Session = Depends(get_db)):
    try:
        conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if conversation:
            conversation.name = name
            db.commit()
            return {"message": "Conversation name updated successfully"}
        else:
            return {"message": "Conversation not found"}
    except Exception as e:
        logger.error(f"Error updating conversation name: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating conversation name: {str(e)}")
    

@app.get("/get_conversations")
def _get_conversations(user_id: int, db: Session = Depends(get_db)):
    return get_conversations(db, user_id)

@app.get("/get_messages")
def _get_messages(conversation_id: int, db: Session = Depends(get_db)):
    return get_messages(db, conversation_id)

@app.post("/save_messages")
async def _save_messages(payload: dict = Body(...), db: Session = Depends(get_db)):
    conversation_id = payload.get("conversation_id")
    messages = payload.get("messages")
    role = payload.get("role")
    
    logger.info(f"Received save messages request with conversation_id: {conversation_id}, messages: {messages}, role: {role}")
    try:
        for message in messages:
            message_item = Message(conversation_id=conversation_id, role=role, content=message)
            db.add(message_item)
        db.commit()
        logger.info("Messages saved successfully")
        return {"message": "Messages saved successfully"}
    except Exception as e:
        logger.error(f"Error saving messages: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error saving messages: {str(e)}")

@app.post("/generate_conversation_name")
async def generate_conversation_name_api(
    payload: dict,
    db: Session = Depends(get_db)
):
    try:
        message_history = payload.get('message_history', [])
        process = payload.get('process', None)
        model = payload.get('model', '')

        # 初始化对话服务
        conversational_service = ConversationalService(model)

        # 调用生成对话名称的方法
        conversation_name = conversational_service.generate_conversation_name(message_history, process)

        return {"conversation_name": conversation_name}
    except Exception as e:
        logger.error(f"Error generating conversation name: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating conversation name: {str(e)}")
    
@app.delete("/delete_conversation")
async def delete_conversation(conversation_id: int, db: Session = Depends(get_db)):
    try:
        # 删除与该对话关联的消息
        db.query(Message).filter(Message.conversation_id == conversation_id).delete()
        # 删除对话
        conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        db.delete(conversation)
        db.commit()
        logger.info(f"Conversation with id {conversation_id} deleted successfully")
        return {"message": "Conversation deleted successfully"}
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting conversation with id {conversation_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting conversation: {str(e)}")