from fastapi import FastAPI

from routers import users, issuers, recipients

app = FastAPI()

app.include_router(users.router, prefix="/users")
# app.include_router(issuers.router, prefix="/issuers")
# app.include_router(recipients.router, prefix="/recipients")