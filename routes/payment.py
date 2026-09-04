from datetime import datetime, timezone

from flask import Blueprint, request, jsonify, g

from config import db
from models import Payment, Order
from routes.auth import auth_required
from services.mpesa import initiate_stk_push


payment_bp = Blueprint('payment', __name__)


@payment_bp.route('/stk-push', methods=['POST'])
@auth_required
def stk_push():
    """
    Initiate an M-Pesa STK Push for an order.
    """

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            'error': 'Invalid JSON body'
        }), 400

    order_id = data.get('order_id')
    phone_number = data.get('phone_number')

    if not order_id or not phone_number:
        return jsonify({
            'error': 'order_id and phone_number are required'
        }), 400

    # Find the order
    order = db.session.get(Order, order_id)

    if not order:
        return jsonify({
            'error': 'Order not found'
        }), 404

    # Make sure the logged-in user owns the order
    if order.user_id != g.current_user.id:
        return jsonify({
            'error': 'You can only pay for your own order'
        }), 403

    # Create a pending payment
    payment = Payment(
        order_id=order.id,
        user_id=g.current_user.id,
        amount=order.total_amount,
        phone_number=phone_number,
        status='pending'
    )

    db.session.add(payment)
    db.session.commit()

    try:
        # Send STK Push to Safaricom
        response = initiate_stk_push(
            phone_number=phone_number,
            amount=order.total_amount,
            account_reference=f'ORD-{order.id}'
        )

        # Save Safaricom request IDs
        payment.checkout_request_id = response.get(
            'CheckoutRequestID'
        )

        payment.merchant_request_id = response.get(
            'MerchantRequestID'
        )

        db.session.commit()

        return jsonify({
            'message': 'STK Push initiated successfully',
            'payment': payment.to_dict(),
            'mpesa_response': response
        }), 200

    except Exception as e:
        payment.status = 'failed'
        db.session.commit()

        return jsonify({
            'error': str(e)
        }), 500


@payment_bp.route('/<int:payment_id>', methods=['GET'])
@auth_required
def get_payment(payment_id):
    """
    Look up a payment's status — the frontend polls this after
    initiating an STK push, since the actual pending -> completed/failed
    transition happens asynchronously via the Safaricom callback below.
    """

    payment = db.session.get(Payment, payment_id)

    if not payment:
        return jsonify({'error': 'Payment not found'}), 404

    if payment.user_id != g.current_user.id:
        return jsonify({'error': 'You can only view your own payments'}), 403

    return jsonify({'payment': payment.to_dict()}), 200


@payment_bp.route('/callback', methods=['POST'])
def mpesa_callback():
    """
    Receive the M-Pesa callback from Safaricom.
    """

    data = request.get_json(silent=True)

    print("M-Pesa Callback:")
    print(data)

    if not data:
        return jsonify({
            'ResultCode': 1,
            'ResultDesc': 'Invalid callback data'
        }), 400

    try:
        stk_callback = data['Body']['stkCallback']

        result_code = stk_callback.get('ResultCode')
        result_desc = stk_callback.get('ResultDesc')

        checkout_request_id = stk_callback.get(
            'CheckoutRequestID'
        )

        # Find the payment using the CheckoutRequestID
        payment = Payment.query.filter_by(
            checkout_request_id=checkout_request_id
        ).first()

        if not payment:
            print(
                'Payment not found:',
                checkout_request_id
            )

            return jsonify({
                'ResultCode': 1,
                'ResultDesc': 'Payment record not found'
            }), 404

        # Successful payment
        if result_code == 0:

            payment.status = 'completed'

            # Read callback metadata
            callback_metadata = stk_callback.get(
                'CallbackMetadata',
                {}
            )

            for item in callback_metadata.get('Item', []):

                name = item.get('Name')
                value = item.get('Value')

                if name == 'MpesaReceiptNumber':
                    payment.mpesa_receipt_number = value

                elif name == 'TransactionDate':
                    try:
                        payment.transaction_date = datetime.strptime(
                            str(value),
                            '%Y%m%d%H%M%S'
                        )
                    except (ValueError, TypeError):
                        pass

            db.session.commit()

            print('M-Pesa payment completed successfully')

        # Failed/cancelled payment
        else:

            payment.status = 'failed'

            db.session.commit()

            print(
                'M-Pesa payment failed:',
                result_desc
            )

        return jsonify({
            'ResultCode': 0,
            'ResultDesc': 'Callback received successfully'
        }), 200

    except (KeyError, TypeError) as e:

        print('Invalid M-Pesa callback:', str(e))

        return jsonify({
            'ResultCode': 1,
            'ResultDesc': 'Invalid callback structure'
        }), 400

    except Exception as e:

        db.session.rollback()

        print('Callback processing error:', str(e))

        return jsonify({
            'ResultCode': 1,
            'ResultDesc': 'Callback processing failed'
        }), 500