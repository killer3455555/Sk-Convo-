import requests
import os
from datetime import datetime

# --- Configuration ---
TOKENS_FILE = 'tokens.txt'  # Jis file mein aapke tokens hain
WORKING_TOKENS_FILE = 'working_tokens.txt' # Yahan working tokens save honge
NOT_WORKING_TOKENS_FILE = 'not_working_tokens.txt' # Yahan bekaar tokens save honge

# Facebook Graph API endpoint
GRAPH_API_URL = 'https://graph.facebook.com/v18.0/me'

def check_token(token):
    """
    Yeh function ek token ko check karta hai ke woh valid hai ya nahi.
    """
    params = {
        'fields': 'id,name',
        'access_token': token
    }
    try:
        response = requests.get(GRAPH_API_URL, params=params, timeout=10)
        
        # Agar response 200 OK hai, to token theek hai
        if response.status_code == 200:
            user_data = response.json()
            return True, f"Working - ID: {user_data.get('id')}, Name: {user_data.get('name')}"
        # Agar response 4xx ya 5xx hai, to token mein masla hai
        else:
            error_data = response.json().get('error', {})
            error_message = error_data.get('message', 'Unknown error')
            return False, f"Not Working - Reason: {error_message}"
            
    except requests.exceptions.RequestException as e:
        return False, f"Not Working - Reason: Network Error ({e})"

def main():
    """
    Main function jo tokens file ko parhta hai aur har token ko check karta hai.
    """
    print("="*50)
    print("      Facebook Access Token Checker by Manus")
    print("="*50)
    
    # Check karein ke tokens.txt file mojood hai ya nahi
    if not os.path.exists(TOKENS_FILE):
        print(f"\n[ERROR] File not found: '{TOKENS_FILE}'")
        print("Please create a file named 'tokens.txt' and paste your tokens in it, one token per line.")
        return

    with open(TOKENS_FILE, 'r') as f:
        tokens = [line.strip() for line in f if line.strip()]

    if not tokens:
        print("\n[INFO] No tokens found in 'tokens.txt'. The file is empty.")
        return

    print(f"\nFound {len(tokens)} tokens. Starting check...\n")

    working_tokens = []
    not_working_tokens = []

    for i, token in enumerate(tokens, 1):
        is_working, message = check_token(token)
        print(f"[{i}/{len(tokens)}] {message}")
        
        if is_working:
            working_tokens.append(token)
        else:
            not_working_tokens.append(token)

    # Working tokens ko file mein save karein
    with open(WORKING_TOKENS_FILE, 'w') as f:
        for token in working_tokens:
            f.write(token + '\n')

    # Not working tokens ko file mein save karein
    with open(NOT_WORKING_TOKENS_FILE, 'w') as f:
        for token in not_working_tokens:
            f.write(token + '\n')

    print("\n" + "="*50)
    print("Check Complete!")
    print(f"Total Working Tokens: {len(working_tokens)}")
    print(f"Total Not Working Tokens: {len(not_working_tokens)}")
    print(f"\nWorking tokens have been saved to: '{WORKING_TOKENS_FILE}'")
    print(f"Not working tokens have been saved to: '{NOT_WORKING_TOKENS_FILE}'")
    print("="*50)


if __name__ == "__main__":
    main()
