from datetime import datetime
import redis
import json
from typing import List, Dict, Any
from app.core.config import settings
import time
import logging
import pytz

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseRedisService:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.redis_client = None
            self._initialized = True
            self.timezone = pytz.timezone('Asia/Shanghai')
    
    def _ensure_initialized(self):
        if self.redis_client is None:
            self.connect_redis()

    def connect_redis(self, max_retries=3):
        retry_count = 0
        while retry_count < max_retries:
            try:
                logger.info(f"Attempting to connect to Redis: {settings.REDIS_HOST}:{settings.REDIS_PORT}")
                redis_params = {
                    "host": settings.REDIS_HOST,
                    "port": settings.REDIS_PORT,
                    "db": settings.REDIS_DB,
                    "decode_responses": True,
                    "socket_timeout": 10,
                    "socket_connect_timeout": 10
                }
                
                if settings.REDIS_PASSWORD:
                    redis_params["password"] = settings.REDIS_PASSWORD
                if settings.REDIS_USERNAME:
                    redis_params["username"] = settings.REDIS_USERNAME

                self.redis_client = redis.Redis(**redis_params)
                self.redis_client.ping()
                logger.info("Successfully connected to Redis")
                break
            except redis.ConnectionError as e:
                retry_count += 1
                logger.error(f"Redis connection attempt {retry_count} failed - Error: {str(e)}")
                if retry_count == max_retries:
                    raise Exception(f"Redis连接失败: {str(e)}")
                time.sleep(1)

    def get_current_time(self) -> str:
        """获取上海时区的当前时间"""
        return datetime.now(self.timezone).strftime("%Y-%m-%d %H:%M:%S")

    def add_to_sorted_set(self, key: str, data: dict) -> bool:
        """添加数据到有序集合"""
        self._ensure_initialized()
        try:
            current_time = self.get_current_time()
            data['time'] = current_time
            timestamp = datetime.strptime(current_time, "%Y-%m-%d %H:%M:%S").timestamp()
            return self.redis_client.zadd(key, {json.dumps(data): timestamp})
        except Exception as e:
            raise Exception(f"添加数据失败: {str(e)}")

    def get_all_from_sorted_set(self, key: str) -> List[dict]:
        """从有序集合中获取所有数据"""
        self._ensure_initialized()
        try:
            data = self.redis_client.zrevrange(key, 0, -1, withscores=False)
            result = []
            for item_json in data:
                try:
                    item = json.loads(item_json)
                    result.append(item)
                except json.JSONDecodeError as e:
                    logger.error(f"解析数据失败: {str(e)}")
                    continue
            return result
        except Exception as e:
            raise Exception(f"获取数据失败: {str(e)}")

    def clear_key(self, key: str) -> bool:
        """清除指定key的数据"""
        self._ensure_initialized()
        try:
            return bool(self.redis_client.delete(key))
        except Exception as e:
            raise Exception(f"清除数据失败: {str(e)}") 