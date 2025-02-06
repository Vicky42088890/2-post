from flask import Flask, request, render_template_string
import requests
import re
import time
import threading
import os

app = Flask(__name__)

class FacebookCommenter:
    def __init__(self):
        self.comment_count = 0

    def comment_on_post(self, cookies, post_id, comment):
        with requests.Session() as r:
            r.headers.update({
                'User-Agent': 'Mozilla/5.0 (Linux; Android 13; SM-G960U)',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Connection': 'keep-alive'
            })

            try:
                response = r.get(f'https://mbasic.facebook.com/{post_id}', cookies={"cookie": cookies})
                if response.status_code != 200:
                    print(f"❌ पेज लोड नहीं हुआ, स्टेटस कोड: {response.status_code}")
                    return

                next_action = re.search('method="post" action="([^"]+)"', response.text)
                fb_dtsg = re.search('name="fb_dtsg" value="([^"]+)"', response.text)
                jazoest = re.search('name="jazoest" value="([^"]+)"', response.text)

                if not (next_action and fb_dtsg and jazoest):
                    print("⚠️ टोकन नहीं मिले, HTML कोड चेक करें।")
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
                    print(f"❌ कमेंट फेल हुआ। Status Code: {response2.status_code}")

            except Exception as e:
                print(f"⚠️ एरर: {e}")

    def process_inputs(self, cookies, post_id, comments, delay):
        threading.Thread(target=self._process, args=(cookies, post_id, comments, delay)).start()

    def _process(self, cookies, post_id, comments, delay):
        cookie_index = 0
        while True:
            for comment in comments:
                comment = comment.strip()
                if comment:
                    time.sleep(delay)
                    self.comment_on_post(cookies[cookie_index], post_id, comment)
                    cookie_index = (cookie_index + 1) % len(cookies)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        post_id = request.form['post_id']
        delay = int(request.form['delay'])
        cookies_file = request.files['cookies_file']
        comments_file = request.files['comments_file']

        cookies = cookies_file.read().decode('utf-8').splitlines()
        comments = comments_file.read().decode('utf-8').splitlines()

        if len(cookies) == 0 or len(comments) == 0:
            return "Cookies या comments file खाली है।"

        commenter = FacebookCommenter()
        commenter.process_inputs(cookies, post_id, comments, delay)

        return "✅ कमेंट्स भेजे जा रहे हैं। अपडेट्स के लिए कंसोल चेक करें।"

    form_html = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Facebook Auto Commenter</title>
        <style>
            body { background-color: #222; color: white; text-align: center; font-family: Arial; }
            .container { background: #333; padding: 20px; margin: 50px auto; border-radius: 10px; width: 300px; }
            input, button { padding: 10px; margin: 10px; width: 90%; }
            button { background-color: limegreen; color: white; border: none; cursor: pointer; }
            button:hover { background-color: darkgreen; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>FB Auto Commenter</h1>
            <form method="POST" enctype="multipart/form-data">
                Post ID: <input type="text" name="post_id" required><br>
                Delay (seconds): <input type="number" name="delay" required><br>
                Cookies File: <input type="file" name="cookies_file" required><br>
                Comments File: <input type="file" name="comments_file" required><br>
                <button type="submit">Start Commenting</button>
            </form>
        </div>
    </body>
    </html>
    '''
    return render_template_string(form_html)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 4000))
    app.run(host='0.0.0.0', port=port)
