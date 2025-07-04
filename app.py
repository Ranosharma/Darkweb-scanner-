# app.py (Enhanced with User Login + Threat Dashboard + Sample Threats + Help Section)

from flask import Flask, jsonify, request, render_template_string, redirect, session, url_for
from datetime import datetime
import random

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Sample users
USERS = {"admin": "password123"}

# 50+ realistic fake threats
SAMPLE_THREATS = [
    {"site": f"threatportal{i}.onion", "type": random.choice([
        "Credential Leak", "Malware Sale", "Credit Card Dump", "DDoS Service", "Exploit Kit", "Phishing Kit", "Ransomware", "Payment Fraud"
    ]), "description": random.choice([
        "Leaked Netflix credentials", "Selling banking trojan", "Fullz + SSN for sale", "Targeted phishing template", "Stolen Paytm account dump",
        "Dump of Indian user credit cards", "Fake e-commerce payment gateway code", "Google Workspace compromise script",
        "New version of Emotet malware", "Crypto wallet brute-force tool"
    ]), "date": f"2025-06-{random.randint(1,30):02d}"} for i in range(1, 51)
]

LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Login - DarkWeb Scanner</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body style="background-color:#0f172a; color:#fff;">
  <div class="container mt-5">
    <h2 class="mb-4">🔐 Login to DarkWeb Scanner</h2>
    <form method="POST" action="/login">
      <div class="mb-3">
        <label class="form-label">Username</label>
        <input type="text" class="form-control" name="username" required>
      </div>
      <div class="mb-3">
        <label class="form-label">Password</label>
        <input type="password" class="form-control" name="password" required>
      </div>
      <button type="submit" class="btn btn-primary">Login</button>
    </form>
  </div>
</body>
</html>
'''

DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>DarkWeb Scanner</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
  <style>
    body {
      background-color: #0f172a;
      color: #e2e8f0;
      padding: 40px;
      font-family: 'Segoe UI', sans-serif;
    }
    .container {
      background-color: #1e293b;
      padding: 30px;
      border-radius: 15px;
    }
    .btn-primary {
      background-color: #2563eb;
      border: none;
    }
    .btn-primary:hover {
      background-color: #1d4ed8;
    }
    input {
      background-color: #334155;
      color: white;
      border: 1px solid #475569;
    }
    .faq {
      margin-top: 50px;
    }
  </style>
</head>
<body>
  <div class="container">
    <h1 class="mb-4">🕵️‍♂️ DarkWeb Scanner Dashboard</h1>
    <a href="/logout" class="btn btn-danger mb-4">Logout</a>

    <input type="text" id="search" class="form-control mb-3" placeholder="Search threats (e.g. payment fraud, malware)...">

    <table class="table table-dark table-striped">
      <thead>
        <tr>
          <th>Onion Site</th>
          <th>Type</th>
          <th>Description</th>
          <th>Date</th>
        </tr>
      </thead>
      <tbody id="threatTable"></tbody>
    </table>

    <hr class="my-4">

    <h3>Add New Threat</h3>
    <div class="row g-3">
      <div class="col-md-4">
        <input type="text" id="site" class="form-control" placeholder="Onion site">
      </div>
      <div class="col-md-4">
        <input type="text" id="type" class="form-control" placeholder="Threat type">
      </div>
      <div class="col-md-4">
        <input type="text" id="description" class="form-control" placeholder="Description">
      </div>
    </div>
    <div class="mt-3">
      <button class="btn btn-primary" onclick="addThreat()">➕ Add Threat</button>
    </div>

    <div class="faq">
      <h4 class="mt-5">📌 Common Questions</h4>
      <ul>
        <li>🔍 What is Payment Fraud?</li>
        <li>📅 How frequently are dark web threats updated?</li>
        <li>💡 Can users contribute to the threat list?</li>
        <li>🧠 How are threats categorized?</li>
        <li>🚨 What is the most reported threat this month?</li>
      </ul>
    </div>
  </div>

  <script>
    function loadThreats(query = '') {
      fetch(`/api/threats?query=${query}`)
        .then(res => res.json())
        .then(data => {
          const table = document.getElementById('threatTable');
          table.innerHTML = '';
          data.forEach(threat => {
            table.innerHTML += `
              <tr>
                <td>${threat.site}</td>
                <td>${threat.type}</td>
                <td>${threat.description}</td>
                <td>${threat.date}</td>
              </tr>
            `;
          });
        });
    }

    function addThreat() {
      const site = document.getElementById('site').value;
      const type = document.getElementById('type').value;
      const description = document.getElementById('description').value;

      fetch('/api/threats', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ site, type, description })
      }).then(() => {
        loadThreats();
        document.getElementById('site').value = '';
        document.getElementById('type').value = '';
        document.getElementById('description').value = '';
      });
    }

    document.getElementById('search').addEventListener('input', e => loadThreats(e.target.value));
    loadThreats();
  </script>
</body>
</html>
'''

@app.route('/')
def index():
    if 'user' in session:
        return render_template_string(DASHBOARD_TEMPLATE)
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in USERS and USERS[username] == password:
            session['user'] = username
            return redirect('/')
        else:
            return "<h3 style='color:red'>Invalid credentials. <a href='/login'>Try again</a></h3>"
    return render_template_string(LOGIN_TEMPLATE)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')

@app.route('/api/threats', methods=['GET'])
def get_threats():
    query = request.args.get('query')
    if query:
        filtered = [t for t in SAMPLE_THREATS if query.lower() in t['description'].lower() or query.lower() in t['type'].lower()]
        return jsonify(filtered)
    return jsonify(SAMPLE_THREATS)

@app.route('/api/threats', methods=['POST'])
def add_threat():
    data = request.json
    data['date'] = datetime.now().strftime('%Y-%m-%d')
    SAMPLE_THREATS.append(data)
    return jsonify({"message": "Threat added successfully"}), 201

if __name__ == '__main__':
    app.run(debug=True)
