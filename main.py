from flask import Flask, request, render_template_string
import requests
import re
import time
import threading

app = Flask(__name__)

class FacebookCommentBot:
    def __init__(self):
        self.comment_count = 0

    def comment_on_post(self, cookie, post_id, comment):
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Linux; Android 13; SM-G960U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.5790.166 Mobile Safari/537.36'
        })

        response = session.get(f'https://mbasic.facebook.com/{post_id}', cookies={"cookie": cookie})
        action = re.search('method="post" action="([^"]+)"', response.text)
        fb_dtsg = re.search('name="fb_dtsg" value="([^"]+)"', response.text)
        jazoest = re.search('name="jazoest" value="([^"]+)"', response.text)

        if not (action and fb_dtsg and jazoest):
            print("❌ Error: Required parameters not found.")
            return

        post_url = f'https://mbasic.facebook.com{action.group(1).replace("amp;", "")}'
        data = {
            'fb_dtsg': fb_dtsg.group(1),
            'jazoest': jazoest.group(1),
            'comment_text': comment,
            'submit': 'Comment'
        }

        response = session.post(post_url, data=data, cookies={"cookie": cookie})
        if 'comment_success' in response.url:
            self.comment_count += 1
            print(f"✅ Comment {self.comment_count} posted successfully!")
        else:
            print(f"❌ Failed to post comment. Status Code: {response.status_code}")

    def start_commenting(self, cookies, post_id, comments, delay):
        def run():
            while True:
                for cookie in cookies:
                    for comment in comments:
                        self.comment_on_post(cookie, post_id, comment)
                        time.sleep(delay)

        threading.Thread(target=run).start()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        post_id = request.form['post_id']
        delay = int(request.form['delay'])
        cookies = request.files['cookies_file'].read().decode().splitlines()
        comments = request.files['comments_file'].read().decode().splitlines()

        bot = FacebookCommentBot()
        bot.start_commenting(cookies, post_id, comments, delay)

        return "✅ Comments are being posted. Check the console for updates."

    form_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Raghu's Auto Comment Bot 🚀</title>
        <style>
            body { background-color: #1e1e1e; color: white; font-family: Arial; text-align: center; padding: 50px; }
            input, button { padding: 10px; margin: 5px; border-radius: 5px; }
            button { background-color: #4CAF50; color: white; border: none; }
            button:hover { background-color: #45a049; }
        </style>
    </head>
    <body>
        <h1>🔥 Facebook Auto Comment Bot for rullx 😈</h1>
        <form method="POST" enctype="multipart/form-data">
            <label>Post ID:</label><br><input type="text" name="post_id" required><br>
            <label>Delay (in seconds):</label><br><input type="number" name="delay" required><br>
            <label>Upload Cookies File:</label><br><input type="file" name="cookies_file" required><br>
            <label>Upload Comments File:</label><br><input type="file" name="comments_file" required><br>
            <button type="submit">🚀 Start Commenting</button>
        </form>
    </body>
    </html>
    """
    return render_template_string(form_html)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
