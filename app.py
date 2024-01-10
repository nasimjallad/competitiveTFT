from flask import Flask, redirect, request, session, render_template_string
from requests_oauthlib import OAuth2Session
import requests.auth

app = Flask(__name__)
app.secret_key = 'asdjaskdask2189'  # Change this to a random secret key

CLIENT_ID = '571rXkQqATNu0uziO0HPWA'
CLIENT_SECRET = '8MZVS7Bx0uCAx7jz0RjV4Efiu6UfQg'
REDIRECT_URI = 'https://127.0.0.1:5000/reddit_callback'  # Use 'http://' for local testing
AUTHORIZATION_BASE_URL = 'https://www.reddit.com/api/v1/authorize'
TOKEN_URL = 'https://www.reddit.com/api/v1/access_token'

# Simple HTML template to display the username
html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Reddit Username</title>
</head>
<body>
    <h1>Welcome, {{ username }}!</h1>
</body>
</html>
"""

@app.route('/')
def index():
    if 'reddit_token' in session:
        reddit = OAuth2Session(CLIENT_ID, token=session['reddit_token'])
        response = reddit.get('https://oauth.reddit.com/api/v1/me', headers={'User-Agent': 'Python Flask'})

        if response.status_code == 200:
            try:
                return render_template_string(html_template, username=response.json()["name"])
            except ValueError:
                return "Invalid JSON response: " + response.text
        else:
            return f"Error fetching data: Status code {response.status_code}"

    else:
        return redirect('/login')

@app.route('/login')
def login():
    reddit = OAuth2Session(CLIENT_ID, redirect_uri=REDIRECT_URI, scope=['identity'])
    authorization_url, _ = reddit.authorization_url(AUTHORIZATION_BASE_URL, duration='permanent')
    return redirect(authorization_url)

@app.route('/reddit_callback')
def reddit_callback():
    reddit = OAuth2Session(CLIENT_ID, redirect_uri=REDIRECT_URI)
    auth = requests.auth.HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)
    token = reddit.fetch_token(
        TOKEN_URL,
        authorization_response=request.url,
        client_secret=CLIENT_SECRET,
        auth=auth,
        headers={"User-Agent": "Python Flask"}
    )
    session['reddit_token'] = token
    return '<script>window.location.href="/";</script>'

if __name__ == '__main__':
    app.run(ssl_context='adhoc')
