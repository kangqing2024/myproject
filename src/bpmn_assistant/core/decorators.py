from functools import wraps
from typing import Callable

from fastapi import HTTPException

from bpmn_assistant.config import logger


def handle_exceptions(func: Callable):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error: {str(e)}", exc_info=e)
            raise HTTPException(status_code=500, detail=str(e))

    return wrapper
