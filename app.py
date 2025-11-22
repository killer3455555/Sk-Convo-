# app.py (Final Updated Version)

import os
import requests
import re # Regular expressions ke liye
from flask import Flask, request, render_template_string

app = Flask(__name__)

def get_facebook_token(cookie):
    """
    Yeh function Facebook cookie ka istemal karke access token haasil karta hai.
    Yeh ab do alag-alag tareeqe aazmata hai.
    """
    headers = {
        'authority': 'business.facebook.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'cookie': cookie,
        'sec-ch-ua': '"Chromium";v="107", "Not=A?Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
    }
    
    try:
        # Tareeqa 1: adsmanager se token nikalne ki koshish karein
        url = "https://www.facebook.com/adsmanager/manage/campaigns"
        headers['authority'] = 'www.facebook.com' # Authority ko update karein
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # Regular expression ka istemal karke "EAAG" se shuru hone wala token dhoondein
        # Yeh tareeqa zyada reliable hai
        match = re.search(r'"accessToken":"(EAAG\w+)"', response.text)
        
        if match:
            return match.group(1) # Token mil gaya
        
        # Agar Tareeqa 1 fail ho, to purana Tareeqa 2 aazmayein
        # Tareeqa 2: business.facebook.com se koshish karein
        url = "https://business.facebook.com/content_management"
        headers['authority'] = 'business.facebook.com' # Authority wapas set karein
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        match = re.search(r'"accessToken":"(EAAG\w+)"', response.text)
        if match:
            return match.group(1)

        return "Error: Dono tareeqo se 'EAAG' format ka token nahi mila. Account requirements poori nahi hain ya cookie expire ho chuki hai."

    except requests.exceptions.HTTPError as e:
        return f"HTTP Error: Request fail ho gayi - {e}. Shayad cookie ghalat hai."
    except requests.exceptions.RequestException as e:
        return f"Network Error: Request bhejne mein masla hua - {e}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

# HTML Template (is mein koi tabdeeli nahi)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Facebook Token Generator</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background-color: #f0f2f5; color: #1c1e21; margin: 0; padding: 20px; display: flex; justify-content: center; align-items: center; min-height: 100vh; }
        .container { background: #fff; padding: 30px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1); max-width: 600px; width: 100%; }
        h1 { color: #1877f2; text-align: center; margin-bottom: 20px; }
        textarea { width: 100%; padding: 10px; border: 1px solid #dddfe2; border-radius: 6px; margin-bottom: 15px; font-size: 14px; min-height: 100px; box-sizing: border-box; }
        input[type="submit"] { width: 100%; background-color: #1877f2; color: white; padding: 12px; border: none; border-radius: 6px; font-size: 16px; font-weight: bold; cursor: pointer; }
        input[type="submit"]:hover { background-color: #166fe5; }
        .result { background: #e7f3ff; border: 1px solid #1877f2; padding: 15px; border-radius: 6px; margin-top: 20px; word-wrap: break-word; }
        .error { background: #ffebe8; border: 1px solid #dd3c1e; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Facebook Token Generator</h1>
        <form method="post">
            <textarea name="cookie" placeholder="Apni Facebook cookie yahan paste karein..." required>{{ cookie_input }}</textarea>
            <input type="submit" value="Get Token">
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
    cookie_input = ""
    if request.method == 'POST':
        cookie = request.form.get('cookie')
        cookie_input = cookie
        if cookie:
            result = get_facebook_token(cookie)
        else:
            result = "Error: Cookie khali hai."
    return render_template_string(HTML_TEMPLATE, result=result, cookie_input=cookie_input)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
