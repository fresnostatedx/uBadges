import os
import datetime
import uuid
import json
from io import BytesIO

# Third party imports
import boto3
import pytz
from pytz import timezone
# from flask import render_template

# Package imports
from models.recipients import RecipientInDB
from models.badges import BadgeInDB
from models.issuers import IssuerInDB
from db.recipients import RecipientsDB


bucket = boto3.resource('s3').Bucket('dx.ubadges.poc')


def generate_unsigned_cert(issuer: IssuerInDB, recipient: RecipientInDB, badge: BadgeInDB):
    unsigned_cert_id = str(uuid.uuid4())
    issuer_public_key = [key for key in issuer.keys if key.date_revoked is None][0]
    recipient_address = recipient.addresses[issuer.id]

    # Get date in pacific time
    date = datetime.datetime.now(tz=pytz.utc)
    date = date.astimezone(timezone('US/Pacific'))

    display_html = ""
    # display_html = render_template('cert/template_{}.html'.format(badge['template']),
    #     issuerID=issuer['id'], 
    #     recipientName=recipient['name'],
    #     description=badge['description'],
    #     badgeImage=badge['image'],
    #     badgeName=badge['name'],
    #     date=str(date),
    #     signature=badge['signatureLines'][0]['image'],
    #     template=badge['template'])
    
    unsigned_cert = ""
    # unsigned_cert = render_template('cert/unsigned_cert.json',
    #     date=date.isoformat(),
    #     issuer_public_key=str(issuer_public_key),
    #     issuer_url=issuer['url'],
    #     issuer_name=issuer['name'],
    #     issuer_email=issuer['email'],
    #     issuer_path='{}/issuers/{}'.format(os.getenv('API_URL'), issuer['id']),
    #     issuer_image=issuer['image'],
    #     issuer_revocations_path='{}/issuers/{}/revocations'.format(os.getenv('API_URL'), issuer['id']),
    #     badge_name=badge['name'],
    #     badge_narrative=badge['criteria']['narrative'],
    #     badge_image=badge['image'],
    #     badge_urn='urn:uuid:{}'.format(badge['id']),
    #     badge_description=badge['description'],
    #     badge_signature_lines=badge['signatureLines'],
    #     cert_urn='urn:uuid:{}'.format(unsigned_cert_id),
    #     recipient_name=recipient['name'],
    #     recipient_email=recipient['email'],
    #     recipient_public_key='ecdsa-koblitz-pubkey:{}'.format(recipient['addresses'][issuer['id']]),
    #     display_html=display_html)
        
    return unsigned_cert_id, unsigned_cert
        

def upload_unsigned_cert(issuer_id, unsigned_cert_id, unsigned_cert):
    date        = datetime.datetime.now(tz=pytz.utc)
    date        = date.astimezone(timezone('US/Pacific'))
    fileobj     = BytesIO(json.dumps(unsigned_cert).encode())
    filepath    = f"batch/{date}/{issuer_id}/unsigned/{unsigned_cert_id}.json"
    bucket.upload_fileobj(fileobj, filepath, ExtraArgs={'ACL': 'public-read'})
    

def issue_cert(issuer: IssuerInDB, recipient: RecipientInDB, badge: BadgeInDB):
    # Get issuer's active key
    issuer_public_key = [key for key in issuer.keys if key.date_revoked is None][0]

    # Get recipient's address associated with this issuer
    recipient_address = recipient.addresses[issuer.id]

    # Generate unsigned cert
    unsigned_cert_id, unsigned_cert = generate_unsigned_cert(issuer, recipient, badge)

    # Upload unsigned cert to file storage
    upload_unsigned_cert(issuer.id, unsigned_cert_id, unsigned_cert)
    
    # Update recipients DB entry with new cert
    RecipientsDB().add_cert(recipient.id, unsigned_cert_id)