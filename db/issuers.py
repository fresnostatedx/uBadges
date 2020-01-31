# Standard library
import uuid
from datetime import datetime
from typing import List

# Third party libraries
import boto3
from boto3.dynamodb.conditions import Key, Attr

# Package
from models.issuers import IssuerInCreate, IssuerInUpdate, IssuerInDB


class IssuersDB:

    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table("ubadges.issuers")


    async def get_all_issuers(self) -> List[IssuerInDB]:
        result = self.table.scan()
        issuers = result.get("Items", [])
        return list(map(lambda issuer: IssuerInDB(**issuer), issuers))


    async def get_issuer_by_id(self, issuer_id: str):
        result = self.table.get_item(Key={"id": issuer_id})
        issuer = result.get("Item")
        if issuer:
            return IssuerInDB(**issuer)
        return None


    async def get_issuer_by_name(self, name: str):
        result = self.table.scan(FilterExpression=Attr("name").eq(name))
        issuers = result.get("Items")
        if issuers:
            issuer = issuers[0]
            return IssuerInDB(**issuer)
        return None


    async def get_issuers_by_owner(self, owner_id: str):
        result = self.table.scan(FilterExpression=Attr("owner_id").eq(owner_id))
        issuers = result.get("Items")
        if issuers:
            return list(map(lambda issuer: IssuerInDB(**issuer), issuers))
        return []


    async def create_issuer(self, issuer: IssuerInCreate):
        if await self.get_issuer_by_name(issuer.name):
            raise Exception

        issuer_id = uuid.uuid4()
        key_dict = issuer.key.dict()
        key_dict["date_created"] = datetime.utcnow()

        self.table.put_item(
            Item={
                "id": issuer_id,
                "owner_id": issuer.owner_id,
                "name": issuer.name,
                "url": issuer.url,
                "email": issuer.email,
                "image": issuer.image,
                "keys": [key_dict],
                revocations: []
            }
        )

        return await self.get_issuer_by_id(issuer_id)


    async def update_issuer(self, issuer_id, updates: IssuerInUpdate):
        issuer = await self.get_issuer_by_id(issuer_id)

        if updates.name is not None:
            if issuer.name != updates.name and await self.get_issuer_by_name(name):
                raise Exception

        issuer_dict = issuer.dict()
        update_dict = updates.dict()

        for key, val in updates_dict.items():
            if val is not None and issuer_dict[key] != val:
                issuer_dict[key] = val

        result = self.table.update_item(
            Key={"id": issuer_id},
            UpdateExpression="SET #issuer_name = :n, url = :u, email = :e, image = :i, owner_id = :o, keys = :k",
            ExpressionAttributeNames={
                "#issuer_name": "name"
            },
            ExpressionAttributeValues={
                ":n": issuer_dict["name"],
                ":u": issuer_dict["url"],
                ":e": issuer_dict["email"],
                ":i": issuer_dict["image"],
                ":o": issuer_dict["owner_id"],
                ":k": issuer_dict["keys"]
            },
            ReturnValues="ALL_NEW"
        )

        return IssuerInDB(**result["Attributes"])
    

    async def delete_issuer(self, issuer_id):
        self.table.delete_item(Key={"id": issuer_id})