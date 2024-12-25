import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    logger.info("Initializing FastAPI application...")
    from app.main import app
    logger.info("FastAPI application initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize FastAPI application: {str(e)}")
    # 创建一个基础的 FastAPI 应用作为后备
    app = FastAPI()
    
    @app.get("/")
    async def fallback_root():
        return {
            "code": 0,
            "message": f"Application initialization failed: {str(e)}",
            "data": None
        }

# 处理 Vercel 的特殊路由
@app.middleware("http")
async def error_handling_middleware(request: Request, call_next):
    try:
        logger.info(f"Handling request to: {request.url.path}")
        response = await call_next(request)
        return response
    except Exception as e:
        logger.error(f"Error handling request: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "code": 0,
                "message": str(e),
                "data": None
            }
        )

# 导出 app 实例
app = app 