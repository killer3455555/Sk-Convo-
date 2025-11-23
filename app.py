# app.py (Final Version for Monokai-Style Token)

import os
import requests
import hashlib
from flask import Flask, request, render_template_string

app = Flask(__name__)

def get_android_token(username, password):
    """
    Facebook Android App ki API ka istemal karke User Access Token haasil karta hai.
    """
    # Yeh values Facebook Android App ki pehchan hain. Inko na badlein.
    api_key = "882a8490361da98702bf97a021ddc14d"
    secret = "62f8ce9f74b12f84c123cc23437a4a32"
    
    params = {
        'api_key': api_key,
        'credentials_type': 'password',
        'email': username,
        'format': 'JSON',
        'generate_machine_id': '1',
        'generate_session_cookies': '1',
        'locale': 'en_US',
        'method': 'auth.login',
        'password': password,
        'return_ssl_resources': '0',
        'v': '1.0'
    }

    # Signature generate karna (Facebook ki security ke liye zaroori)
    sig_string = "".join([f"{key}={value}" for key, value in sorted(params.items())])
    sig_string += secret
    params['sig'] = hashlib.md5(sig_string.encode('utf-8')).hexdigest()

    api_url = 'https://api.facebook.com/restserver.php'
    
    headers = {
        'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 12; SM-G988N Build/SP1A.210812.016) [FBAN/FB4A;FBAV/353.0.0.28.118;FBBV/343324868;FBDM/{density=3.0,width=1080,height=2196};FBLC/en_US;FBRV/344639944;FBCR/KT;FBMF/samsung;FBBD/samsung;FBPN/com.facebook.katana;FBDV/SM-G988N;FBSV/12;FBOP/1;FBCA/arm64-v8a:;]'
    }

    try:
        response = requests.post(api_url, data=params, headers=headers, timeout=15)
        response_data = response.json()

        if 'access_token' in response_data:
            return response_data['access_token']
        elif 'error_msg' in response_data:
            return f"Error: {response_data['error_msg']}"
        else:
            return f"Error: Ek anjana error hua. Response: {response_data}"

    except requests.exceptions.RequestException as e:
        return f"Network Error: Request fail ho gayi - {e}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

# HTML Template jo browser mein dikhega
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Monokai-Style Token Generator</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background-color: #f0f2f5; color: #1c1e21; margin: 0; padding: 20px; display: flex; justify-content: center; align-items: center; min-height: 100vh; }
        .container { background: #fff; padding: 30px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1); max-width: 500px; width: 100%; }
        h1 { color: #1877f2; text-align: center; margin-bottom: 10px; }
        p { text-align: center; color: #606770; margin-top: 0; margin-bottom: 20px; }
        input[type="text"], input[type="password"] { width: 100%; padding: 12px; border: 1px solid #dddfe2; border-radius: 6px; margin-bottom: 15px; font-size: 16px; box-sizing: border-box; }
        input[type="submit"] { width: 100%; background-color: #1877f2; color: white; padding: 12px; border: none; border-radius: 6px; font-size: 16px; font-weight: bold; cursor: pointer; }
        input[type="submit"]:hover { background-color: #166fe5; }
        .result { background: #e7f3ff; border: 1px solid #1877f2; padding: 15px; border-radius: 6px; margin-top: 20px; word-wrap: break-word; font-family: 'Courier New', Courier, monospace; }
        .error { background: #ffebe8; border: 1px solid #dd3c1e; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Monokai-Style Token Generator</h1>
        <p>Apna Facebook username aur password daal kar powerful token haasil karein.</p>
        <form method="post">
            <input type="text" name="username" placeholder="Email ya Username" required>
            <input type="password" name="password" placeholder="Password" required>
            <input type="submit" value="Generate Token">
        </form>
        {% if result %}
            <div class="result {% if 'Error' in result %}error{% endif %}">
                <strong>Result:</strong><br>
                {{ result }}
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
        if username and password:
            result = get_android_token(username, password)
        else:
            result = "Error: Username aur Password dono zaroori hain."
    return render_template_string(HTML_TEMPLATE, result=result)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
