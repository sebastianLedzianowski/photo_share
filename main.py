import redis.asyncio as redis
import uvicorn

from fastapi import FastAPI
from fastapi_limiter import FastAPILimiter


from src.routes import users, auth

from src.secrets_manager import get_secret

app = FastAPI()

app.include_router(auth.router, prefix='/api')
app.include_router(users.router, prefix='/api')

REDIS_HOST, REDIS_PORT, REDIS_PASSWORD = get_secret()

@app.on_event("startup")
async def startup():
    """
    Function to initialize FastAPILimiter on application startup.
    """
    r = await redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        password=REDIS_PASSWORD,
        encoding="utf-8",
        decode_responses=True
    )
    await FastAPILimiter.init(r)


@app.get("/ping")
def root():
    return {"message": "pong"}


if __name__ == "__main__":
    uvicorn.run("app:app", reload=True)