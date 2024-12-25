from datetime import datetime
import redis
import json
from typing import List, Dict
from app.core.config import settings
import time

class RedisService:
    def __init__(self):
        self.redis_client = None
        self.connect_redis()

    def connect_redis(self, max_retries=3):
        retry_count = 0
        while retry_count < max_retries:
            try:
                self.redis_client = redis.Redis(
                    host=settings.REDIS_HOST,
                    port=settings.REDIS_PORT,
                    db=settings.REDIS_DB,
                    decode_responses=True,
                    username=settings.REDIS_USERNAME,
                    password=settings.REDIS_PASSWORD,
                    socket_timeout=5,  # 添加超时设置
                    socket_connect_timeout=5
                )
                # 测试连接
                self.redis_client.ping()
                break
            except redis.ConnectionError as e:
                retry_count += 1
                if retry_count == max_retries:
                    raise Exception(f"Redis连接失败: {str(e)}")
                time.sleep(1)  # 等待1秒后重试

    def ensure_connection(self):
        try:
            self.redis_client.ping()
        except (redis.ConnectionError, AttributeError):
            self.connect_redis()
    
    def create_order(self, food_ids: List[int]) -> bool:
        self.ensure_connection()
        try:
            key = "order"
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            value = json.dumps(food_ids)
            return self.redis_client.hset(key, current_time, value)
        except Exception as e:
            raise Exception(f"创建订单失败: {str(e)}")
    
    def get_all_orders(self) -> List[dict]:
        self.ensure_connection()
        try:
            key = "order"
            all_orders = self.redis_client.hgetall(key)
            
            result = []
            for time_str, food_ids_json in all_orders.items():
                result.append({
                    "time": time_str,
                    "food_ids": json.loads(food_ids_json)
                })
                
            result.sort(key=lambda x: x["time"], reverse=True)
            return result
        except Exception as e:
            raise Exception(f"获取订单列表失败: {str(e)}")

redis_service = RedisService() 