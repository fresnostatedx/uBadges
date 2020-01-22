from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def get_issuers():
    return [{"name": "issuer1"}, {"name": "issuer2"}, {"name": "issuer3"}]