# Third party library imports
from fastapi import FastAPI

# Package imports
from routers import (
    auth,
    users,
    issuers,
    recipients
)

app = FastAPI()

app.include_router(auth.router, prefix="/auth")
app.include_router(users.router, prefix="/users")
app.include_router(issuers.router, prefix="/issuers")
# app.include_router(recipients.router, prefix="/recipients")