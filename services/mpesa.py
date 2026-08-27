import base64
from datetime import datetime

import requests
from flask import current_app


def get_mpesa_access_token():
    """
    Get an OAuth access token from Safaricom Daraja.
    """

    consumer_key = current_app.config.get('MPESA_CONSUMER_KEY')
    consumer_secret = current_app.config.get('MPESA_CONSUMER_SECRET')
    environment = current_app.config.get('MPESA_ENVIRONMENT', 'sandbox')

    if not consumer_key or not consumer_secret:
        raise ValueError(
            'M-Pesa Consumer Key and Secret are not configured'
        )

    if environment == 'production':
        url = 'https://api.safaricom.co.ke/oauth/v1/generate'
    else:
        url = 'https://sandbox.safaricom.co.ke/oauth/v1/generate'

    try:
        response = requests.get(
            url,
            params={
                'grant_type': 'client_credentials'
            },
            auth=(consumer_key, consumer_secret),
            timeout=30
        )

        print("M-Pesa URL:", response.url)
        print("M-Pesa status:", response.status_code)
        print("M-Pesa response:", response.text)

        response.raise_for_status()

        data = response.json()

        if 'access_token' not in data:
            raise Exception(
                f'Access token missing from response: {data}'
            )

        return data['access_token']

    except requests.exceptions.RequestException as e:
        raise Exception(
            f'Failed to get M-Pesa access token: {e}'
        )


def initiate_stk_push(phone_number, amount, account_reference):
    """
    Initiate an M-Pesa STK Push.
    """

    access_token = get_mpesa_access_token()

    shortcode = current_app.config.get('MPESA_SHORTCODE')
    passkey = current_app.config.get('MPESA_PASSKEY')
    callback_url = current_app.config.get('MPESA_CALLBACK_URL')
    environment = current_app.config.get('MPESA_ENVIRONMENT', 'sandbox')

    if not shortcode:
        raise ValueError('MPESA_SHORTCODE is not configured')

    if not passkey:
        raise ValueError('MPESA_PASSKEY is not configured')

    if not callback_url:
        raise ValueError('MPESA_CALLBACK_URL is not configured')

    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')

    password_string = f'{shortcode}{passkey}{timestamp}'

    password = base64.b64encode(
        password_string.encode('utf-8')
    ).decode('utf-8')

    if environment == 'production':
        url = (
            'https://api.safaricom.co.ke/'
            'mpesa/stkpush/v1/processrequest'
        )
    else:
        url = (
            'https://sandbox.safaricom.co.ke/'
            'mpesa/stkpush/v1/processrequest'
        )

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    payload = {
        'BusinessShortCode': shortcode,
        'Password': password,
        'Timestamp': timestamp,
        'TransactionType': 'CustomerPayBillOnline',
        'Amount': int(amount),
        'PartyA': phone_number,
        'PartyB': shortcode,
        'PhoneNumber': phone_number,
        'CallBackURL': callback_url,
        'AccountReference': account_reference,
        'TransactionDesc': 'Mealy food order'
    }

    try:
        response = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=30
        )

        print("STK Push status:", response.status_code)
        print("STK Push response:", response.text)

        response.raise_for_status()

        return response.json()

    except requests.exceptions.RequestException as e:
        raise Exception(
            f'STK Push request failed: {e}'
        )