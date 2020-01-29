# Standard library imports
import uuid

# Third party library imports
import boto3
from boto3.dynamodb.conditions import Key, Attr

# Package imports
from models.users import UserRole, UserInDB
from services.security import get_password_hash


class UsersDB:

    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table("ubadges.users")


    async def get_all_users(self):
        result = self.table.scan()
        users = result["Items"]
        return list(map(lambda user: UserInDB(**user), users))


    async def get_user_by_id(self, user_id: str):
        result = self.table.get_item(Key={"id": user_id})
        user = result.get("Item", None)
        if user:
            return UserInDB(**user) 
        return None


    async def get_user_by_email(self, email: str):
        result = self.table.query(
            IndexName="email-index",
            KeyConditionExpression=Key("email").eq(email)
        )
        users = result.get("Items")
        if users:
            return await self.get_user_by_id(users[0]["id"])
        return None


    async def get_users_by_role(self, role: UserRole):
        result = self.table.scan(FilterExpression=Attr('role').eq(role))
        users = result["Items"]
        return list(map(lambda user: UserInDB(**user), users))


    async def create_user(self, email: str, password: str, role: UserRole):
        user = UserInDB(
            id=str(uuid.uuid4()),
            email=email,
            hashed_password=get_password_hash(password),
            role=role
        )
        self.table.put_item(Item=user.dict())
        return user


    async def update_user(self):
        pass


    async def delete_user(self):
        pass