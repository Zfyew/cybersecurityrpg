# Flask server — RPG game with Security+ certification integration
from flask import Flask, render_template, request, jsonify, session
import random
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data.rpg_scenarios import (
    PORT_SCENARIOS, LOG_SETS, PASSWORDS_EASY, PASSWORDS_HARD, DOMAIN_MAP
)
from data.security_plus import QUESTIONS, DOMAINS

app = Flask(__name__)
app.secret_key = os.urandom(24)

LEVELS = {
    1: {'title': 'Password Cracking', 'description': 'A user account has been flagged. Identify the weakest password before the attacker does.', 'type': 'password'},
    2: {'title': 'Port Scanning', 'description': 'An unknown device appeared on the network. Analyse the open port and decide whether to block it.', 'type': 'port'},
    3: {'title': 'Breach Investigation', 'description': 'Alerts are firing. Read the logs and identify which entry shows the attacker.', 'type': 'logs'}
}

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
        'run': 1,
        'domain_scores': {domain: {'correct': 0, 'attempted': 0} for domain in DOMAINS},
        'cert_progress': 0
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
    model = request.args.get('model', 'claude-sonnet-4-6')

    if ai_mode and api_key:
        try:
            import urllib.request
            import json as json_lib

            prompts = {
                'password': f"""You are generating content for a cybersecurity training game mapped to CompTIA Security+ SY0-701 exam objective 1.1.
Create a password strength challenge for run number {player.get('run', 1)}.
Rules:
- Generate exactly 6 passwords, 3 weak and 3 strong
- Weak: common words, keyboard patterns, names with numbers, dictionary words, short
- Strong: 12+ chars, mixed case, numbers, symbols, no dictionary words
- Do NOT use password123, qwerty, 123456 — be creative
- Run {player.get('run', 1)} difficulty — higher runs should have more subtle weak passwords
Return ONLY this JSON, nothing else:
{{"passwords": [{{"password": "example", "weak": true}}]}}""",

                'port': f"""You are generating content for a cybersecurity training game mapped to CompTIA Security+ SY0-701 exam objective 3.3.
Create a network port security scenario for run number {player.get('run', 1)}.
Rules:
- Use a realistic enterprise scenario
- Higher runs ({player.get('run', 1)}) should use more subtle or ambiguous cases
- Avoid overused examples like port 23 Telnet on early runs
- The reason must clearly explain the real-world security implication
Return ONLY this JSON, nothing else:
{{"port": 8080, "service": "HTTP-Alt", "threat": true, "reason": "one sentence"}}""",

                'logs': f"""You are generating content for a cybersecurity training game mapped to CompTIA Security+ SY0-701 exam objective 4.2.
Create a log analysis challenge for run number {player.get('run', 1)}.
Rules:
- Generate exactly 3 log entries, exactly one suspicious
- Difficulty for run {player.get('run', 1)}: {'easy — obvious indicators' if player.get('run', 1) == 1 else 'medium — subtler indicators like impossible travel or off-hours access' if player.get('run', 1) == 2 else 'hard — very subtle indicators'}
- Reflect real attack techniques: credential stuffing, lateral movement, data exfiltration, brute force
- answer is zero-based index of suspicious entry
Return ONLY this JSON, nothing else:
{{"logs": ["log1", "log2", "log3"], "answer": 1, "reason": "one sentence"}}"""
            }

            payload = json_lib.dumps({
                "model": model,
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
                        'ai_generated': True,
                        'domain_info': DOMAIN_MAP[level_num]
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
                        'ai_generated': True,
                        'domain_info': DOMAIN_MAP[level_num]
                    })
                elif level_type == 'logs':
                    session['current_logs'] = ai_data
                    return jsonify({
                        'type': 'logs',
                        'title': LEVELS[level_num]['title'],
                        'description': LEVELS[level_num]['description'],
                        'logs': ai_data['logs'],
                        'hard_mode': hard_mode,
                        'ai_generated': True,
                        'domain_info': DOMAIN_MAP[level_num]
                    })
        except Exception:
            pass

    # static fallback
    if level_type == 'password':
        from data.rpg_scenarios import get_random_passwords
        passwords = get_random_passwords(hard_mode)
        return jsonify({
            'type': 'password',
            'title': LEVELS[level_num]['title'],
            'description': LEVELS[level_num]['description'],
            'passwords': passwords,
            'hard_mode': hard_mode,
            'domain_info': DOMAIN_MAP[level_num]
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
            'hard_mode': hard_mode,
            'domain_info': DOMAIN_MAP[level_num]
        })
    elif level_type == 'logs':
        log_set = random.choice(LOG_SETS)
        session['current_logs'] = log_set
        return jsonify({
            'type': 'logs',
            'title': LEVELS[level_num]['title'],
            'description': LEVELS[level_num]['description'],
            'logs': log_set['logs'],
            'hard_mode': hard_mode,
            'domain_info': DOMAIN_MAP[level_num]
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

    # update domain score
    domain = DOMAIN_MAP.get(level, {}).get('domain', '')
    if domain and domain in player['domain_scores']:
        player['domain_scores'][domain]['attempted'] += 1
        if correct:
            player['domain_scores'][domain]['correct'] += 1

    if correct:
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

        if len(player['completed']) == 3:
            player['run'] = player.get('run', 1) + 1
            player['completed'] = []
            player['level'] = 1
            player['health'] = min(100, player['health'] + 20)

        session['player'] = player
        return jsonify({
            'correct': True,
            'reason': reason,
            'points': points,
            'player': player,
            'domain_info': DOMAIN_MAP.get(level, {})
        })
    else:
        player['health'] -= 25 if not hard_mode else 35
        session['player'] = player
        return jsonify({
            'correct': False,
            'reason': reason,
            'player': player,
            'domain_info': DOMAIN_MAP.get(level, {})
        })

@app.route('/api/quiz/question', methods=['GET'])
def get_question():
    player = session.get('player')
    if not player:
        return jsonify({'error': 'No session'}), 400

    domain = request.args.get('domain', None)

    if domain and domain in DOMAINS:
        pool = DOMAINS[domain]
    else:
        pool = QUESTIONS

    if not pool:
        return jsonify({'error': 'No questions available'}), 404

    q = random.choice(pool)
    session['current_question'] = q

    return jsonify({
        'id': q['id'],
        'domain': q['domain'],
        'objective': q['objective'],
        'question': q['question'],
        'options': q['options']
    })

@app.route('/api/quiz/answer', methods=['POST'])
def quiz_answer():
    player = session.get('player')
    if not player:
        return jsonify({'error': 'No session'}), 400

    data = request.json
    ans = data.get('answer')
    q = session.get('current_question')

    if not q:
        return jsonify({'error': 'No active question'}), 400

    correct = ans == q['answer']
    domain = q['domain']

    if domain in player['domain_scores']:
        player['domain_scores'][domain]['attempted'] += 1
        if correct:
            player['domain_scores'][domain]['correct'] += 1
            player['score'] += 50
            player['cert_progress'] = min(100, player.get('cert_progress', 0) + 2)

    session['player'] = player

    return jsonify({
        'correct': correct,
        'correct_answer': q['answer'],
        'correct_text': q['options'][q['answer']],
        'explanation': q['explanation'],
        'domain': domain,
        'player': player
    })

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
            "messages": [{
                "role": "user",
                "content": f"""You are a cybersecurity mentor in a Security+ exam training game.
{context}
Give a practical 2 sentence hint that references real-world security practice and connects to CompTIA Security+ SY0-701 exam objectives.
Do not reveal the answer directly. Be specific, not generic."""
            }]
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
            return jsonify({'hint': result['content'][0]['text']})

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
    prompt = f"""You are a Security+ exam trainer. A player {outcome} this scenario: {context}
Give exactly one sentence of feedback connecting this to a real-world attack technique or CompTIA Security+ SY0-701 exam objective.
Be specific and technical. Reference actual frameworks, tools or CVEs where relevant."""

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

if __name__ == '__main__':
    app.run(debug=True)