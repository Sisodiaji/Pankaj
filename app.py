from flask import Flask, request, render_template_string, send_file, redirect, url_for
import time, requests, io, os

app = Flask(__name__)

@app.route('/')
def index():
    return '''
    <h2>🩷 TruMax Facebook Reaction Tool</h2>
    <form method="POST" action="/start" enctype="multipart/form-data">
      Token:<br><input type="text" name="token" required style="width:400px"><br><br>
      Reaction:
      <select name="reaction">
        <option value="LOVE">LOVE 🩷</option>
        <option value="LIKE">LIKE 👍</option>
        <option value="WOW">WOW 😮</option>
        <option value="CARE">CARE 🤗</option>
        <option value="SAD">SAD 😢</option>
        <option value="ANGRY">ANGRY 😡</option>
      </select><br><br>
      Delay (sec): <input type="number" name="delay" value="3" step="0.5"><br><br>
      Upload Post ID file (.txt): <input type="file" name="file"><br><br>
      OR Paste Post IDs:<br>
      <textarea name="pasted_ids" rows="6" cols="60"></textarea><br><br>
      <button type="submit">Start Reaction</button>
    </form>
    '''

@app.route('/start', methods=['POST'])
def start():
    token = request.form.get('token', '').strip()
    reaction = request.form.get('reaction', 'LOVE')
    delay = float(request.form.get('delay', 3))
    post_ids = []

    if 'file' in request.files and request.files['file'].filename:
        content = request.files['file'].read().decode('utf-8')
        post_ids += [line.strip() for line in content.splitlines() if line.strip()]

    pasted = request.form.get('pasted_ids', '')
    if pasted:
        post_ids += [line.strip() for line in pasted.splitlines() if line.strip()]

    post_ids = list(dict.fromkeys(post_ids))
    if not post_ids:
        return "⚠️ No Post IDs found!"

    results = []
    for pid in post_ids:
        url = f'https://graph.facebook.com/v17.0/{pid}/reactions'
        payload = {'type': reaction, 'access_token': token}
        try:
            r = requests.post(url, data=payload, timeout=20)
            results.append((pid, r.status_code, r.text))
        except Exception as e:
            results.append((pid, 0, str(e)))
        time.sleep(delay)

    html = "<h3>✅ Reaction Completed</h3><table border=1 cellpadding=5><tr><th>Post ID</th><th>Code</th><th>Response</th></tr>"
    for pid, code, text in results:
        color = "green" if code == 200 else "red"
        html += f"<tr><td>{pid}</td><td style='color:{color}'>{code}</td><td>{text}</td></tr>"
    html += "</table><br><a href='/'>Back</a>"
    return html

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
