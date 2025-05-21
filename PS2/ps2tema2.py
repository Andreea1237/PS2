# app.py
from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
import os

app = Flask(__name__)

temperature = "N/A"
cloud_led_state = 0
messages = []
message_valid = 0
message = "NULL"
flood_events = []

def send_email(subject, body):
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()

        email_user = os.getenv('EMAIL_USER')
        email_pass = os.getenv('EMAIL_PASS')

        server.login(email_user, email_pass)
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = email_user
        msg['To'] = "denysavydac@gmail.com"

        server.sendmail(email_user, "denysavydac@gmail.com", msg.as_string())
        server.quit()
        print("Email trimis cu succes!")
    except Exception as e:
        print(f"Eroare la trimiterea email-ului: {e}")

@app.route('/')
def main_page():
    led_state_text = 'ON' if cloud_led_state == 1 else 'OFF'
    return render_template(
        'ps2.html',
        temperature=temperature,
        led_state=led_state_text,
        flood_events=flood_events,
        messages=messages
    )

@app.route('/update_temperature', methods=['POST'])
def update_temperature():
    global temperature
    temperature = request.form['temperature']
    return 'Temperature updated'

@app.route('/get_temperature', methods=['GET'])
def get_temperature():
    return temperature

@app.route('/get_led', methods=['GET'])
def get_led():
    return str(cloud_led_state)

@app.route('/set_led', methods=['POST'])
def set_led():
    global cloud_led_state
    action = request.form['action']
    if action == 'on':
        cloud_led_state = 1
    elif action == 'off':
        cloud_led_state = 0
    return redirect(url_for('main_page'))

@app.route('/send_message', methods=['POST'])
def send_message():
    global message, message_valid, messages
    msg = request.form['message']
    message = msg
    message_valid = 1
    timestamped = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {msg}"
    messages.append(timestamped)
    if len(messages) > 10:
        messages.pop(0)
    return redirect(url_for('main_page'))

@app.route('/get_message', methods=['GET'])
def get_message():
    global message_valid, message
    if message_valid == 1:
        message_valid = 0
        return message
    return "NULL"

@app.route('/detect_flood', methods=['POST'])
def detect_flood():
    event_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    flood_events.append(f"Inundație detectată la {event_time}")
    if len(flood_events) > 10:
        flood_events.pop(0)

    print(f"[{event_time}] Inundație detectată de la Arduino!")
    send_email("Flood Alert", f"Inundație detectată la {event_time}")
    return "Flood event recorded", 200


@app.route('/clear_flood_event', methods=['POST'])
def clear_flood_event():
    event_index = int(request.form['event_index'])
    if 0 <= event_index < len(flood_events):
        flood_events.pop(event_index)
    return redirect(url_for('main_page'))

if __name__ == '__main__':
    print("Flask server pornește...")
    app.run(debug=True)
