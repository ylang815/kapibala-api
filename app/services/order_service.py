from typing import List, Dict
from app.services.base_redis_service import BaseRedisService

class OrderService(BaseRedisService):
    ORDER_KEY = "orders"
    ORDER_SEQUENCE_KEY = "order_sequence"
    ORDER_PREFIX = "kpbl"
    
    def generate_order_number(self) -> str:
        """生成8位订单号，格式：kpbl + 4位数字"""
        try:
            sequence = self.redis_client.incr(self.ORDER_SEQUENCE_KEY)
            sequence = sequence % 10000
            number_part = f"{sequence:04d}"
            return f"{self.ORDER_PREFIX}{number_part}"
        except Exception as e:
            raise Exception(f"生成订单号失败: {str(e)}")
    
    def create_order(self, food_ids: List[int]) -> dict:
        """创建订单"""
        order_data = {
            "order_number": self.generate_order_number(),
            "time": self.get_current_time(),
            "food_ids": food_ids
        }
        self.add_to_sorted_set(self.ORDER_KEY, order_data)
        return order_data
    
    def get_all_orders(self) -> List[dict]:
        """获取所有订单"""
        return self.get_all_from_sorted_set(self.ORDER_KEY)
    
    def clear_orders(self) -> bool:
        """清除所有订单"""
        self.clear_key(self.ORDER_KEY)
        self.clear_key(self.ORDER_SEQUENCE_KEY)
        return True

order_service = OrderService() 