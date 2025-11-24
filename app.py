import requests

def check_facebook_token(token):
    url = f"https://graph.facebook.com/me?access_token={token}"
    try:
        res = requests.get(url).json()
        if "error" in res:
            return f"❌ Token Invalid/Expired: {res['error']['message']}"
        else:
            return f"✅ Token Valid! User: {res.get('name', 'Unknown')}, ID: {res.get('id')}"
    except Exception as e:
        return f"⚠️ Error Occurred: {str(e)}"

# Example Use:
token = "YOUR_ACCESS_TOKEN_HERE"
print(check_facebook_token(token))
