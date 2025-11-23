# app.py (Sab Se Aasan Version - Sirf Non-2FA Accounts Ke Liye)

import os
import requests
import hashlib
from flask import Flask, request, render_template_string

app = Flask(__name__)

def get_simple_token(username, password):
    """
    Sirf username aur asli password se token nikalta hai.
    Yeh sirf un accounts par kaam karega jin par 2FA on nahi hai.
    """
    api_key = "882a8490361da98702bf97a021ddc14d"
    secret = "62f8ce9f74b12f84c123cc23437a4a32"
    
    params = {
        'api_key': api_key, 'credentials_type': 'password', 'email': username,
        'format': 'JSON', 'generate_machine_id': '1', 'generate_session_cookies': '1',
        'locale': 'en_US', 'method': 'auth.login', 'password': password,
        'return_ssl_resources': '0', 'v': '1.0'
    }

    sig_string = "".join([f"{key}={value}" for key, value in sorted(params.items())]) + secret
    params['sig'] = hashlib.md5(sig_string.encode('utf-8')).hexdigest()

    api_url = 'https://api.facebook.com/restserver.php'
    headers = {'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 12; SM-G988N Build/SP1A.210812.016) [FBAN/FB4A;FBAV/353.0.0.28.118;]'}

    try:
        response = requests.post(api_url, data=params, headers=headers, timeout=15)
        response_data = response.json()

        if 'access_token' in response_data:
            return response_data['access_token']
        elif 'error_msg' in response_data:
            return f"Error: {response_data['error_msg']}"
        else:
            return f"Error: An unknown error occurred."
    except Exception as e:
        return f"Error: {e}"

# --- Simple HTML Template ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Simple Token Generator</title>
    <style>
        body { font-family: sans-serif; background-color: #f0f2f5; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .container { background: #fff; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); width: 90%; max-width: 400px; }
        h1 { color: #1877f2; text-align: center; margin-bottom: 20px; }
        input { width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 6px; margin-bottom: 15px; box-sizing: border-box; }
        input[type="submit"] { background-color: #1877f2; color: white; font-weight: bold; cursor: pointer; }
        .result { padding: 15px; margin-top: 20px; border-radius: 6px; word-wrap: break-word; }
        .success { background: #e7f3ff; border: 1px solid #1877f2; }
        .error { background: #ffebe8; border: 1px solid #dd3c1e; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Simple Token Generator</h1>
        <form method="post">
            <input type="text" name="username" placeholder="Email ya Username" required>
            <input type="password" name="password" placeholder="Asli Password" required>
            <input type="submit" value="Generate Token">
        </form>
        {% if result %}
            <div class="result {% if 'Error' in result %}error{% else %}success{% endif %}">
                <strong>Result:</strong><br>{{ result }}
            </div>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def home():
    result = ""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        result = get_simple_token(username, password)
    return render_template_string(HTML_TEMPLATE, result=result)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
