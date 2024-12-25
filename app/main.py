from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.api.order import router as order_router
from app.core.response import error_response

app = FastAPI(title="订单管理系统")

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return error_response(str(exc))

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return error_response("请求参数验证失败：" + str(exc))

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        return error_response("接口不存在")
    return error_response(str(exc.detail))

# 添加健康检查接口
@app.get("/health")
async def health_check():
    return {"status": "ok"}

app.include_router(order_router, prefix="/api/order", tags=["orders"]) 