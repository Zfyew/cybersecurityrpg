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
    hard_mode = player.get('run', 1) > 1
    ai_mode = request.args.get('ai_mode') == 'true'
    api_key = request.args.get('api_key', '')

    # if AI mode, fetch a generated scenario
    if ai_mode and api_key:
        import urllib.request
        import json as json_lib

        prompts = {
    'password': f"""You are generating content for a cybersecurity training game. 
Create a password strength challenge for run number {player.get('run', 1)}.

Rules:
- Generate exactly 6 passwords
- 3 must be weak, 3 must be strong
- Weak passwords: common words, keyboard patterns, names with numbers, dictionary words, short length
- Strong passwords: 12+ chars, mix of uppercase/lowercase/numbers/symbols, no dictionary words
- Do NOT use password123, qwerty, 123456 or other overused examples — be creative and realistic
- Vary difficulty based on run {player.get('run', 1)} — higher runs should have more subtle weak passwords
- Strong passwords should look like real generated passwords, not textbook examples

Return ONLY this JSON, no markdown, no explanation:
{{"passwords": [{{"password": "example", "weak": true}}]}}""",

    'port': f"""You are generating content for a cybersecurity training game.
Create a port scanning scenario for run number {player.get('run', 1)}.

Rules:
- Use a realistic enterprise network scenario
- Mix genuine threats with false positives across runs
- Higher run numbers ({player.get('run', 1)}) should use more subtle or ambiguous cases
- Avoid overused examples like port 23 Telnet or port 3389 RDP on early runs
- Consider: unusual high ports, database ports, management interfaces, legacy protocols
- The reason must explain the real-world security implication clearly in one sentence

Return ONLY this JSON, no markdown, no explanation:
{{"port": 8080, "service": "HTTP-Alt", "threat": true, "reason": "one sentence"}}""",

    'logs': f"""You are generating content for a cybersecurity training game.
Create a log analysis challenge for run number {player.get('run', 1)}.

Rules:
- Generate exactly 3 log entries, exactly one must be suspicious
- Use realistic enterprise log format with timestamps, event types, usernames, IPs
- Run {player.get('run', 1)} difficulty: {'easy — obvious indicators like TOR nodes or brute force' if player.get('run', 1) == 1 else 'medium — subtler indicators like impossible travel or off-hours access' if player.get('run', 1) == 2 else 'hard — very subtle indicators requiring careful analysis'}
- The suspicious entry should reflect a real attack technique: credential stuffing, lateral movement, data exfiltration, privilege escalation, impossible travel, brute force, insider threat
- Normal entries must look completely legitimate
- answer is the zero-based index of the suspicious entry

Return ONLY this JSON, no markdown, no explanation:
{{"logs": ["log1", "log2", "log3"], "answer": 1, "reason": "one sentence explanation of the attack technique"}}"""
}

        try:
            payload = json_lib.dumps({
                "model": "claude-sonnet-4-6",
                "max_tokens": 500,
                "messages": [{"role": "user", "content": prompts[level_type]}]
            }).encode()

            req = urllib.request.Request(
                'https://api.anthropic.com/v1/messages',
                data=payload,
                headers={
                    'Content-Type': 'application/json',
                    'x-api-key': api_key,
                    'anthropic-version': '2023-06-01'
                }
            )

            with urllib.request.urlopen(req) as response:
                result = json_lib.loads(response.read())
                text = result['content'][0]['text'].strip()
                if text.startswith('```'):
                    text = text.split('```')[1]
                    if text.startswith('json'):
                        text = text[4:]
                ai_data = json_lib.loads(text.strip())

                if level_type == 'password':
                    return jsonify({
                        'type': 'password',
                        'title': LEVELS[level_num]['title'],
                        'description': LEVELS[level_num]['description'],
                        'passwords': ai_data['passwords'],
                        'hard_mode': hard_mode,
                        'ai_generated': True
                    })
                elif level_type == 'port':
                    session['current_scenario'] = ai_data
                    return jsonify({
                        'type': 'port',
                        'title': LEVELS[level_num]['title'],
                        'description': LEVELS[level_num]['description'],
                        'port': ai_data['port'],
                        'service': ai_data['service'],
                        'hard_mode': hard_mode,
                        'ai_generated': True
                    })
                elif level_type == 'logs':
                    session['current_logs'] = ai_data
                    return jsonify({
                        'type': 'logs',
                        'title': LEVELS[level_num]['title'],
                        'description': LEVELS[level_num]['description'],
                        'logs': ai_data['logs'],
                        'hard_mode': hard_mode,
                        'ai_generated': True
                    })
        except Exception:
            # fall back to static if AI call fails
            pass

    # static fallback
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

