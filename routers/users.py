from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def get_users():
    return [{"username": "user1"}, {"username": "user2"}, {"username": "user3"}]