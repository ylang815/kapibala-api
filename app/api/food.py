from fastapi import APIRouter
from pydantic import BaseModel
from app.services.food_wish_service import food_wish_service
from app.core.response import success_response, error_response

router = APIRouter()

class FoodWishCreate(BaseModel):
    food: str

@router.post("/wish-create")
async def create_food_wish(wish: FoodWishCreate):
    try:
        wish_info = food_wish_service.create_wish(wish.food)
        return success_response(wish_info)
    except Exception as e:
        return error_response(str(e))

@router.get("/wish-list")
async def get_food_wishes():
    try:
        wishes = food_wish_service.get_all_wishes()
        return success_response(wishes)
    except Exception as e:
        return error_response(str(e)) 