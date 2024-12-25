from datetime import datetime
import redis
import json
from typing import List, Dict
from app.core.config import settings
import time
import logging
import pytz

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RedisService:
    _instance = None
    ORDER_KEY = "orders"  # sorted set key for orders
    ORDER_SEQUENCE_KEY = "order_sequence"  # key for order number sequence
    ORDER_PREFIX = "kpbl"
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.redis_client = None
            self._initialized = True
            # 设置上海时区
            self.timezone = pytz.timezone('Asia/Shanghai')
    
    def _ensure_initialized(self):
        if self.redis_client is None:
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
                logger.error(f"Redis connection attempt {retry_count} failed for host {settings.REDIS_HOST}:{settings.REDIS_PORT} - Error: {str(e)}")
                if retry_count == max_retries:
                    logger.error(f"All Redis connection attempts failed for host {settings.REDIS_HOST}:{settings.REDIS_PORT}")
                    raise Exception(f"Redis连接失败 (host: {settings.REDIS_HOST}:{settings.REDIS_PORT}): {str(e)}")
                time.sleep(1)

    def ensure_connection(self):
        try:
            self.redis_client.ping()
        except Exception as e:
            logger.warning(f"Redis connection lost, attempting to reconnect: {str(e)}")
            self.connect_redis()
    
    def generate_order_number(self) -> str:
        """生成8位订单号，格式：kpbl + 4位数字"""
        try:
            # 获取并递增序列号
            sequence = self.redis_client.incr(self.ORDER_SEQUENCE_KEY)
            # 确保序列号不超过9999
            sequence = sequence % 10000
            # 格式化为4位数字，不足前面补0
            number_part = f"{sequence:04d}"
            return f"{self.ORDER_PREFIX}{number_part}"
        except Exception as e:
            raise Exception(f"生成订单号失败: {str(e)}")
    
    def get_current_time(self) -> str:
        """获取上海时区的当前时间"""
        return datetime.now(self.timezone).strftime("%Y-%m-%d %H:%M:%S")
    
    def create_order(self, food_ids: List[int]) -> dict:
        """创建订单，返回订单信息"""
        self._ensure_initialized()
        try:
            # 生成订单号
            order_number = self.generate_order_number()
            current_time = self.get_current_time()
            
            # 构建订单数据
            order_data = {
                "order_number": order_number,
                "time": current_time,
                "food_ids": food_ids
            }
            
            # 将订单数据存入Redis有序集合
            # 使用时间戳作为score以便按时间排序
            timestamp = datetime.strptime(current_time, "%Y-%m-%d %H:%M:%S").timestamp()
            self.redis_client.zadd(
                self.ORDER_KEY,
                {json.dumps(order_data): timestamp}
            )
            
            return order_data
        except Exception as e:
            raise Exception(f"创建订单失败: {str(e)}")
    
    def get_all_orders(self) -> List[dict]:
        """获取所有订单"""
        self._ensure_initialized()
        try:
            # 从有序集合中获取所有订单，按分数倒序（最新的订单在前）
            orders_data = self.redis_client.zrevrange(
                self.ORDER_KEY,
                0,
                -1,
                withscores=False
            )
            
            result = []
            for order_json in orders_data:
                try:
                    order = json.loads(order_json)
                    result.append(order)
                except json.JSONDecodeError as e:
                    logger.error(f"解析订单数据失败: {str(e)}")
                    continue
            
            # 直接返回订单数组
            return result
        except Exception as e:
            raise Exception(f"获取订单列表失败: {str(e)}")
    
    def clear_orders(self) -> bool:
        """清除所有订单数据"""
        self._ensure_initialized()
        try:
            # 删除订单数据
            self.redis_client.delete(self.ORDER_KEY)
            # 重置订单序号
            self.redis_client.delete(self.ORDER_SEQUENCE_KEY)
            return True
        except Exception as e:
            raise Exception(f"清除订单失败: {str(e)}")

redis_service = RedisService() 