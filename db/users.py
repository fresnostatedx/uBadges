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


    async def update_user(self, user_id, email: str = None, role: UserRole = None, password: str = None):
        user = await self.get_user_by_id(user_id)

        if email:
            if email != user.email and await self.get_user_by_email(email):
                raise Exception
            user.email = email

        if role:
            user.role = role

        if password:
            user.hashed_password = get_password_hash(password)

        response = self.table.update_item(
            Key={"id": user_id},
            UpdateExpression="SET email = :e, #user_role = :r, hashed_password = :p",
            ExpressionAttributeNames={
                "#user_role": "role"
            },
            ExpressionAttributeValues={
                ":e": user.email,
                ":r": user.role,
                ":p": user.hashed_password
            },
            ReturnValues="ALL_NEW"
        )

        return UserInDB(**response["Attributes"])
