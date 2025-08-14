import os
from flask import Flask, request, jsonify, send_from_directory, render_template
import stripe
from flask_cors import CORS
import smtplib
from email.mime.text import MIMEText
import redis
from flask_mail import Mail, Message

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

# Set your Stripe secret key here
stripe.api_key = 'sk_test_51RvirJDlZyQ3F8XX4cEAa3yDZAFLnr9iY9R7VHyX1dCwu35jggmGFuqWxU8atGrqestzuz9blwPzWwYnzqiLSRYC00ZORj8eAp'

# Connect to Redis
redis_client = redis.Redis(host='127.0.0.1', port=6379, db=0, decode_responses=True)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 't9491359@gmail.com'      # <-- replace with your Gmail
app.config['MAIL_PASSWORD'] = '100100@@'         # <-- replace with your Gmail app password

mail = Mail(app)

@app.route('/')
def index():
    return render_template('config.html')

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    remember_me = data.get('rememberMe', False)
    if username and email and password:
        # Optionally, set a flag for "remember me"
        if remember_me:
            redis_client.set(f"remember:{username}", "1")
        return jsonify({"message": "Login successful", "email": email})
    else:
        return jsonify({"error": "Missing fields"}), 400

@app.route('/payment_methos', methods=['POST'])
def payment_methos():
    data = request.get_json()
    product = data.get('product', 'Product')
    price = data.get('price', '0')
    username = data.get('username', 'User')

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': product,
                    },
                    'unit_amount': int(float(price) * 100),
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url='http://127.0.0.1:5000/success',
            cancel_url='http://127.0.0.1:5000/cancel',
        )

        return jsonify({'sessionId': session.id, 'checkout_url': session.url})
    except Exception as e:
        return jsonify(error=str(e)), 400

@app.route('/success')
def success():
    # Send email after payment is successful
    sender_email = "t9491359@gmail.com"
    sender_password = "ontr jccs ohay mlpn"
    to_email = "mustafamohammed161616@gmail.com"
    subject = "Your Gym Store Purchase"
    body = f"Hello,\n\nThank you for your purchase!\n\nYour payment was successful.\n\n- Gym Store Team"

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = to_email

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, to_email, msg.as_string())
    except Exception as e:
        print("Email error:", e)

    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Order Success</title>
        <link rel="stylesheet" href="/success.css">
    </head>
    <body>
        <h1>Payment successful!</h1>
        <p>Your order will be completed soon.</p>
        <script>
            setTimeout(function() {
                window.location.href = '/';
            }, 5000);
        </script>
    </body>
    </html>
    """

@app.route('/cancel')
def cancel():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Payment Cancelled</title>
        <link rel="stylesheet" href="/success.css">
    </head>
    <body>
        <h1>Payment cancelled.</h1>
        <p>You can try again or contact support.</p>
        <script>
            setTimeout(function() {
                window.location.href = '/';
            }, 5000);
        </script>
    </body>
    </html>
    """

@app.route('/success.css')
def success_css():
    return send_from_directory(os.path.dirname(__file__), 'success.css')

if __name__ == '__main__':
    app.run(port=5000)