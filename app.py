# Flask server — handles game state, routing and scoring
from flask import Flask, render_template, request, jsonify, session
import random
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

LEVELS = {
    1: {'title': 'Password Cracking', 'description': 'A user account has been flagged. Identify the weakest password before the attacker does.', 'type': 'password'},
    2: {'title': 'Port Scanning', 'description': 'An unknown device appeared on the network. Analyse the open port and decide whether to block it.', 'type': 'port'},
    3: {'title': 'Breach Investigation', 'description': 'Alerts are firing. Read the logs and identify which entry shows the attacker.', 'type': 'logs'}
}

# easy and hard password sets — hard set unlocks after first completion
PASSWORDS_EASY = [
    {"password": "password123", "weak": True},
    {"password": "Tr0ub4dor&3", "weak": False},
    {"password": "qwerty", "weak": True},
    {"password": "xK#9mP2$vL8n", "weak": False},
    {"password": "123456", "weak": True},
    {"password": "C0rrect-Horse-Battery", "weak": False}
]

PASSWORDS_HARD = [
    {"password": "iloveyou2024", "weak": True},
    {"password": "9$kLm#2pXnW!", "weak": False},
    {"password": "letmein", "weak": True},
    {"password": "Vx7@qR3!mKp2", "weak": False},
    {"password": "monkey123", "weak": True},
    {"password": "Kj#8nP$2mLx9", "weak": False}
]

PORT_SCENARIOS = [
    {'port': 23, 'service': 'Telnet', 'threat': True, 'reason': 'Telnet sends data in plain text. Should always be disabled.'},
    {'port': 443, 'service': 'HTTPS', 'threat': False, 'reason': 'HTTPS is expected on a web server. Nothing suspicious here.'},
    {'port': 3389, 'service': 'RDP', 'threat': True, 'reason': 'RDP exposed to the internet is a common attack vector.'},
    {'port': 22, 'service': 'SSH', 'threat': False, 'reason': 'SSH is a secure protocol. Expected on a Linux server.'},
    {'port': 21, 'service': 'FTP', 'threat': True, 'reason': 'FTP transmits credentials in plain text. Should be replaced with SFTP.'},
    {'port': 1433, 'service': 'MSSQL', 'threat': True, 'reason': 'A database port exposed to the internet is a serious risk.'}
]

LOG_SETS = [
    {
        'logs': [
            "09:14:22  user.login  alice@corp.com  IP: 192.168.1.5  SUCCESS",
            "09:15:01  user.login  bob@corp.com  IP: 185.220.101.45  SUCCESS  (TOR exit node)",
            "09:16:44  file.access  charlie@corp.com  IP: 192.168.1.8  SUCCESS"
        ],
        'answer': 1,
        'reason': 'Login from a TOR exit node is a major red flag. Likely credential stuffing.'
    },
    {
        'logs': [
            "14:02:11  admin.login  sysadmin  IP: 10.0.0.1  SUCCESS",
            "14:03:55  file.download  sysadmin  IP: 10.0.0.1  200 files downloaded",
            "14:04:01  admin.login  sysadmin  IP: 203.0.113.99  SUCCESS  (outside business hours)"
        ],
        'answer': 2,
        'reason': 'Same account logged in from two different IPs within seconds — impossible without credential theft.'
    },
    {
        'logs': [
            "11:30:00  user.login  dave@corp.com  IP: 192.168.1.12  FAILED x5 then SUCCESS",
            "11:31:20  user.login  eve@corp.com  IP: 192.168.1.9  SUCCESS",
            "11:32:45  user.login  frank@corp.com  IP: 192.168.1.14  SUCCESS"
        ],
        'answer': 0,
        'reason': 'Five failed attempts followed by a success is a classic brute force pattern.'
    },
    {
        'logs': [
            "16:05:11  file.access  grace@corp.com  IP: 192.168.1.20  SUCCESS",
            "16:05:44  user.login  grace@corp.com  IP: 192.168.1.20  SUCCESS",
            "16:06:01  data.export  grace@corp.com  IP: 192.168.1.20  8500 records exported"
        ],
        'answer': 2,
        'reason': 'Exporting 8500 records in one go outside normal working patterns is a data exfiltration indicator.'
    }
]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/start', methods=['POST'])
def start():
    data = request.json
    session['player'] = {
        'name': data.get('name', 'Agent'),
        'health': 100,
        'score': 0,
        'level': 1,
        'inventory': [],
        'completed': [],
        'run': 1
    }
    return jsonify({'status': 'ok', 'player': session['player']})

