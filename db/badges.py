# Standard library
import uuid
from datetime import datetime
from typing import List

# Third party libraries
import boto3
from boto3.dynamodb.conditions import Key, Attr

# Package
from models.badges import BadgeIn, BadgeInDB


class BadgesDB:

    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table("ubadges.badges")

    async def get_all_badges(self):
        result = self.table.scan()
        badges = result.get("Items")
        return list(map(lambda badge: BadgeInDB(**badge), badges))


    async def get_badge_by_id(self, badge_id: str, issuer_id: str):
        result = self.table.get_item(
            Key={'id': badge_id, 'issuer_id': issuer_id}
        )
        badge = result.get("Item")
        if not badge is None:
            return BadgeInDB(**badge)
        return None


    async def get_badge_by_name(self, name: str):
        result = self.table.scan(FilterExpression=Attr("name").eq(name))
        badges = result.get("Items")
        if badges:
            badge = badges[0]
            return BadgeInDB(**badge)
        return None


    async def get_badges_by_issuer_id(self, issuer_id: str):
        result = self.table.scan(FilterExpression=Attr("issuer_id").eq(issuer_id))
        badges = result.get("Items")
        return list(map(lambda badge: BadgeInDB(**badge), badges))   
    

    async def create_badge(self, badge: BadgeIn):
        badge_id = str(uuid.uuid4())
        badge_dict = badge.dict()
        badge_dict["id"] = badge_id
        self.table.put_item(Item=badge_dict)
        return await self.get_badge_by_id(badge_id, badge.issuer_id)


    async def update_badge(self):
        pass