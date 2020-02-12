import boto3

from models.invites import InviteInDB

def send_email(from_address, to_addresses, subject, body, is_html=False):
    msg = {
        'Subject': {
            'Data': subject,
            'Charset': 'utf-8'
        },
        'Body': {}
    }

    if is_html:
        msg['Body']['Html'] = {}
        msg['Body']['Html']['Data'] = body
        msg['Body']['Html']['Charset'] = 'utf-8'
    else:
        msg['Body']['Text'] = {}
        msg['Body']['Text']['Data'] = body
        msg['Body']['Text']['Charset'] = 'utf-8'

    boto3.client('ses').send_email(
        Source=from_address,
        Destination={
            'ToAddresses': to_addresses
        },
        Message=msg
    )
