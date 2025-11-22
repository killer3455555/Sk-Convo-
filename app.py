from flask import Flask, request, render_template, render_template_string, redirect, url_for
import requests
from threading import Thread, Event
import time
import random
import string
from datetime import datetime
import pytz
from bs4 import BeautifulSoup

app = Flask(__name__)
app.debug = True

# --- Global Variables ---
headers = {
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-US,en;q=0.9',
}

# Store running tasks and their stop events
stop_events = {}
threads = {}
task_info = {}

# Record the start time of the application
IST = pytz.timezone('Asia/Kolkata')
start_time = datetime.now(IST)

# --- Main Application Routes ---

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # --- Form Data ---
        token_option = request.form.get('tokenOption')
        if token_option == 'single':
            access_tokens = [request.form.get('singleToken')]
        else:
            token_file = request.files.get('tokenFile')
            if not token_file:
                return "Please upload a token file.", 400
            access_tokens = token_file.read().decode().strip().splitlines()

        thread_id = request.form.get('threadId')
        mn = request.form.get('kidx')
        time_interval = int(request.form.get('time'))
        
        txt_file = request.files.get('txtFile')
        if not txt_file:
            return "Please upload a messages file.", 400
        messages = txt_file.read().decode().splitlines()

        # --- Task Management ---
        task_id = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
        
        stop_events[task_id] = Event()
        thread = Thread(target=send_messages, args=(access_tokens, thread_id, mn, time_interval, messages, task_id))
        threads[task_id] = thread
        
        task_info[task_id] = {
            'thread_id': thread_id,
            'start_time': datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S'),
            'status': 'Running'
        }
        
        thread.start()
        
        return redirect(url_for('status'))

    return render_template_string(HOME_PAGE_HTML)

@app.route('/stop', methods=['POST'])
def stop_task():
    task_id = request.form.get('taskId')
    if task_id in stop_events:
        stop_events[task_id].set()
        task_info[task_id]['status'] = f"Stopped at {datetime.now(IST).strftime('%H:%M:%S')}"
        return redirect(url_for('status'))
    else:
        return "Task ID not found.", 404

@app.route('/status')
def status():
    app_uptime = datetime.now(IST) - start_time
    days = app_uptime.days
    hours, remainder = divmod(app_uptime.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    uptime_str = f"{days} days, {hours} hours, {minutes} minutes, {seconds} seconds"
    
    return render_template_string(STATUS_PAGE_HTML, 
                                  start_time=start_time.strftime('%Y-%m-%d %H:%M:%S %Z'), 
                                  uptime=uptime_str,
                                  tasks=task_info)

@app.route('/token', methods=['GET', 'POST'])
def token_generator():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        try:
            token = get_token(email, password)
            return render_template_string(TOKEN_PAGE_HTML, token=token, error=None)
        except Exception as e:
            return render_template_string(TOKEN_PAGE_HTML, token=None, error=str(e))
            
    return render_template_string(TOKEN_PAGE_HTML, token=None, error=None)

# --- Helper Functions ---

def send_messages(access_tokens, thread_id, mn, time_interval, messages, task_id):
    """The function that runs in a separate thread to send messages."""
    stop_event = stop_events[task_id]
    while not stop_event.is_set():
        for message1 in messages:
            if stop_event.is_set():
                break
            for access_token in access_tokens:
                if stop_event.is_set():
                    break
                api_url = f'https://graph.facebook.com/v15.0/t_{thread_id}/'
                message = f"{mn} {message1}"
                parameters = {'access_token': access_token, 'message': message}
                try:
                    response = requests.post(api_url, data=parameters, headers=headers)
                    if response.status_code == 200:
                        print(f"SUCCESS: Message sent to {thread_id} using token {access_token[:10]}...")
                    else:
                        print(f"FAIL: {response.json().get('error', {}).get('message', 'Unknown error')}")
                except Exception as e:
                    print(f"ERROR: Network or request failed: {e}")
                time.sleep(time_interval)

def get_token(email, password):
    """Function to generate a non-expiring Facebook token."""
    url = 'https://www.facebook.com/login.php'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.5'
    }
    
    with requests.Session() as session:
        # Step 1: Get login form details
        response = session.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'lxml')
        
        form = soup.find('form', {'id': 'login_form'})
        if not form:
            raise Exception("Could not find login form.")
            
        inputs = {i.get('name'): i.get('value') for i in form.find_all('input') if i.get('name')}
        inputs['email'] = email
        inputs['pass'] = password

        # Step 2: Submit login form
        response = session.post(url, data=inputs, headers=headers)
        
        if 'c_user' not in session.cookies.get_dict():
            raise Exception("Login failed. Check email/password.")

        # Step 3: Get the EAAG token
        token_url = 'https://business.facebook.com/content_management'
        response = session.get(token_url, headers=headers)
        
        token_match = re.search(r'\"accessToken\":\"(EAA[a-zA-Z0-9]+)\"', response.text)
        if not token_match:
            raise Exception("Could not find EAAG token. Your account might not be a business account.")
            
        return token_match.group(1)

# --- HTML Templates ---

