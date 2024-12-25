from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.main import app

# 处理 Vercel 的特殊路由
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except Exception as e:
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