@app.route('/api/state', methods=['GET'])
def state():
    player = session.get('player')
    if not player:
        return jsonify({'error': 'No active session'}), 400
    return jsonify({'player': player, 'levels': LEVELS})

@app.route('/api/level/<int:level_num>', methods=['GET'])
def get_level(level_num):
    player = session.get('player')
    if not player:
        return jsonify({'error': 'No session'}), 400
    if level_num > player['level']:
        return jsonify({'error': 'Level locked'}), 403

    level_type = LEVELS[level_num]['type']
    # use harder sets if player has completed a full run before
    hard_mode = player.get('run', 1) > 1

    if level_type == 'password':
        passwords = PASSWORDS_HARD if hard_mode else PASSWORDS_EASY
        return jsonify({
            'type': 'password',
            'title': LEVELS[level_num]['title'],
            'description': LEVELS[level_num]['description'],
            'passwords': passwords,
            'hard_mode': hard_mode
        })
    elif level_type == 'port':
        scenario = random.choice(PORT_SCENARIOS)
        session['current_scenario'] = scenario
        return jsonify({
            'type': 'port',
            'title': LEVELS[level_num]['title'],
            'description': LEVELS[level_num]['description'],
            'port': scenario['port'],
            'service': scenario['service'],
            'hard_mode': hard_mode
        })
    elif level_type == 'logs':
        log_set = random.choice(LOG_SETS)
        session['current_logs'] = log_set
        return jsonify({
            'type': 'logs',
            'title': LEVELS[level_num]['title'],
            'description': LEVELS[level_num]['description'],
            'logs': log_set['logs'],
            'hard_mode': hard_mode
        })

@app.route('/api/answer', methods=['POST'])
def answer():
    player = session.get('player')
    if not player:
        return jsonify({'error': 'No session'}), 400

    data = request.json
    level = data.get('level')
    ans = data.get('answer')
    correct = False
    reason = ''

    if 'completed' not in player:
        player['completed'] = []

    hard_mode = player.get('run', 1) > 1

    if level == 1:
        passwords = PASSWORDS_HARD if hard_mode else PASSWORDS_EASY
        if 0 <= ans < len(passwords):
            correct = passwords[ans]['weak']
            reason = f"'{passwords[ans]['password']}' is {'weak — short and common' if correct else 'actually a strong password'}."
    elif level == 2:
        scenario = session.get('current_scenario')
        if scenario:
            correct = (ans == scenario['threat'])
            reason = scenario['reason']
    elif level == 3:
        log_set = session.get('current_logs')
        if log_set:
            correct = (ans == log_set['answer'])
            reason = log_set['reason']

    if correct:
        # harder runs give more points
        base_points = level * 100
        points = int(base_points * 1.5) if hard_mode else base_points
        if level not in player['completed']:
            player['score'] += points
            player['completed'].append(level)
        else:
            points = 0

        if level < 3:
            player['level'] = max(player['level'], level + 1)

        tools = {1: 'Wordlist Cracker', 2: 'Port Scanner', 3: 'Log Analyser'}
        if tools[level] not in player['inventory']:
            player['inventory'].append(tools[level])

        # if all levels done, increment run counter and reset for next run
        if len(player['completed']) == 3:
            player['run'] = player.get('run', 1) + 1
            player['completed'] = []
            player['level'] = 1
            player['health'] = min(100, player['health'] + 20)

        session['player'] = player
        return jsonify({'correct': True, 'reason': reason, 'points': points, 'player': player})
    else:
        player['health'] -= 25 if not hard_mode else 35
        session['player'] = player
        return jsonify({'correct': False, 'reason': reason, 'player': player})

if __name__ == '__main__':
    app.run(debug=True)