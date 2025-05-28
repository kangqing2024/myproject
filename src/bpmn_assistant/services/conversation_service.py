from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from bpmn_assistant.core.user_model import User, Conversation, Message

import logging

# 配置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def save_conversation(db: Session, user_id: int, messages: list, name: str = None):
    try:
        db.begin()  # 开始事务
        conversation = Conversation(user_id=user_id, name=name)
        db.add(conversation)
        db.flush()  # 刷新会话，获取新创建的对话 ID
        for message in messages:
            new_message = Message(
                conversation_id=conversation.id,
                role=message['role'],
                content=message['content']
            )
            db.add(new_message)
        db.commit()  # 提交事务
        logger.info(f"Conversation with user_id {user_id} saved successfully")
        return conversation
    except Exception as e:
        db.rollback()  # 回滚事务
        logger.error(f"Error saving conversation for user_id {user_id}: {str(e)}")
        raise e
    

def get_conversations(db: Session, user_id: int):
    conversations = db.query(Conversation).filter(Conversation.user_id == user_id).order_by(desc(Conversation.created_at)).all()
    result = []
    for conversation in conversations:
        result.append({
            'conversation_id': conversation.id,
            'created_at': conversation.created_at,
            'name': conversation.name
        })
    return result


def get_messages(db: Session, conversation_id: int):
    messages = db.query(Message).filter(Message.conversation_id == conversation_id).all()
    result = []
    for message in messages:
        result.append({
            'role': message.role,
            'content': message.content,
            'created_at': message.created_at
        })
    return result

