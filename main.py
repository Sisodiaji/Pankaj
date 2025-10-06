""" Simple Flask web UI for Batch Facebook Reaction Tool Save this file as app.py and run: python3 app.py

This is intentionally synchronous: when you press Start, the server will perform the reactions sequentially and then show you a results page. Use ONLY with Page/User tokens you own and have permission to use. Do NOT use this to operate on other people's accounts without permission.

Requirements: pip install flask requests

Notes:

The app accepts a text file of Post IDs (one per line) or pasted Post IDs.

Reaction types supported: LIKE, LOVE, WOW, CARE, SAD, ANGRY

Default delay between requests is configurable in the form.

The app returns a table with per-post status and API response text.


Security: This is a local-tool intended to be run on your machine or a trusted server. Do not expose it publicly without adding authentication and HTTPS.

""" from flask import Flask, request, render_template_string, send_file, redirect, url_for import time, requests, io

app = Flask(name)

INDEX_HTML = """ <!doctype html>

<html>
<head>
  <meta charset="utf-8">
  <title>Facebook Batch Reaction UI</title>
  <style>
    body{font-family: Arial, Helvetica, sans-serif; max-width:900px;margin:30px auto;padding:10px}
    label{display:block;margin-top:12px}
    textarea{width:100%;height:120px}
    input[type=text], input[type=number]{width:100%;padding:8px}
    table{width:100%;border-collapse:collapse;margin-top:16px}
    th,td{border:1px solid #ddd;padding:8px;text-align:left}
    th{background:#f4f4f4}
    .ok{color:green}
    .err{color:#c00}
    .small{font-size:0.9em;color:#666}
    .hint{background:#f9f9f9;padding:10px;border-left:4px solid #ddd;margin-bottom:12px}
  </style>
</head>
<body>
  <h1>Facebook Batch Reaction UI</h1>
  <div class="hint">
    <strong>Use only with tokens you own.</strong> This tool calls Facebook Graph API <code>/&lt;post-id&gt;/reactions</code>.
    Make sure your token has required permissions (e.g. pages_manage_engagement / pages_read_engagement).</n  </div>  <form method="POST" action="/start" enctype="multipart/form-data">
    <label>Page / User Access Token (required)</label>
    <input type="text" name="token" required placeholder="EAAX..." /><label>Reaction type</label>
<select name="reaction">
  <option value="LOVE">LOVE (🩷)</option>
  <option value="LIKE">LIKE</option>
  <option value="WOW">WOW</option>
  <option value="CARE">CARE</option>
  <option value="SAD">SAD</option>
  <option value="ANGRY">ANGRY</option>
</select>

<label>Delay between reactions (seconds)</label>
<input type="number" name="delay" value="3" min="0" step="0.5" />

<label>Upload file containing Post IDs (one per line) OR paste Post IDs below</label>
<input type="file" name="file" accept=".txt" />
<label>Or paste Post IDs (one per line)</label>
<textarea name="pasted_ids" placeholder="123_456\n789_012"></textarea>

<label class="small">If you use a Page Token, use post IDs like <code>PAGEID_POSTID</code>.</label>

<button type="submit" style="margin-top:12px;padding:10px 14px">Start</button>

  </form>  <p class="small">This tool is synchronous — the page will load results after all requests finish.</p>
</body>
</html>
"""RESULTS_HTML = """ <!doctype html>

<html>
<head>
  <meta charset="utf-8">
  <title>Results — Batch Reaction</title>
  <style>
    body{font-family: Arial, Helvetica, sans-serif;max-width:1000px;margin:20px auto;padding:10px}
    table{width:100%;border-collapse:collapse;margin-top:12px}
    th,td{border:1px solid #ddd;padding:8px;text-align:left}
    th{background:#f4f4f4}
    .ok{color:green}
    .err{color:#c00}
    pre{white-space:pre-wrap;word-wrap:break-word;font-size:0.9em}
    a.button{display:inline-block;padding:8px 12px;margin-top:10px;background:#2b7cff;color:#fff;border-radius:4px;text-decoration:none}
  </style>
</head>
<body>
  <h1>Batch Reaction Results</h1>
  <p>Reaction: <strong>{{reaction}}</strong> &nbsp;|&nbsp; Delay: <strong>{{delay}}</strong>s &nbsp;|&nbsp; Token: <em class="small">(hidden)</em></p>
  <a class="button" href="/">« Back</a>
  <a class="button" href="/download_log?key={{key}}">Download CSV Log</a>  <table>
    <thead>
      <tr><th>#</th><th>Post ID</th><th>Status</th><th>HTTP Code</th><th>Response</th></tr>
    </thead>
    <tbody>
      {% for r in results %}
      <tr>
        <td>{{loop.index}}</td>
        <td>{{r.post_id}}</td>
        <td class="{{ 'ok' if r.ok else 'err' }}">{{'OK' if r.ok else 'FAIL'}}</td>
        <td>{{r.code}}</td>
        <td><pre>{{r.text}}</pre></td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
</body>
</html>
"""In-memory simple log store (key -> csv bytes)

