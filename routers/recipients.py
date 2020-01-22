from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def get_recipients():
    return [{"name": "recipient1"}, {"name": "recipient2"}]