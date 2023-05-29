import asyncio
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
import uvicorn
import redis.asyncio as redis
from fastapi_limiter import FastAPILimiter

from src.routes import contacts, auth, users

app = FastAPI(title='Contacts')

app.include_router(contacts.router)
app.include_router(auth.router)
app.include_router(users.router, prefix='/api')

origins = [ 
    "http://localhost:8000",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    r = await redis.Redis(host='localhost', port=6379, db=0)
    await FastAPILimiter.init(r)
    
    
@app.get('/')
async def root():
    return {'message': 'Contacts'}
    
async def start_app():
    config = uvicorn.Config("main:app", port=8000, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    asyncio.run(start_app())
    
