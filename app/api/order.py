from fastapi import APIRouter, HTTPException
from typing import List
from pydantic import BaseModel
from app.services.order_service import order_service
from app.core.response import success_response, error_response

router = APIRouter()

class OrderCreate(BaseModel):
    food_ids: List[int]

@router.post("/create")
async def create_order(order: OrderCreate):
    try:
        order_info = order_service.create_order(order.food_ids)
        return success_response(order_info)
    except Exception as e:
        return error_response(str(e))

@router.get("/list")
async def get_orders():
    try:
        orders = order_service.get_all_orders()
        return success_response(orders)
    except Exception as e:
        return error_response(str(e))

@router.get("/clear")
async def clear_orders():
    try:
        order_service.clear_orders()
        return success_response({"message": "所有订单已清除"})
    except Exception as e:
        return error_response(str(e)) 