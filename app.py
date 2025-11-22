from flask import Flask, request, render_template_string
import requests
import re

# Flask app initialize karna
app = Flask(__name__)

# --- HTML Template (Web Page ka Design) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cookie to Token Generator</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #121212; color: white; display: flex; align-items: center; justify-content: center; min-height: 100vh; }
        .container { max-width: 600px; background-color: #1e1e1e; border-radius: 15px; padding: 30px; box-shadow: 0 0 20px rgba(0, 136, 255, 0.1); }
        textarea.form-control { background-color: #2a2a2a; border: 1px solid #444; color: white; height: 150px; }
        textarea.form-control:focus { background-color: #2a2a2a; color: white; box-shadow: none; border-color: #0088ff; }
        .btn-generate { background-color: #0088ff; border: none; color: white; font-weight: bold; }
        .btn-generate:hover { background-color: #006edc; }
        .token-box { background-color: #2a2a2a; padding: 15px; border-radius: 5px; word-wrap: break-word; margin-top: 20px; border: 1px dashed #444; }
        .footer { text-align: center; margin-top: 20px; color: #888; font-size: 0.9em; }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="text-center mb-4" style="color: #0088ff;">Cookie to Token Generator</h1>
        <p class="text-center text-muted">Apne Facebook account ki cookies paste karein aur non-expiring token haasil karein.</p>
        <form method="post">
            <div class="mb-3">
                <label for="cookie" class="form-label">Facebook Cookies</label>
                <textarea class="form-control" id="cookie" name="cookie" placeholder="Yahan apni cookies paste karein..." required></textarea>
            </div>
            <button type="submit" class="btn btn-generate w-100">Generate Non-Expiring Token</button>
        </form>

        {% if error %}
        <div class="alert alert-danger mt-4">{{ error }}</div>
        {% endif %}

        {% if token %}
        <div class="mt-4">
            <h5 style="color: #0088ff;">✅ Token (EAAAAU) Generated Successfully:</h5>
            <div class="token-box" id="token-text">{{ token }}</div>
            <button class="btn btn-secondary mt-2 w-100" onclick="copyToken()">Copy Token</button>
        </div>
        {% endif %}
        
        <div class="footer">
            <p>© 2025 | Non-Stop 24/7 Service</p>
        </div>
    </div>

    <script>
        function copyToken() {
            const tokenText = document.getElementById('token-text').innerText;
            navigator.clipboard.writeText(tokenText).then(() => {
                alert('Token copied to clipboard!');
            });
        }
    </script>
</body>
</html>
"""

# --- Token Banane ka Main Function ---
def get_token_from_cookie(cookie):
    """
    Yeh function Facebook cookies ka istemal karke non-expiring token haasil karta hai.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cookie': cookie  # Yahan user ki di hui cookie istemal hogi
    }
    
    try:
        # Business page se token nikalna
        business_url = 'https://business.facebook.com/content_management'
        res = requests.get(business_url, headers=headers, timeout=10)
        res.raise_for_status()
        
        # Page ke response mein se token dhoondna
        token_match = re.search(r'\"accessToken\":\"(EAA[a-zA-Z0-9]+)\"', res.text)
        
        if not token_match:
            raise Exception("Access token nahi mila. Aapki cookies galat, expire, ya invalid ho sakti hain. Ya phir aapka account business account nahi hai.")
            
        return token_match.group(1)

    except requests.exceptions.RequestException as e:
        raise Exception(f"Network mein masla hai: {e}")
    except Exception as e:
        raise e

# --- Web Routes (URL Handling) ---
@app.route("/", methods=["GET", "POST"])
def main_page():
    if request.method == "POST":
        cookie = request.form.get("cookie")
        token = None
        error = None
        
        if not cookie:
            error = "Cookies ka field khaali nahi ho sakta."
        else:
            try:
                token = get_token_from_cookie(cookie)
            except Exception as e:
                error = str(e)
        
        return render_template_string(HTML_TEMPLATE, token=token, error=error)
    
    return render_template_string(HTML_TEMPLATE)

# --- Script ko Chalane ke liye ---
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
