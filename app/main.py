from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging

logger = logging.getLogger(__name__)

app = FastAPI(title="订单管理系统")

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"status": "ok", "message": "API is running"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

# 延迟导入路由，避免循环导入
from app.api.order import router as order_router
app.include_router(order_router, prefix="/api/order", tags=["orders"])

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {str(exc)}")
    return {
        "code": 0,
        "message": str(exc),
        "data": None
    } 