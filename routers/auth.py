# Third party library imports
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from starlette.status import HTTP_401_UNAUTHORIZED

# Package imports
from services.auth import authenticate_user
from services.jwt import create_access_token
from models.jwt import JWTPayload
from models.tokens import Token


router = APIRouter()


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    payload = JWTPayload(sub=user.email)
    access_token = create_access_token(payload=payload)
    return Token(access_token=access_token, token_type="bearer")
