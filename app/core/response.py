from typing import Generic, TypeVar, Optional, Any
from pydantic import BaseModel

T = TypeVar('T')

class ResponseModel(BaseModel, Generic[T]):
    code: int = 1
    message: str = ""
    data: Optional[T] = None

def success_response(data: Any = None) -> dict:
    return ResponseModel(code=1, message="操作成功", data=data).model_dump()

def error_response(message: str) -> dict:
    return ResponseModel(code=0, message=message).model_dump() 