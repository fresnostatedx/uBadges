# Third party library imports
from fastapi import FastAPI
from starlette.requests import Request
from starlette.staticfiles import StaticFiles

# Package imports
from routers import (
    auth,
    users,
    issuers,
    recipients
)

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth.router, prefix="/auth")
app.include_router(users.router, prefix="/users")
app.include_router(issuers.router, prefix="/issuers")
app.include_router(recipients.router, prefix="/recipients")