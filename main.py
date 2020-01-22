from fastapi import FastAPI
from pydantic import BaseModel

from routers import users, issuers, recipients


app = FastAPI()

@app.get("/")
async def index():
    return {"Hello": "World"}


app.include_router(users.router, prefix="/users")
app.include_router(issuers.router, prefix="/issuers")
app.include_router(recipients.router, prefix="/recipients")