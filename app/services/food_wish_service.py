from typing import List, Dict
import random

from app.core.decorators import async_mail_notify
from app.services.base_redis_service import BaseRedisService

class FoodWishService(BaseRedisService):
    FOOD_WISH_KEY = "food_wish"

    @async_mail_notify(
        subject="开小灶加菜",
        body="报！！！卡皮巴拉需要开小灶投喂: {result}"
    )
    def create_wish(self, food: str) -> dict:
        replys = ["收到，饲养员已就位", "好嘞~我看看怎么搞", "尽快安排投喂哈", "这个有点难哟，需要鼓励下(疯狂暗示)...",
                  "passion", "🎵缓缓飘落的枫叶像思念...🎵", "四方食事，不过一碗人间烟火", "打个酱油..."]

        """创建食品愿望"""
        wish_data = {
            "food": food,
            "is_up": 0,
            "reply": random.choice(replys)
        }
        self.add_to_sorted_set(self.FOOD_WISH_KEY, wish_data)
        return wish_data
    
    def get_all_wishes(self) -> List[dict]:
        """获取所有食品愿望"""
        return self.get_all_from_sorted_set(self.FOOD_WISH_KEY)

food_wish_service = FoodWishService() 