from flask import Flask, request, jsonify
import requests
import time

app = Flask(__name__)

# Function to send a message
def send_message(page_access_token, recipient_id, message_text):
    url = "https://graph.facebook.com/v17.0/me/messages"
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    }
    params = {
        "access_token": page_access_token
    }
    
    response = requests.post(url, headers=headers, json=payload, params=params)
    return response.json()

# Home Page with Form
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        page_access_token = request.form.get("access_token")
        recipient_id = request.form.get("recipient_id")
        message = request.form.get("message")
        delay = int(request.form.get("delay", 0))
        
        # Adding delay if required
        if delay > 0:
            time.sleep(delay)
        
        # Sending the message
        result = send_message(page_access_token, recipient_id, message)
        return jsonify(result)

    return '''
    <h1>Facebook Message Sender</h1>
    <form method="POST">
        Page Access Token: <input type="text" name="access_token"><br><br>
        Recipient ID: <input type="text" name="recipient_id"><br><br>
        Message: <input type="text" name="message"><br><br>
        Delay (in seconds): <input type="number" name="delay" value="0"><br><br>
        <button type="submit">Send Message</button>
    </form>
    '''

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
