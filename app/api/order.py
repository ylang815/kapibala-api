from fastapi import APIRouter, HTTPException
from typing import List
from pydantic import BaseModel
from app.services.redis_service import redis_service
from app.core.response import success_response, error_response

router = APIRouter()

class OrderCreate(BaseModel):
    food_ids: List[int]

@router.post("/create")
async def create_order(order: OrderCreate):
    try:
        redis_service.create_order(order.food_ids)
        return success_response({})
    except Exception as e:
        return error_response(str(e))

@router.get("/list")
async def get_orders():
    try:
        orders = redis_service.get_all_orders()
        return success_response(orders)
    except Exception as e:
        return error_response(str(e)) 