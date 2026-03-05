# Flask server — RPG game with Security+ certification integration
from flask import Flask, render_template, request, jsonify, session
import random
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data.rpg_scenarios import (
    PORT_SCENARIOS, LOG_SETS, PASSWORDS_EASY, PASSWORDS_HARD,
    DOMAIN_MAP, SCENARIO_META, ALL_SCENARIO_TYPES,
    SOCIAL_ENGINEERING_SCENARIOS, MALWARE_SCENARIOS,
    CRYPTO_SCENARIOS, ACCESS_CONTROL_SCENARIOS, VULNERABILITY_SCENARIOS,
    TERMINAL_SCENARIOS, PACKET_TRACER_SCENARIOS, BRUTE_FORCE_SCENARIOS,
    MINIGAME_TYPES, DOMAIN_MAP_MINIGAMES,
    get_random_passwords
)
from data.security_plus import QUESTIONS, DOMAINS

app = Flask(__name__)
app.secret_key = os.urandom(24)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/start', methods=['POST'])
def start():
    data = request.json

    # levels 1-3 pick from scenario types, level 4 is always a mini-game
    level_types = random.sample(ALL_SCENARIO_TYPES, 3)
    minigame = random.choice(MINIGAME_TYPES)
    level_types.append(minigame)
    session['level_order'] = level_types

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

@app.route('/api/level_meta', methods=['GET'])
def level_meta():
    order = session.get('level_order', ['password', 'port', 'logs', 'terminal'])

    minigame_meta = {
        'terminal': {'title': 'Terminal Hacking', 'domain': 'Operations & Incident Response'},
        'packet_tracer': {'title': 'Packet Tracer', 'domain': 'Network Security'},
        'brute_force': {'title': 'Brute Force Intercept', 'domain': 'Implementation'}
    }

    meta = []
    for t in order:
        if t in SCENARIO_META:
            m = SCENARIO_META[t]
            d = DOMAIN_MAP.get(t, {})
            meta.append({'type': t, 'title': m['title'], 'domain': d.get('domain', '')})
        elif t in minigame_meta:
            m = minigame_meta[t]
            meta.append({'type': t, 'title': m['title'], 'domain': m['domain']})

    return jsonify({'order': order, 'meta': meta})

