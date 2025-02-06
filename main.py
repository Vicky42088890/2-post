from flask import Flask, request, render_template_string
import requests
import time
import os

app = Flask(__name__)

# Facebook Comment Function
def post_comment(access_token, post_id, message):
    url = f"https://graph.facebook.com/{post_id}/comments"
    payload = {
        'message': message,
        'access_token': access_token
    }
    response = requests.post(url, data=payload)
    return response.json()

# Flask App Route
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        access_token = request.form['access_token']
        post_id = request.form['post_id']
        message = request.form['message']
        delay = int(request.form['delay'])

        for i in range(5):  # Number of comments to post (Change as needed)
            result = post_comment(access_token, post_id, f"{message} #{i+1}")
            if 'id' in result:
                print(f"✅ Comment {i+1} posted successfully!")
            else:
                print(f"❌ Failed to post comment: {result}")
            time.sleep(delay)

        return "Comments have been posted. Check your Facebook post!"

    # HTML Form
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Facebook Auto Commenter - Raghu's Bot 😈</title>
        <style>
            body { font-family: Arial, background-color: #1c1c1c; color: white; text-align: center; padding: 50px; }
            input, button { padding: 10px; margin: 5px; width: 80%; border-radius: 5px; }
            button { background-color: #ffcc00; border: none; cursor: pointer; }
            button:hover { background-color: #ffaa00; }
        </style>
    </head>
    <body>
        <h1>🔥 Raghu's Auto Comment Bot for rullx 😈 🔥</h1>
        <form method="POST">
            Access Token: <input type="text" name="access_token" required><br>
            Post ID: <input type="text" name="post_id" required><br>
            Message: <input type="text" name="message" required><br>
            Delay (seconds): <input type="number" name="delay" value="30" required><br>
            <button type="submit">Start Commenting 🚀</button>
        </form>
    </body>
    </html>
    ''')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