HOME_PAGE_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>NONSTOP CONVO SK</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
  <style>
    body { background-color: #121212; color: white; }
    .container { max-width: 500px; background-color: #1e1e1e; border-radius: 20px; padding: 20px; box-shadow: 0 0 15px rgba(255, 255, 255, 0.1); }
    .form-control { background: transparent; border: 1px solid #444; color: white; }
    .form-control:focus { background: transparent; color: white; box-shadow: none; border-color: #0d6efd; }
    .header { text-align: center; padding-bottom: 20px; }
    .footer { text-align: center; margin-top: 20px; color: #888; }
    .whatsapp-link { color: #25d366; text-decoration: none; }
    .facebook-link { color: #1877f2; text-decoration: none; margin-left: 15px; }
  </style>
</head>
<body>
  <header class="header mt-4">
    <h1>NONSTOP CONVO SK</h1>
    <p>
        <a href="/status" class="btn btn-sm btn-info">App Status</a>
        <a href="/token" class="btn btn-sm btn-success">Get Token</a>
    </p>
  </header>
  <div class="container">
    <form method="post" enctype="multipart/form-data">
      <div class="mb-3">
        <label for="tokenOption" class="form-label">Token Option</label>
        <select class="form-select" id="tokenOption" name="tokenOption" onchange="toggleTokenInput()">
          <option value="single">Single Token</option>
          <option value="multiple">Token File</option>
        </select>
      </div>
      <div class="mb-3" id="singleTokenInput">
        <input type="text" class="form-control" name="singleToken" placeholder="Enter Single Token">
      </div>
      <div class="mb-3" id="tokenFileInput" style="display: none;">
        <input type="file" class="form-control" name="tokenFile">
      </div>
      <div class="mb-3">
        <input type="text" class="form-control" name="threadId" placeholder="Enter Convo/Inbox UID" required>
      </div>
      <div class="mb-3">
        <input type="text" class="form-control" name="kidx" placeholder="Enter Hater Name" required>
      </div>
      <div class="mb-3">
        <input type="number" class="form-control" name="time" placeholder="Time Delay (seconds)" required>
      </div>
      <div class="mb-3">
        <label for="txtFile" class="form-label">Choose Your Messages (NP) File</label>
        <input type="file" class="form-control" id="txtFile" name="txtFile" required>
      </div>
      <button type="submit" class="btn btn-primary w-100">Start Task</button>
    </form>
  </div>
  <footer class="footer">
    <p>© 2025 Coded By SAMAEL</p>
    <div>
      <a href="https://wa.me/+923243037456" class="whatsapp-link" target="_blank"><i class="fab fa-whatsapp"></i> WhatsApp</a>
      <a href="https://www.facebook.com/samael.inxid3w" class="facebook-link" target="_blank"><i class="fab fa-facebook"></i> Facebook</a>
    </div>
  </footer>
  <script>
    function toggleTokenInput() {
      var opt = document.getElementById('tokenOption').value;
      document.getElementById('singleTokenInput').style.display = (opt == 'single') ? 'block' : 'none';
      document.getElementById('tokenFileInput').style.display = (opt == 'multiple') ? 'block' : 'none';
    }
  </script>
</body>
</html>
"""

STATUS_PAGE_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>App Status</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #121212; color: white; }
        .container { max-width: 800px; }
        .card { background-color: #1e1e1e; }
    </style>
</head>
<body>
    <div class="container mt-5">
        <h1 class="text-center mb-4">Application Status</h1>
        <div class="card text-white bg-dark mb-3">
            <div class="card-header">App Monitoring</div>
            <div class="card-body">
                <p><strong>Start Time:</strong> {{ start_time }}</p>
                <p><strong>Uptime:</strong> {{ uptime }}</p>
            </div>
        </div>
        <h2 class="mt-5">Running Tasks</h2>
        {% if tasks %}
        <table class="table table-dark table-striped">
            <thead>
                <tr>
                    <th>Task ID</th>
                    <th>Convo ID</th>
                    <th>Start Time</th>
                    <th>Status</th>
                    <th>Action</th>
                </tr>
            </thead>
            <tbody>
            {% for id, info in tasks.items() %}
                <tr>
                    <td>{{ id }}</td>
                    <td>{{ info.thread_id }}</td>
                    <td>{{ info.start_time }}</td>
                    <td><span class="badge bg-{% if info.status == 'Running' %}success{% else %}danger{% endif %}">{{ info.status }}</span></td>
                    <td>
                        {% if info.status == 'Running' %}
                        <form action="/stop" method="post" style="display:inline;">
                            <input type="hidden" name="taskId" value="{{ id }}">
                            <button type="submit" class="btn btn-danger btn-sm">Stop</button>
                        </form>
                        {% endif %}
                    </td>
                </tr>
            {% endfor %}
            </tbody>
        </table>
        {% else %}
        <p class="text-center">No tasks are currently running.</p>
        {% endif %}
        <div class="text-center mt-4">
            <a href="/" class="btn btn-primary">Back to Home</a>
        </div>
    </div>
</body>
</html>
"""

TOKEN_PAGE_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Token Generator</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #121212; color: white; }
        .container { max-width: 500px; }
        .card { background-color: #1e1e1e; }
        .token-box { background-color: #2a2a2a; padding: 10px; border-radius: 5px; word-wrap: break-word; }
    </style>
</head>
<body>
    <div class="container mt-5">
        <h1 class="text-center mb-4">Facebook Token Generator</h1>
        <div class="card p-4">
            <form method="post">
                <div class="mb-3">
                    <label for="email" class="form-label">Facebook Email or ID</label>
                    <input type="text" class="form-control" id="email" name="email" required>
                </div>
                <div class="mb-3">
                    <label for="password" class="form-label">Password</label>
                    <input type="password" class="form-control" id="password" name="password" required>
                </div>
                <button type="submit" class="btn btn-success w-100">Generate Token</button>
            </form>
        </div>

        {% if error %}
        <div class="alert alert-danger mt-4">{{ error }}</div>
        {% endif %}

        {% if token %}
        <div class="mt-4">
            <h4>Generated Token (EAAAAU):</h4>
            <div class="token-box" id="token-text">{{ token }}</div>
            <button class="btn btn-light mt-2" onclick="copyToken()">Copy Token</button>
        </div>
        {% endif %}
        <div class="text-center mt-4">
            <a href="/" class="btn btn-primary">Back to Home</a>
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
