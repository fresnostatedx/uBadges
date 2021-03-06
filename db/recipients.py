# Standard library
import uuid
from datetime import datetime
from typing import List

# Third party libraries
import boto3
from boto3.dynamodb.conditions import Key, Attr

# Package
from models.recipients import RecipientIn, RecipientInDB


class RecipientsDB:

    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table("ubadges.recipients")

    
    async def get_all_recipients(self):
        result = self.table.scan()
        recipients = result.get("Items")
        return list(map(lambda r: RecipientInDB(**r), recipients))


    async def get_recipients_by_id(self, recipient_id):
        result = self.table.get_item(Key={"id": recipient_id})
        recipient = result.get("Item")
        if not recipient is None:
            return RecipientInDB(**recipient)
        return None


    async def get_recipient_by_email(self, email):
        result = self.table.scan(FilterExpression=Attr("email").eq(email))
        recipients = result.get("Items")
        if recipients:
            return RecipientInDB(**recipients[0])
        return None


    async def create_recipient(self, recipient: RecipientIn):
        recipient_in_db = RecipientInDB(
            id=str(uuid.uuid4()),
            name=recipient.name,
            email=recipient.email,
            certs=[],
            addresses={}
        )
        self.table.put_item(Item=recipient_in_db.dict())
        return recipient_in_db


    async def add_address(self, recipient_id: str, issuer_id: str, address: str):
        recipient = await self.get_recipients_by_id(recipient_id)
        recipient.addresses[issuer_id] = address
        self.table.update_item(
            Key={"id": recipient_id},
            UpdateExpression="SET addresses = :a",
            ExpressionAttributeValues={
                ":a": recipient.addresses
            }
        )
        return recipient


    async def add_cert(self, recipient_id, cert_id):
        recipient = await self.get_recipients_by_id(recipient_id)
        signed_cert_path = f"dx.ubadges.poc/certs/{cert_id}.json"
        cert_url = f"https://s3-us-west-2.amazonaws.com/{signed_cert_path}"
        recipient.certs.append(cert_url)
        self.table.update_item(
            Key={"id": recipient_id},
            UpdateExpression="SET certs = :c",
            ExpressionAttributeValues={
                ":c": recipient.certs
            }
        )
        return recipient
