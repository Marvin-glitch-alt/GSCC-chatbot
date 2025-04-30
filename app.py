from flask import Flask, request
from flask import jsonify
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask_cors import CORS
from email_notifier import send_handoff_email
from dotenv import load_dotenv
import os
import json
import re
import smtplib



if os.getenv("FLASK_ENV") != "production":
    load_dotenv()

app = Flask(__name__)
CORS(app)


with open('ggscc_knowledge_base.json', 'r') as f:
    knowledge_base = json.load(f)

@app.route('/chat', methods=['POST'])
def chat():
    
    user_input = request.json.get('message', '').lower()

    
    cleaned_input = re.sub(r'[^\w\s]', '', user_input)
    cleaned_input = re.sub(r'\s+', ' ', cleaned_input).strip()

    print(f"User input after cleaning: {cleaned_input}")  

    best_match = None
    highest_score = 0

    
    for intent in knowledge_base['intents']:
        for pattern in intent['patterns']:
             if "talk to a consultant" in cleaned_input:
                send_handoff_email(message_text=cleaned_input)
                return jsonify({"response": "Please fill in the form on the contact page and a consultant will get in touch with you shortly. ✅"})
             if re.search(rf"\b{re.escape(pattern.lower())}\b", cleaned_input, re.IGNORECASE):
                return jsonify({"response": intent['response']})
             score = len(pattern.split())
             if score > highest_score:
                    highest_score = score
                    best_match = intent

    return jsonify({"response": "I'm sorry, I couldn't understand your request. Could you please rephrase it?"})



@app.route('/contact', methods=['POST'])
def contact():

    data = request.get_json(silent=True)
    name = data.get('name') if data else None
    email = data.get('email') if data else None
    phone = data.get('phone') if data else None
    message = data.get('message') if data else None


    subject = "New Contact Form Submission"
    body = f"""
    You have a new contact form submission:

    Name: {name}
    Email: {email}
    Phone: {phone}
    Message: {message}
    """

    try:
        send_email(subject, body)
        return jsonify({"message": "Message sent successfully"}), 200
    except Exception as e:
        return jsonify({"message": "Failed to send message"}), 500
    

def send_email(subject, body):
    sender_email = os.getenv("EMAIL_USER")
    sender_password = os.getenv("EMAIL_PASS")
    receiver_email = os.getenv("RECEIVER_EMAIL")
    msg = MIMEMultipart()

    if not all([sender_email, sender_password, receiver_email]):
        raise Exception("Missing email config. Check your .env or environment variables.")

    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
         server.starttls()
         server.login(sender_email, sender_password)
         server.send_message(msg)
    except Exception as e:
        raise  



if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
