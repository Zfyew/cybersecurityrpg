# Flask server — handles game state and routes
from flask import Flask, render_template, request, jsonify, session
import random
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# all game data lives here
LEVELS = {
    1: {
        'title': 'Password Cracking',
        'description': 'A user account has been flagged. Identify the weakest password before the attacker does.',
        'type': 'password'
    },
    2: {
        'title': 'Port Scanning',
        'description': 'An unknown device appeared on the network. Analyse the open port and decide whether to block it.',
        'type': 'port'
    },
    3: {
        'title': 'Breach Investigation',
        'description': 'Alerts are firing. Read the logs and identify which entry shows the attacker.',
        'type': 'logs'
    }
}

PASSWORDS = [
    {"password": "password123", "weak": True},
    {"password": "Tr0ub4dor&3", "weak": False},
    {"password": "qwerty", "weak": True},
    {"password": "xK#9mP2$vL8n", "weak": False},
    {"password": "123456", "weak": True},
    {"password": "C0rrect-Horse-Battery", "weak": False}
]

PORT_SCENARIOS = [
    {
        'port': 23, 'service': 'Telnet', 'threat': True,
        'reason': 'Telnet sends data in plain text. Should always be disabled.'
    },
    {
        'port': 443, 'service': 'HTTPS', 'threat': False,
        'reason': 'HTTPS is expected on a web server. Nothing suspicious here.'
    },
    {
        'port': 3389, 'service': 'RDP', 'threat': True,
        'reason': 'RDP exposed to the internet is a common attack vector.'
    }
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
        'inventory': []
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

    if level_type == 'password':
        return jsonify({
            'type': 'password',
            'title': LEVELS[level_num]['title'],
            'description': LEVELS[level_num]['description'],
            'passwords': PASSWORDS
        })
    elif level_type == 'port':
        scenario = random.choice(PORT_SCENARIOS)
        session['current_scenario'] = scenario
        return jsonify({
            'type': 'port',
            'title': LEVELS[level_num]['title'],
            'description': LEVELS[level_num]['description'],
            'port': scenario['port'],
            'service': scenario['service']
        })
    elif level_type == 'logs':
        log_set = random.choice(LOG_SETS)
        session['current_logs'] = log_set
        return jsonify({
            'type': 'logs',
            'title': LEVELS[level_num]['title'],
            'description': LEVELS[level_num]['description'],
            'logs': log_set['logs']
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

    # track which levels have already been scored
    if 'completed' not in player:
        player['completed'] = []

    if level == 1:
        if 0 <= ans < len(PASSWORDS):
            correct = PASSWORDS[ans]['weak']
            reason = f"'{PASSWORDS[ans]['password']}' is {'weak — short and common' if correct else 'actually a strong password'}."

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
        # only award points if this level hasn't been completed before
        points = level * 100 if level not in player['completed'] else 0
        player['score'] += points
        player['completed'].append(level) if level not in player['completed'] else None
        if level < 3:
            player['level'] = max(player['level'], level + 1)
        tools = {1: 'Wordlist Cracker', 2: 'Port Scanner', 3: 'Log Analyser'}
        if tools[level] not in player['inventory']:
            player['inventory'].append(tools[level])
        session['player'] = player
        return jsonify({
            'correct': True,
            'reason': reason,
            'points': points,
            'player': player
        })
    else:
        player['health'] -= 25
        session['player'] = player
        return jsonify({
            'correct': False,
            'reason': reason,
            'player': player
        })
    
@app.route('/api/ai_hint', methods=['POST'])
def ai_hint():
    data = request.json
    context = data.get('context', '')
    key = data.get('api_key', '')

    if not key:
        return jsonify({'hint': 'No API key provided.'})

    try:
        import urllib.request
        import json as json_lib

        payload = json_lib.dumps({
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 150,
            "messages": [
                {
                    "role": "user",
                    "content": f"You are a cybersecurity mentor in a training game. {context} Keep your hint to 2 sentences maximum. Do not give the answer away directly."
                }
            ]
        }).encode()

        req = urllib.request.Request(
            'https://api.anthropic.com/v1/messages',
            data=payload,
            headers={
                'Content-Type': 'application/json',
                'x-api-key': key,
                'anthropic-version': '2023-06-01'
            }
        )

        with urllib.request.urlopen(req) as response:
            result = json_lib.loads(response.read())
            hint = result['content'][0]['text']
            return jsonify({'hint': hint})

    except Exception as e:
        return jsonify({'hint': f'Could not reach Claude: {str(e)}'})   
    

if __name__ == '__main__':
    app.run(debug=True)