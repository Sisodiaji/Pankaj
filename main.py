from flask import Flask, redirect, request, session, url_for, render_template, jsonify
import requests, os

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "change-me-please")

APP_ID = os.environ.get("FB_APP_ID", "1549920276327064")
APP_SECRET = os.environ.get("FB_APP_SECRET", "d9944bc84aa7c88807a795915e1a5aaf")
REDIRECT_URI = os.environ.get("FB_REDIRECT_URI", "https://pankaj-1ibi.onrender.com/callback")
SCOPES = os.environ.get("FB_SCOPES", "public_profile,email")

@app.route("/")
def index():
    fb_login_url = (
        f"https://www.facebook.com/v16.0/dialog/oauth?client_id={APP_ID}"
        f"&redirect_uri={REDIRECT_URI}&response_type=code&scope={SCOPES}"
    )
    return render_template('index.html',
                           fb_login_url=fb_login_url,
                           token=session.get('short_token'),
                           long_token=session.get('long_token'))

@app.route("/callback")
def callback():
    error=request.args.get("error")
    if error: return f"Facebook error: {error}",400
    code=request.args.get("code")
    if not code: return "No code",400

    r=requests.get("https://graph.facebook.com/v16.0/oauth/access_token",
        params={"client_id":APP_ID,"redirect_uri":REDIRECT_URI,"client_secret":APP_SECRET,"code":code})
    data=r.json()
    if "error" in data: return jsonify(data),400
    short=data.get("access_token")
    session["short_token"]=short

    r2=requests.get("https://graph.facebook.com/v16.0/oauth/access_token",
        params={"grant_type":"fb_exchange_token","client_id":APP_ID,"client_secret":APP_SECRET,"fb_exchange_token":short})
    data2=r2.json()
    long=data2.get("access_token")
    session["long_token"]=long

    return redirect(url_for("index"))

if __name__=="__main__":
    app.run(host="0.0.0.0",port=int(os.environ.get("PORT",5000)),debug=True)
