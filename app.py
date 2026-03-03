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