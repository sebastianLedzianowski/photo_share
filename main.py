import redis.asyncio as redis
import uvicorn

from fastapi import FastAPI
from fastapi_limiter import FastAPILimiter


from src.routes import users, auth

import os
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

app.include_router(auth.router, prefix='/api')
app.include_router(users.router, prefix='/api')

@app.on_event("startup")
async def startup():
    """
    Function to initialize FastAPILimiter on application startup.
    """
    r = await redis.Redis(
        host=os.getenv('REDIS_HOST'),
        port=int(os.getenv('REDIS_PORT')),
        password=os.getenv('REDIS_PASSWORD'))
    await FastAPILimiter.init(r)


@app.get("/ping")
def root():
    return {"message": "pong"}


if __name__ == "__main__":
    uvicorn.run("app:app", reload=True)