@app.route('/api/ai_hint', methods=['POST'])
def ai_hint():
    data = request.json
    context = data.get('context', '')
    key = data.get('api_key', '')
    model = data.get('model', 'claude-sonnet-4-6')

    if not key:
        return jsonify({'hint': 'No API key provided.'})

    try:
        import urllib.request
        import json as json_lib

        payload = json_lib.dumps({
            "model": model,
            "max_tokens": 150,
            "messages": [
                {
                    "role": "user",
                    "content": f"""You are a cybersecurity mentor in a training game. 
{context} 
Give a practical 2 sentence hint that references real-world security practice. 
Do not reveal the answer directly. Be specific, not generic."""
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


@app.route('/api/ai_feedback', methods=['POST'])
def ai_feedback():
    data = request.json
    key = data.get('api_key', '')
    model = data.get('model', 'claude-sonnet-4-6')
    correct = data.get('correct')
    context = data.get('context', '')

    if not key:
        return jsonify({'feedback': ''})

    outcome = "correctly identified" if correct else "incorrectly assessed"
    prompt = f"""You are a cybersecurity trainer. A player {outcome} this scenario: {context}
Give exactly one sentence of feedback that connects this to a real-world attack or defence technique.
Be specific and technical, not generic. Reference actual tools, frameworks or incidents where relevant."""

    try:
        import urllib.request
        import json as json_lib

        payload = json_lib.dumps({
            "model": model,
            "max_tokens": 120,
            "messages": [{"role": "user", "content": prompt}]
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
            return jsonify({'feedback': result['content'][0]['text'].strip()})

    except Exception as e:
        return jsonify({'feedback': ''})
    
@app.route('/api/ai_scenario', methods=['POST'])
def ai_scenario():
    data = request.json
    key = data.get('api_key', '')
    level_type = data.get('type', '')

    if not key:
        return jsonify({'error': 'No API key'})

    prompts = {
        'password': """Generate a cybersecurity training scenario about password strength. 
Return ONLY valid JSON in this exact format, nothing else:
{
  "passwords": [
    {"password": "example1", "weak": true},
    {"password": "example2", "weak": false},
    {"password": "example3", "weak": true},
    {"password": "example4", "weak": false},
    {"password": "example5", "weak": true},
    {"password": "example6", "weak": false}
  ]
}
Mix weak passwords (short, common words, simple patterns) with strong ones (long, random, mixed characters). Make them realistic.""",

        'port': """Generate a cybersecurity training scenario about a suspicious network port.
Return ONLY valid JSON in this exact format, nothing else:
{
  "port": 8080,
  "service": "HTTP-Alt",
  "threat": true,
  "reason": "Explanation of why this is or isn't a threat in one sentence."
}
Use realistic port numbers and services. Vary between genuine threats and false positives.""",

        'logs': """Generate a cybersecurity training scenario with 3 server log entries, one showing suspicious activity.
Return ONLY valid JSON in this exact format, nothing else:
{
  "logs": [
    "timestamp  event.type  user@corp.com  IP: x.x.x.x  STATUS  optional_detail",
    "timestamp  event.type  user@corp.com  IP: x.x.x.x  STATUS  optional_detail",
    "timestamp  event.type  user@corp.com  IP: x.x.x.x  STATUS  optional_detail"
  ],
  "answer": 1,
  "reason": "Explanation of why this log entry is suspicious in one sentence."
}
Use realistic timestamps and IPs. The answer field is the zero-based index of the suspicious log."""
    }

    prompt = prompts.get(level_type)
    if not prompt:
        return jsonify({'error': 'Unknown level type'})

    try:
        import urllib.request
        import json as json_lib

        payload = json_lib.dumps({
            "model": "claude-sonnet-4-6",
            "max_tokens": 500,
            "messages": [{"role": "user", "content": prompt}]
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
            text = result['content'][0]['text'].strip()
            # strip markdown code fences if Claude wraps it
            if text.startswith('```'):
                text = text.split('```')[1]
                if text.startswith('json'):
                    text = text[4:]
            scenario = json_lib.loads(text.strip())
            return jsonify({'scenario': scenario})

    except Exception as e:
        return jsonify({'error': str(e)})
    
if __name__ == '__main__':
    app.run(debug=True)