LOG_STORE = {}

@app.route('/') def index(): return render_template_string(INDEX_HTML)

@app.route('/start', methods=['POST']) def start(): token = request.form.get('token', '').strip() reaction = request.form.get('reaction', 'LOVE').strip().upper() try: delay = float(request.form.get('delay', '3')) except: delay = 3.0

if not token:
    return "Missing token", 400

# collect post ids from uploaded file or pasted text
post_ids = []
f = request.files.get('file')
if f and f.filename:
    try:
        data = f.read().decode('utf-8')
    except:
        data = f.read().decode('latin-1')
    for line in data.splitlines():
        line = line.strip()
        if line:
            post_ids.append(line)

pasted = request.form.get('pasted_ids', '').strip()
if pasted:
    for line in pasted.splitlines():
        line = line.strip()
        if line:
            post_ids.append(line)

# dedupe while preserving order
seen = set()
post_ids_clean = []
for pid in post_ids:
    if pid not in seen:
        seen.add(pid)
        post_ids_clean.append(pid)
post_ids = post_ids_clean

if not post_ids:
    return "No Post IDs provided.", 400

results = []

for pid in post_ids:
    url = f'https://graph.facebook.com/v17.0/{pid}/reactions'
    payload = {'type': reaction, 'access_token': token}
    try:
        r = requests.post(url, data=payload, timeout=20)
        ok = (r.status_code == 200)
        text = r.text
        code = r.status_code
    except Exception as e:
        ok = False
        text = str(e)
        code = 0
    results.append({'post_id': pid, 'ok': ok, 'text': text, 'code': code})
    # delay before next
    time.sleep(delay)

# build a CSV log and store it in-memory with a key
csv_buf = io.StringIO()
csv_buf.write('post_id,ok,http_code,response\n')
for r in results:
    # sanitize commas/newlines
    resp_s = r['text'].replace('"', '""').replace('\n', ' | ').replace('\r', '')
    csv_buf.write(f'"{r["post_id"]}",{int(r["ok"])},{r["code"]},"{resp_s}"\n')
csv_bytes = csv_buf.getvalue().encode('utf-8')
key = str(int(time.time()*1000))
LOG_STORE[key] = csv_bytes

return render_template_string(RESULTS_HTML, results=results, reaction=reaction, delay=delay, key=key)

@app.route('/download_log') def download_log(): key = request.args.get('key') if not key or key not in LOG_STORE: return redirect(url_for('index')) b = LOG_STORE.pop(key) return send_file(io.BytesIO(b), mimetype='text/csv', as_attachment=True, download_name='batch_reaction_log.csv')

if name == 'main': print("Running on http://127.0.0.1:5000 — use only locally or on a trusted network") app.run(debug=True)
