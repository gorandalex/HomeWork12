import asyncio
from fastapi import FastAPI
import uvicorn

from src.routes import contacts, auth

app = FastAPI(title='Contacts')

app.include_router(contacts.router)
app.include_router(auth.router)


@app.get('/')
async def root():
    return {'message': 'Contacts'}
    
async def start_app():
    config = uvicorn.Config("main:app", port=8000, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    asyncio.run(start_app())
    
