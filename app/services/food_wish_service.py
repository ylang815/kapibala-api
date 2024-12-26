from typing import List, Dict
from app.services.base_redis_service import BaseRedisService

class FoodWishService(BaseRedisService):
    FOOD_WISH_KEY = "food_wish"
    
    def create_wish(self, food: str) -> dict:
        """创建食品愿望"""
        wish_data = {
            "food": food,
            "is_up": 0,
            "reply": ""
        }
        self.add_to_sorted_set(self.FOOD_WISH_KEY, wish_data)
        return wish_data
    
    def get_all_wishes(self) -> List[dict]:
        """获取所有食品愿望"""
        return self.get_all_from_sorted_set(self.FOOD_WISH_KEY)

food_wish_service = FoodWishService() 