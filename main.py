from flask import Flask, request, render_template_string
import requests
import time
import threading

app = Flask(__name__)

class FacebookCommenter:
    def __init__(self):
        self.comment_count = 0

    def comment_on_post(self, cookie, post_id, comment):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.5790.166 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        session = requests.Session()
        session.headers.update(headers)
        session.cookies.set('cookie', cookie)

        post_url = f'https://mbasic.facebook.com/{post_id}'
        response = session.get(post_url)

        if 'name="fb_dtsg"' not in response.text:
            print("Login failed or invalid cookie.")
            return

        fb_dtsg = response.text.split('name="fb_dtsg" value="')[1].split('"')[0]
        jazoest = response.text.split('name="jazoest" value="')[1].split('"')[0]

        action_url = response.text.split('method="post" action="')[1].split('"')[0].replace('amp;', '')

        payload = {
            'fb_dtsg': fb_dtsg,
            'jazoest': jazoest,
            'comment_text': comment,
            'submit': 'Comment'
        }

        comment_response = session.post(f'https://mbasic.facebook.com{action_url}', data=payload)

        if comment_response.status_code == 200:
            self.comment_count += 1
            print(f"✅ Comment {self.comment_count} posted successfully.")
        else:
            print("❌ Failed to post comment.")

    def start_commenting(self, cookies, post_id, comments, delay):
        while True:
            for cookie in cookies:
                for comment in comments:
                    self.comment_on_post(cookie, post_id, comment)
                    time.sleep(delay)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        post_id = request.form['post_id']
        delay = int(request.form['delay'])
        cookies = request.form['cookies'].splitlines()
        comments = request.form['comments'].splitlines()

        commenter = FacebookCommenter()
        threading.Thread(target=commenter.start_commenting, args=(cookies, post_id, comments, delay)).start()

        return "✅ Comments are being posted. Check logs for updates."

    return render_template_string('''
        <h1>Facebook Auto Comment Bot</h1>
        <form method="POST">
            Post ID: <input type="text" name="post_id" required><br><br>
            Delay (in seconds): <input type="number" name="delay" required><br><br>
            Cookies (one per line): <textarea name="cookies" rows="5" required></textarea><br><br>
            Comments (one per line): <textarea name="comments" rows="5" required></textarea><br><br>
            <button type="submit">Start Commenting</button>
        </form>
    ''')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