@app.route('/api/level/<int:level_num>', methods=['GET'])
def get_level(level_num):
    player = session.get('player')
    if not player:
        return jsonify({'error': 'No session'}), 400
    if level_num > player['level']:
        return jsonify({'error': 'Level locked'}), 403

    level_order = session.get('level_order', ['password', 'port', 'logs', 'terminal'])
    level_type = level_order[level_num - 1]
    hard_mode = player.get('run', 1) > 1
    ai_mode = request.args.get('ai_mode') == 'true'
    api_key = request.args.get('api_key', '')
    model = request.args.get('model', 'claude-sonnet-4-6')

    # mini-game types
    if level_type == 'terminal':
        scenario = random.choice(TERMINAL_SCENARIOS)
        session['current_terminal'] = scenario
        return jsonify({
            'type': 'terminal',
            'title': 'Terminal Hacking',
            'description': 'You have breached the network perimeter. Use your tools to complete the objective.',
            'objective': scenario['objective'],
            'target': scenario['target'],
            'sequence': scenario['sequence'],
            'prompts': scenario['prompts'],
            'wrong_responses': scenario['wrong_responses'],
            'domain_info': DOMAIN_MAP_MINIGAMES['terminal']
        })

    elif level_type == 'packet_tracer':
        scenario = random.choice(PACKET_TRACER_SCENARIOS)
        session['current_packet'] = scenario
        return jsonify({
            'type': 'packet_tracer',
            'title': 'Packet Tracer',
            'description': 'Route the packet through the network to reach the target. Avoid compromised nodes.',
            'objective': scenario['objective'],
            'nodes': scenario['nodes'],
            'connections': scenario['connections'],
            'domain_info': DOMAIN_MAP_MINIGAMES['packet_tracer']
        })

    elif level_type == 'brute_force':
        scenario = random.choice(BRUTE_FORCE_SCENARIOS)
        session['current_brute'] = scenario
        return jsonify({
            'type': 'brute_force',
            'title': 'Brute Force Intercept',
            'description': 'An attacker is running a cracking session. Identify the weakest hash before it is compromised.',
            'objective': scenario['objective'],
            'hashes': scenario['hashes'],
            'domain_info': DOMAIN_MAP_MINIGAMES['brute_force']
        })

    # standard scenario types
    meta = SCENARIO_META.get(level_type, {'title': level_type, 'description': ''})
    domain_info = DOMAIN_MAP.get(level_type, {})

    if ai_mode and api_key and level_type in ['password', 'port', 'logs']:
        try:
            import urllib.request
            import json as json_lib

            prompts = {
                'password': f"""Generate 6 passwords for a Security+ training game (run {player.get('run', 1)}), 3 weak and 3 strong.
Return ONLY JSON: {{"passwords": [{{"password": "example", "weak": true}}]}}""",
                'port': f"""Generate a network port security scenario for a Security+ training game (run {player.get('run', 1)}).
Return ONLY JSON: {{"port": 8080, "service": "HTTP-Alt", "threat": true, "reason": "one sentence"}}""",
                'logs': f"""Generate 3 log entries for a Security+ training game (run {player.get('run', 1)}), one suspicious.
Difficulty: {'easy' if player.get('run', 1) == 1 else 'medium' if player.get('run', 1) == 2 else 'hard'}.
Return ONLY JSON: {{"logs": ["log1","log2","log3"], "answer": 1, "reason": "one sentence"}}"""
            }

            payload = json_lib.dumps({
                "model": model,
                "max_tokens": 500,
                "messages": [{"role": "user", "content": prompts[level_type]}]
            }).encode()

            req = urllib.request.Request(
                'https://api.anthropic.com/v1/messages',
                data=payload,
                headers={'Content-Type': 'application/json', 'x-api-key': api_key, 'anthropic-version': '2023-06-01'}
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
                    return jsonify({'type': 'password', 'title': meta['title'], 'description': meta['description'], 'passwords': ai_data['passwords'], 'hard_mode': hard_mode, 'ai_generated': True, 'domain_info': domain_info})
                elif level_type == 'port':
                    session['current_scenario'] = ai_data
                    return jsonify({'type': 'port', 'title': meta['title'], 'description': meta['description'], 'port': ai_data['port'], 'service': ai_data['service'], 'hard_mode': hard_mode, 'ai_generated': True, 'domain_info': domain_info})
                elif level_type == 'logs':
                    session['current_logs'] = ai_data
                    return jsonify({'type': 'logs', 'title': meta['title'], 'description': meta['description'], 'logs': ai_data['logs'], 'hard_mode': hard_mode, 'ai_generated': True, 'domain_info': domain_info})
        except Exception:
            pass

    if level_type == 'password':
        passwords = get_random_passwords(hard_mode)
        return jsonify({'type': 'password', 'title': meta['title'], 'description': meta['description'], 'passwords': passwords, 'hard_mode': hard_mode, 'domain_info': domain_info})
    elif level_type == 'port':
        scenario = random.choice(PORT_SCENARIOS)
        session['current_scenario'] = scenario
        return jsonify({'type': 'port', 'title': meta['title'], 'description': meta['description'], 'port': scenario['port'], 'service': scenario['service'], 'hard_mode': hard_mode, 'domain_info': domain_info})
    elif level_type == 'logs':
        log_set = random.choice(LOG_SETS)
        session['current_logs'] = log_set
        return jsonify({'type': 'logs', 'title': meta['title'], 'description': meta['description'], 'logs': log_set['logs'], 'hard_mode': hard_mode, 'domain_info': domain_info})
    elif level_type == 'social_engineering':
        scenario = random.choice(SOCIAL_ENGINEERING_SCENARIOS)
        session['current_social'] = scenario
        return jsonify({'type': 'social_engineering', 'title': meta['title'], 'description': meta['description'], 'email': scenario['email'], 'question': scenario['question'], 'options': scenario['options'], 'domain_info': domain_info})
    elif level_type == 'malware':
        scenario = random.choice(MALWARE_SCENARIOS)
        session['current_malware'] = scenario
        return jsonify({'type': 'malware', 'title': meta['title'], 'description': meta['description'], 'behaviours': scenario['behaviours'], 'context': scenario['description'], 'question': scenario['question'], 'options': scenario['options'], 'domain_info': domain_info})
    elif level_type == 'cryptography':
        scenario = random.choice(CRYPTO_SCENARIOS)
        session['current_crypto'] = scenario
        return jsonify({'type': 'cryptography', 'title': meta['title'], 'description': meta['description'], 'scenario': scenario['scenario'], 'question': scenario['question'], 'options': scenario['options'], 'domain_info': domain_info})
    elif level_type == 'access_control':
        scenario = random.choice(ACCESS_CONTROL_SCENARIOS)
        session['current_access'] = scenario
        return jsonify({'type': 'access_control', 'title': meta['title'], 'description': meta['description'], 'request': scenario['request'], 'question': scenario['question'], 'options': scenario['options'], 'domain_info': domain_info})
    elif level_type == 'vulnerability':
        scenario = random.choice(VULNERABILITY_SCENARIOS)
        session['current_vuln'] = scenario
        return jsonify({'type': 'vulnerability', 'title': meta['title'], 'description': meta['description'], 'cve': scenario['cve'], 'cve_description': scenario['description'], 'cvss': scenario['cvss'], 'affected': scenario['affected'], 'question': scenario['question'], 'options': scenario['options'], 'domain_info': domain_info})

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
    level_order = session.get('level_order', ['password', 'port', 'logs', 'terminal'])
    level_type = level_order[level - 1] if level <= len(level_order) else 'password'

    if level_type == 'password':
        passwords = get_random_passwords(hard_mode)
        if 0 <= ans < len(passwords):
            correct = passwords[ans]['weak']
            reason = f"'{passwords[ans]['password']}' is {'weak — short and common' if correct else 'actually a strong password'}."
    elif level_type == 'port':
        scenario = session.get('current_scenario')
        if scenario:
            correct = (ans == scenario['threat'])
            reason = scenario['reason']
    elif level_type == 'logs':
        log_set = session.get('current_logs')
        if log_set:
            correct = (ans == log_set['answer'])
            reason = log_set['reason']
    elif level_type == 'social_engineering':
        scenario = session.get('current_social')
        if scenario:
            correct = (ans == scenario['answer'])
            reason = scenario['reason']
    elif level_type == 'malware':
        scenario = session.get('current_malware')
        if scenario:
            correct = (ans == scenario['answer'])
            reason = scenario['reason']
    elif level_type == 'cryptography':
        scenario = session.get('current_crypto')
        if scenario:
            correct = (ans == scenario['answer'])
            reason = scenario['reason']
    elif level_type == 'access_control':
        scenario = session.get('current_access')
        if scenario:
            correct = (ans == scenario['answer'])
            reason = scenario['reason']
    elif level_type == 'vulnerability':
        scenario = session.get('current_vuln')
        if scenario:
            correct = (ans == scenario['answer'])
            reason = scenario['reason']
    elif level_type == 'terminal':
        # terminal sends 'completed' true/false
        correct = data.get('completed', False)
        scenario = session.get('current_terminal')
        reason = scenario['reason'] if scenario else 'Terminal sequence completed.'
    elif level_type == 'packet_tracer':
        scenario = session.get('current_packet')
        if scenario:
            submitted_path = data.get('path', [])
            correct = (submitted_path == scenario['correct_path'])
            reason = scenario['reason']
    elif level_type == 'brute_force':
        scenario = session.get('current_brute')
        if scenario:
            correct = (ans == scenario['answer'])
            reason = scenario['reason']

    # domain scoring
    if level_type in DOMAIN_MAP_MINIGAMES:
        domain_info = DOMAIN_MAP_MINIGAMES[level_type]
    else:
        domain_info = DOMAIN_MAP.get(level_type, {})

    domain = domain_info.get('domain', '')
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

        if level < 4:
            player['level'] = max(player['level'], level + 1)

        tools = {1: 'Threat Scanner', 2: 'Network Analyser', 3: 'Log Parser', 4: 'Exploit Framework'}
        if tools.get(level) and tools[level] not in player['inventory']:
            player['inventory'].append(tools[level])

        if len(player['completed']) == 4:
            player['run'] = player.get('run', 1) + 1
            player['completed'] = []
            player['level'] = 1
            player['health'] = min(100, player['health'] + 20)
            new_types = random.sample(ALL_SCENARIO_TYPES, 3)
            new_types.append(random.choice(MINIGAME_TYPES))
            session['level_order'] = new_types

        session['player'] = player
        return jsonify({'correct': True, 'reason': reason, 'points': points, 'player': player, 'domain_info': domain_info})
    else:
        player['health'] -= 25 if not hard_mode else 35
        session['player'] = player
        return jsonify({'correct': False, 'reason': reason, 'player': player, 'domain_info': domain_info})

@app.route('/api/quiz/question', methods=['GET'])
def get_question():
    player = session.get('player')
    if not player:
        return jsonify({'error': 'No session'}), 400
    domain = request.args.get('domain', None)
    pool = DOMAINS.get(domain, QUESTIONS) if domain else QUESTIONS
    if not pool:
        return jsonify({'error': 'No questions available'}), 404
    q = random.choice(pool)
    session['current_question'] = q
    return jsonify({'id': q['id'], 'domain': q['domain'], 'objective': q['objective'], 'question': q['question'], 'options': q['options']})

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
    return jsonify({'correct': correct, 'correct_answer': q['answer'], 'correct_text': q['options'][q['answer']], 'explanation': q['explanation'], 'domain': domain, 'player': player})

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
        payload = json_lib.dumps({"model": model, "max_tokens": 150, "messages": [{"role": "user", "content": f"You are a cybersecurity mentor in a Security+ training game. {context} Give a 2 sentence hint referencing real-world practice and Security+ SY0-701 objectives. Do not reveal the answer."}]}).encode()
        req = urllib.request.Request('https://api.anthropic.com/v1/messages', data=payload, headers={'Content-Type': 'application/json', 'x-api-key': key, 'anthropic-version': '2023-06-01'})
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
    try:
        import urllib.request
        import json as json_lib
        payload = json_lib.dumps({"model": model, "max_tokens": 120, "messages": [{"role": "user", "content": f"You are a Security+ trainer. A player {outcome} this scenario: {context}. Give one sentence connecting this to a real attack technique or Security+ SY0-701 objective."}]}).encode()
        req = urllib.request.Request('https://api.anthropic.com/v1/messages', data=payload, headers={'Content-Type': 'application/json', 'x-api-key': key, 'anthropic-version': '2023-06-01'})
        with urllib.request.urlopen(req) as response:
            result = json_lib.loads(response.read())
            return jsonify({'feedback': result['content'][0]['text'].strip()})
    except Exception as e:
        return jsonify({'feedback': ''})

if __name__ == '__main__':
    app.run(debug=True)