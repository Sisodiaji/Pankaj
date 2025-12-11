from flask import Flask, redirect, request, jsonify
import requests

APP_ID = "714013164690867"
APP_SECRET = "169b13848c922fa9139a6ac610726feb"
REDIRECT_URI = "https://pankaj-1ibi.onrender.com/callback"

app = Flask(__name__)

@app.route("/")
def home():
    return '<a href="https://www.facebook.com/v20.0/dialog/oauth?client_id=%s&redirect_uri=%s&scope=email,public_profile">Login With Facebook</a>' % (APP_ID, REDIRECT_URI)

@app.route("/callback")
def callback():
    code = request.args.get("code")
    if not code:
        return "No code received."

    token_url = f"https://graph.facebook.com/v20.0/oauth/access_token"
    params = {
        "client_id": APP_ID,
        "redirect_uri": REDIRECT_URI,
        "client_secret": APP_SECRET,
        "code": code
    }
    r = requests.get(token_url, params=params).json()
    return jsonify(r)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
