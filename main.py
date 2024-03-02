import redis.asyncio as redis
import uvicorn
from fastapi import FastAPI
from fastapi_limiter import FastAPILimiter
from src.routes import users, auth, messages, tags, pictures_oktawian, search
from src.services.secrets_manager import get_secret
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Define allowed origins for CORS (Cross-Origin Resource Sharing)
origins = [
    "http://localhost:8000"
    ]

# Add CORS middleware to allow requests from the defined origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the routers for the different routes
app.include_router(auth.router, prefix='/api')
app.include_router(users.router, prefix='/api')
app.include_router(messages.router, prefix='/api')
app.include_router(search.router, prefix='/api')
app.include_router(pictures_oktawian.router, prefix='/api')
app.include_router(tags.router, prefix='/api')

# Get the Redis connection details from the secrets manager
REDIS_HOST = get_secret("REDIS_HOST")
REDIS_PORT = get_secret("REDIS_PORT")
REDIS_PASSWORD = get_secret("REDIS_PASSWORD")

# Initialize FastAPILimiter on application startup
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

# Add a simple ping endpoint
@app.get("/ping")
def root():
    return {"message": "pong"}

# Run the application using uvicorn
if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)