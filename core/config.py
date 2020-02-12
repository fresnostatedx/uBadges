from starlette.config import Config
from starlette.datastructures import Secret

config = Config(".env")

SECRET_KEY = config("SECRET_KEY", cast=Secret)
ALGORITHM = config("ALGORITHM", cast=str)
ACCESS_TOKEN_EXPIRE_MINUTES = config("ACCESS_TOKEN_EXPIRE_MINUTES", cast=int)
API_URL = config("API_URL", cast=str)