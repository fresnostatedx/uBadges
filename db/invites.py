# Standard library
import uuid
import hashlib
import random
from datetime import datetime
from typing import List

# Third party libraries
import boto3
from boto3.dynamodb.conditions import Key, Attr

# Package
from models.invites import InviteInCreate, InviteInDB


def generate_nonce(length=6):
    """Generate pseudorandom number."""
    return ''.join([str(random.randint(0, 9)) for i in range(length)])


class InvitesDB:

    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table("ubadges.invites")


    async def get_by_id(self, invite_id: str):
        result = self.table.get_item(Key={"id": invite_id})
        invite = result.get("Item")
        if invite:
            return InviteInDB(**invite)
        return None


    async def get_by_none(self, nonce: str):
        result = self.table.scan(FilterExpression=Attr("nonce").eq(nonce))
        invites = result.get("Items")
        if invites:
            return InviteInDB(**invites[0])
        return None


    async def get_by_issuer_and_recipient_ids(self, issuer_id: str, recipient_id: str):
        result = self.table.scan(FilterExpression=Attr("issuer_id").eq(issuer_id)
            & Attr("recipient_id").eq(recipient_id)
        )
        invites = result.get("Items")
        if invites:
            return InviteInDB(**invites[0])
        return None


    async def create(self, invite: InviteInCreate):
        invite_in_db = InviteInDB(
            id=str(uuid.uuid4()),
            nonce=generate_nonce(),
            badges=[invite.badge_id],
            issuer_id=invite.issuer_id,
            recipient_id=invite.recipient_id
        )
        self.table.put_item(Item=invite_in_db.dict())
        return invite_in_db


    async def add_badge(self, invite_id: str, badge_id: str):
        invite = await self.get_by_id(invite_id)
        if badge_id not in invite.badges:
            invite.badges.append(badge_id)
        self.table.update_item(
            Key={"id": invite_id},
            UpdateExpression="SET badges = :b",
            ExpressionAttributeValues={
                ":b": invite.badges
            }
        )
        return invite


    async def delete(self, invite_id: str):
        self.table.delete_item(Key={"id": invite_id})
