from datetime import datetime
import redis
import json
from typing import List, Dict
from app.core.config import settings
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RedisService:
    def __init__(self):
        self.redis_client = None
        self.connect_redis()

    def connect_redis(self, max_retries=3):
        retry_count = 0
        while retry_count < max_retries:
            try:
                logger.info(f"Attempting to connect to Redis: {settings.REDIS_HOST}:{settings.REDIS_PORT}")
                
                # 如果没有设置密码，则不传入密码参数
                redis_params = {
                    "host": settings.REDIS_HOST,
                    "port": settings.REDIS_PORT,
                    "db": settings.REDIS_DB,
                    "decode_responses": True,
                    "socket_timeout": 5,
                    "socket_connect_timeout": 5
                }
                
                if settings.REDIS_PASSWORD:
                    redis_params["password"] = settings.REDIS_PASSWORD
                if settings.REDIS_USERNAME:
                    redis_params["username"] = settings.REDIS_USERNAME

                self.redis_client = redis.Redis(**redis_params)
                
                # 测试连接
                self.redis_client.ping()
                logger.info("Successfully connected to Redis")
                break
            except redis.ConnectionError as e:
                retry_count += 1
                logger.error(f"Redis connection attempt {retry_count} failed: {str(e)}")
                if retry_count == max_retries:
                    logger.error("All Redis connection attempts failed")
                    raise Exception(f"Redis连接失败: {str(e)}")
                time.sleep(1)

    def ensure_connection(self):
        try:
            self.redis_client.ping()
        except Exception as e:
            logger.warning(f"Redis connection lost, attempting to reconnect: {str(e)}")
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