# Standard library
import uuid
from datetime import datetime
from typing import List

# Third party libraries
import boto3
from boto3.dynamodb.conditions import Key, Attr

# Package
from models.issuers import IssuerIn, IssuerInDB
from models.keys import KeyInDB


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


    async def create_issuer(self, issuer: IssuerIn):
        # Not checking that issuer name is not already taken in DB.
        # This should be used in the client that uses this function.
        issuer_id = str(uuid.uuid4())
        key_dict = issuer.key.dict()
        key_dict["date_created"] = str(datetime.utcnow())

        self.table.put_item(
            Item={
                "id": issuer_id,
                "owner_id": issuer.owner_id,
                "name": issuer.name,
                "url": issuer.url,
                "email": issuer.email,
                "image": issuer.image,
                "keys": [key_dict],
                "revocations": []
            }
        )
        return await self.get_issuer_by_id(issuer_id)


    async def update_issuer(self, issuer_id, issuer: IssuerIn):
        # Not checking that issuer_id exists or that new issuer name
        # isn't already taken in the DB. This should be handled in the client.
        # issuer_in_db = await self.get_issuer_by_id(issuer_id)
        # keys = issuer_in_db.keys
        # for key in keys:
        #     if not key.date_revoked:
        #         key.date_revoked = datetime.utcnow()
        # keys.append(
        #     KeyInDB(**issuer.key.dict(), date_created=datetime.utcnow())
        # )
        
        # keys = list(map(lambda k: k.dict(), keys))
        # for k in keys:
        #     k["date_created"] = str(k["date_created"])
        #     k["date_revoked"] = str(k["date_revoked"])
 
        # result = self.table.update_item(
        #     Key={"id": issuer_id},
        #     UpdateExpression="SET #issuer_name = :n, #issuer_url = :u, email = :e, image = :i, owner_id = :o, #issuer_keys = :k",
        #     ExpressionAttributeNames={
        #         "#issuer_name": "name",
        #         "#issuer_url": "url",
        #         "#issuer_keys": "keys"
        #     },
        #     ExpressionAttributeValues={
        #         ":n": issuer.name, 
        #         ":u": issuer.url,
        #         ":e": issuer.email, 
        #         ":i": issuer.image,
        #         ":o": issuer.owner_id,
        #         ":k": keys
        #     },
        #     ReturnValues="ALL_NEW"
        # )
        # return IssuerInDB(**result["Attributes"])
        pass
    

    async def delete_issuer(self, issuer_id):
        self.table.delete_item(Key={"id": issuer_id})