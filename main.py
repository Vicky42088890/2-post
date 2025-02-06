from flask import Flask, request, render_template_string
import requests, re, time, threading, os

app = Flask(__name__)

# Facebook Auto Comment Class
class FacebookCommenter:
    def __init__(self):
        self.comment_count = 0
        self.is_running = True

    def comment_on_post(self, cookies, post_id, comment):
        with requests.Session() as r:
            r.headers.update({
                'User-Agent': 'Mozilla/5.0 (Linux; Android 13; SM-G960U)',
                'Host': 'mbasic.facebook.com'
            })

            try:
                response = r.get(f'https://mbasic.facebook.com/{post_id}', cookies={"cookie": cookies})
                next_action = re.search('method="post" action="([^"]+)"', response.text)
                fb_dtsg = re.search('name="fb_dtsg" value="([^"]+)"', response.text)
                jazoest = re.search('name="jazoest" value="([^"]+)"', response.text)

                if not (next_action and fb_dtsg and jazoest):
                    print("⚠️ टोकन नहीं मिले।")
                    return

                data = {
                    'fb_dtsg': fb_dtsg.group(1),
                    'jazoest': jazoest.group(1),
                    'comment_text': comment,
                    'comment': 'Submit'
                }

                response2 = r.post(f'https://mbasic.facebook.com{next_action.group(1)}', data=data, cookies={"cookie": cookies})
                if 'comment_success' in response2.url:
                    self.comment_count += 1
                    print(f"✅ कमेंट {self.comment_count} सफलतापूर्वक पोस्ट हुआ!")
                else:
                    print("❌ कमेंट पोस्ट नहीं हो पाया।")

            except Exception as e:
                print(f"⚠️ एरर: {e}")

    def process_inputs(self, cookies, post_id, comments, delay):
        while self.is_running:
            for cookie, comment in zip(cookies, comments):
                self.comment_on_post(cookie, post_id, comment)
                time.sleep(delay)

    def stop(self):
        self.is_running = False


# Flask Route
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        post_id = request.form['post_id']
        delay = int(request.form['delay'])

        cookies = request.files['cookies_file'].read().decode().splitlines()
        comments = request.files['comments_file'].read().decode().splitlines()

        commenter = FacebookCommenter()
        thread = threading.Thread(target=commenter.process_inputs, args=(cookies, post_id, comments, delay))
        thread.start()

        return "✅ कमेंट पोस्ट हो रहे हैं।"

    # HTML + CSS
    html_content = '''
    <!DOCTYPE html>
    <html lang="hi">
    <head>
        <meta charset="UTF-8">
        <title>FB Auto Comment Bot</title>
        <style>
            body {
                background: #111;
                color: #fff;
                font-family: Arial, sans-serif;
                text-align: center;
                padding: 20px;
            }
            .container {
                background: #222;
                padding: 20px;
                border-radius: 10px;
                display: inline-block;
            }
            input, button {
                padding: 10px;
                margin: 10px;
                border-radius: 5px;
                border: none;
            }
            button {
                background-color: yellow;
                cursor: pointer;
            }
            button:hover {
                background-color: orange;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔥 FB Auto Comment Bot 🔥</h1>
            <form method="POST" enctype="multipart/form-data">
                <input type="text" name="post_id" placeholder="Post ID डालें" required><br>
                <input type="number" name="delay" placeholder="Delay (सेकंड)" required><br>
                <label>Cookies File:</label>
                <input type="file" name="cookies_file" required><br>
                <label>Comments File:</label>
                <input type="file" name="comments_file" required><br>
                <button type="submit">🚀 Start Commenting</button>
            </form>
        </div>
    </body>
    </html>
    '''
    return render_template_string(html_content)


# Server Run
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
