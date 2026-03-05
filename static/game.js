// game state
let player = null;
let currentLevel = null;
let selectedLog = null;
let aiMode = false;
let apiKey = null;
let selectedModel = 'claude-sonnet-4-6';
let levelAnswered = false;

const BASE_HINTS = {
    1: "Look for passwords that use common words, keyboard patterns or are just numbers. Length and complexity are what separate weak from strong.",
    2: "Think about whether this service should ever be publicly exposed. Some protocols are outdated and send data unencrypted.",
    3: "Look for patterns that break normal user behaviour — unusual source IPs, impossible login timing, or bulk data access outside working hours."
}

function animateIntro() {
    const lines = document.querySelectorAll('.boot-line');
    lines.forEach((line, i) => {
        line.style.setProperty('--d', `${i * 0.4}s`);
    });
}

animateIntro();

function selectMode(mode) {
    document.getElementById('mode-base').classList.remove('active');
    document.getElementById('mode-ai').classList.remove('active');
    document.getElementById(`mode-${mode}`).classList.add('active');
    document.getElementById('ai-fields').style.display = mode === 'ai' ? 'block' : 'none';
    if (mode === 'base') {
        aiMode = false;
        apiKey = null;
    }
}

async function startGame() {
    const name = document.getElementById('player-name').value.trim();
    if (!name) {
        document.getElementById('player-name').focus();
        return;
    }

    const modeAi = document.getElementById('mode-ai').classList.contains('active');

    if (modeAi) {
        const key = document.getElementById('api-key').value.trim();
        if (!key) {
            document.getElementById('api-key').focus();
            document.getElementById('api-key').style.borderBottom = '1px solid #ff003c';
            return;
        }
        apiKey = key;
        aiMode = true;
        selectedModel = document.getElementById('model-select').value;
    }

    const res = await fetch('/api/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, ai_mode: aiMode })
    });

    const data = await res.json();
    player = data.player;

    document.getElementById('intro-screen').classList.remove('active');
    document.getElementById('game-screen').classList.add('active');
    updateHUD();
    updateDomainTracker();
}

document.getElementById('player-name').addEventListener('keydown', e => {
    if (e.key === 'Enter') startGame();
});

function updateHUD() {
    if (!player) return;

    document.getElementById('hud-name').textContent = player.name.toUpperCase();
    document.getElementById('hud-health').textContent = player.health;
    document.getElementById('hud-score').textContent = player.score;
    document.getElementById('hud-tools').textContent = player.inventory.length
        ? player.inventory.map(t => t.toUpperCase()).join(' / ')
        : 'NONE';

    if (aiMode) {
        const nameEl = document.getElementById('hud-name');
        if (!nameEl.querySelector('.ai-badge')) {
            const badge = document.createElement('span');
            badge.className = 'ai-badge';
            badge.style.cssText = 'font-size:9px; color:#00d4ff; letter-spacing:2px; margin-left:8px;';
            badge.textContent = '[NEURAL NET]';
            nameEl.appendChild(badge);
        }
    }

    const bar = document.getElementById('health-bar');
    bar.style.width = player.health + '%';
    if (player.health > 60) bar.style.background = '#f5c518';
    else if (player.health > 30) bar.style.background = '#ff8800';
    else bar.style.background = '#ff003c';

    const certBar = document.getElementById('cert-bar');
    if (certBar) certBar.style.width = (player.cert_progress || 0) + '%';

    const completed = player.completed || [];

    for (let i = 1; i <= 3; i++) {
        const card = document.getElementById(`level-${i}-card`);
        const status = document.getElementById(`level-${i}-status`);

        if (completed.includes(i)) {
            card.classList.remove('locked');
            card.style.opacity = '0.5';
            card.style.cursor = 'not-allowed';
            status.textContent = '✓ COMPLETE';
            card.onclick = null;
        } else if (i <= player.level) {
            card.classList.remove('locked');
            card.style.opacity = '1';
            card.style.cursor = 'pointer';
            status.textContent = 'AVAILABLE ▶';
            card.onclick = () => loadLevel(i);
        } else {
            card.classList.add('locked');
            card.style.opacity = '0.4';
            status.textContent = '◈ LOCKED';
            card.onclick = null;
        }
    }

    if (player.health <= 0) gameOver(false);
}

function updateDomainTracker() {
    if (!player) return;
    const container = document.getElementById('domain-tracker');
    if (!container) return;

    container.innerHTML = '';
    const domains = player.domain_scores || {};

    Object.entries(domains).forEach(([domain, scores]) => {
        const pill = document.createElement('div');
        pill.className = 'cp-domain-pill' + (scores.attempted > 0 ? ' active' : '');
        const shortName = domain.split(' ')[0];
        pill.textContent = scores.attempted > 0
            ? `${shortName}: ${scores.correct}/${scores.attempted}`
            : shortName;
        pill.title = domain;
        container.appendChild(pill);
    });
}

function showLevelSelect() {
    document.getElementById('level-panel').classList.remove('active');
    document.getElementById('level-select').classList.add('active');
    document.getElementById('feedback').classList.add('hidden');
    document.getElementById('domain-card').classList.add('hidden');
    levelAnswered = false;
    updateDomainTracker();
}

async function loadLevel(num) {
    currentLevel = num;
    selectedLog = null;
    levelAnswered = false;

    const params = aiMode
        ? `?ai_mode=true&api_key=${encodeURIComponent(apiKey)}&model=${encodeURIComponent(selectedModel)}`
        : '';
    const res = await fetch(`/api/level/${num}${params}`);
    if (!res.ok) return;
    const data = await res.json();

    document.getElementById('level-select').classList.remove('active');
    document.getElementById('level-panel').classList.add('active');
    document.getElementById('level-title').textContent = data.title.toUpperCase();
    document.getElementById('level-desc').textContent = data.description;
    document.getElementById('feedback').classList.add('hidden');
    document.getElementById('feedback').className = 'cp-feedback hidden';
    document.getElementById('domain-card').classList.add('hidden');

    const content = document.getElementById('level-content');
    content.innerHTML = '';

    const modeEl = document.createElement('p');
    modeEl.className = `cp-mode-indicator ${aiMode ? 'ai' : ''}`;
    modeEl.textContent = data.ai_generated
        ? '// NEURAL NET MODE — scenario generated by Claude'
        : aiMode ? '// NEURAL NET MODE — using cached scenario' : '// STANDARD OPS MODE';
    content.appendChild(modeEl);

    const hintWrap = document.createElement('div');
    const hintBtn = document.createElement('button');
    hintBtn.className = 'cp-hint-btn';
    hintBtn.textContent = aiMode ? '⚡ QUERY CLAUDE' : '? REQUEST HINT';
    hintBtn.onclick = () => showHint(num, data);
    hintWrap.appendChild(hintBtn);

    const hintBox = document.createElement('div');
    hintBox.className = 'cp-hint-box';
    hintBox.id = 'hint-box';
    hintWrap.appendChild(hintBox);
    content.appendChild(hintWrap);

    if (data.type === 'password') renderPasswordLevel(data, content);
    else if (data.type === 'port') renderPortLevel(data, content);
    else if (data.type === 'logs') renderLogLevel(data, content);
}

async function showHint(levelNum, levelData) {
    const hintBox = document.getElementById('hint-box');
    hintBox.classList.add('visible');
    hintBox.textContent = aiMode ? '[ QUERYING CLAUDE... ]' : BASE_HINTS[levelNum];

    if (!aiMode) return;

    let context = '';
    if (levelData.type === 'password') {
        const passwords = levelData.passwords.map(p => p.password).join(', ');
        context = `The player is looking at these passwords: ${passwords}. Give a short hint about what makes a password weak without revealing the answer.`;
    } else if (levelData.type === 'port') {
        context = `The player is deciding whether to block port ${levelData.port} running ${levelData.service}. Give a short hint about this service without revealing the answer.`;
    } else if (levelData.type === 'logs') {
        context = `The player is analysing these log entries: ${levelData.logs.join(' | ')}. Give a short hint about what to look for in suspicious logs without revealing which one is the attacker.`;
    }

    try {
        const res = await fetch('/api/ai_hint', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ context, api_key: apiKey, model: selectedModel })
        });
        const data = await res.json();
        hintBox.textContent = data.hint || 'Could not reach Claude. Check your API key.';
    } catch (e) {
        hintBox.textContent = 'Connection to Claude failed.';
    }
}

function lockAllOptions() {
    // disable all clickable options once level is solved
    document.querySelectorAll('.cp-password-btn').forEach(btn => {
        btn.onclick = null;
        btn.style.opacity = '0.4';
        btn.style.cursor = 'not-allowed';
    });
    document.querySelectorAll('.cp-log-entry').forEach(entry => {
        entry.onclick = null;
        entry.style.cursor = 'default';
    });
    document.querySelectorAll('.cp-btn-block, .cp-btn-allow').forEach(btn => {
        btn.onclick = null;
        btn.style.opacity = '0.4';
        btn.style.cursor = 'not-allowed';
    });
    const confirmBtn = document.querySelector('.cp-confirm-btn');
    if (confirmBtn) {
        confirmBtn.onclick = null;
        confirmBtn.style.opacity = '0.4';
        confirmBtn.style.cursor = 'not-allowed';
    }
}

function renderPasswordLevel(data, container) {
    const label = document.createElement('p');
    label.style.cssText = 'font-size:12px; color:#8888aa; margin-bottom:14px; letter-spacing:1px;';
    label.textContent = '// IDENTIFY THE WEAKEST PASSWORD IN THIS SET';
    container.appendChild(label);

    // shuffle passwords so the order is different every time
    const shuffled = [...data.passwords].sort(() => Math.random() - 0.5);

    const grid = document.createElement('div');
    grid.className = 'cp-password-grid';

    shuffled.forEach((p, i) => {
        const btn = document.createElement('button');
        btn.className = 'cp-password-btn';
        btn.textContent = p.password;
        // find original index for answer submission
        const originalIndex = data.passwords.findIndex(orig => orig.password === p.password);
        btn.onclick = () => {
            if (levelAnswered) return;
            submitAnswer(originalIndex);
        };
        grid.appendChild(btn);
    });

    container.appendChild(grid);
}

function renderPortLevel(data, container) {
    const output = document.createElement('div');
    output.className = 'cp-scan-output';

    const lines = [
        `> INITIATING DEEP PACKET SCAN...`,
        `> TARGET: 192.168.${Math.floor(Math.random()*255)}.${Math.floor(Math.random()*255)}`,
        `> SCANNING REGISTERED PORTS...`,
        `>`,
        `> PORT      SERVICE     STATE    RISK`,
        `> ─────────────────────────────────────`,
        `> ${String(data.port).padEnd(10)}${data.service.padEnd(12)}OPEN     UNKNOWN`,
        `>`,
        `> SCAN COMPLETE. ASSESSMENT REQUIRED.`
    ];

    lines.forEach((line, i) => {
        const p = document.createElement('p');
        p.className = 'scan-line';
        p.textContent = line;
        output.appendChild(p);
        setTimeout(() => p.classList.add('visible'), i * 180);
    });

    container.appendChild(output);

    const label = document.createElement('p');
    label.style.cssText = 'font-size:12px; color:#8888aa; margin-bottom:14px; letter-spacing:1px;';
    label.textContent = '// SHOULD THIS PORT BE BLOCKED?';
    container.appendChild(label);

    const actions = document.createElement('div');
    actions.className = 'cp-port-actions';

    const blockBtn = document.createElement('button');
    blockBtn.className = 'cp-btn-block';
    blockBtn.textContent = '◼ BLOCK PORT';
    blockBtn.onclick = () => {
        if (levelAnswered) return;
        submitAnswer(true);
    };

    const allowBtn = document.createElement('button');
    allowBtn.className = 'cp-btn-allow';
    allowBtn.textContent = '◻ LEAVE OPEN';
    allowBtn.onclick = () => {
        if (levelAnswered) return;
        submitAnswer(false);
    };

    actions.appendChild(blockBtn);
    actions.appendChild(allowBtn);
    container.appendChild(actions);
}

function renderLogLevel(data, container) {
    const label = document.createElement('p');
    label.style.cssText = 'font-size:12px; color:#8888aa; margin-bottom:14px; letter-spacing:1px;';
    label.textContent = '// SELECT THE SUSPICIOUS LOG ENTRY THEN CONFIRM';
    container.appendChild(label);

    // shuffle log order so the answer isn't always the same position
    const indices = [0, 1, 2].sort(() => Math.random() - 0.5);
    const shuffledLogs = indices.map(i => ({ log: data.logs[i], originalIndex: i }));

    shuffledLogs.forEach(({ log, originalIndex }) => {
        const entry = document.createElement('div');
        entry.className = 'cp-log-entry';
        entry.textContent = log;
        entry.onclick = () => {
            if (levelAnswered) return;
            document.querySelectorAll('.cp-log-entry').forEach(e => e.classList.remove('selected'));
            entry.classList.add('selected');
            selectedLog = originalIndex;
        };
        container.appendChild(entry);
    });

    const confirmBtn = document.createElement('button');
    confirmBtn.className = 'cp-confirm-btn';
    confirmBtn.style.marginTop = '18px';
    confirmBtn.textContent = '▶ CONFIRM SELECTION';
    confirmBtn.onclick = () => {
        if (levelAnswered || selectedLog === null) return;
        submitAnswer(selectedLog);
    };
    container.appendChild(confirmBtn);
}

async function submitAnswer(answer) {
    if (levelAnswered) return;

    const res = await fetch('/api/answer', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ level: currentLevel, answer, ai_mode: aiMode, api_key: apiKey, model: selectedModel })
    });

    const data = await res.json();
    player = data.player;
    updateHUD();

    const feedback = document.getElementById('feedback');
    feedback.classList.remove('hidden', 'wrong');
    feedback.className = 'cp-feedback';

    if (data.correct) {
        levelAnswered = true;
        lockAllOptions();

        feedback.textContent = `◈ CORRECT. ${data.reason} +${data.points} pts`;

        if (data.domain_info) showDomainCard(data.domain_info);

        if (aiMode) {
            const fbRes = await fetch('/api/ai_feedback', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ level: currentLevel, correct: true, context: data.reason, api_key: apiKey, model: selectedModel })
            });
            const fbData = await fbRes.json();
            if (fbData.feedback) {
                const p = document.createElement('p');
                p.style.cssText = 'margin-top:8px; color:#00d4ff; font-size:11px;';
                p.textContent = `[ CLAUDE ] ${fbData.feedback}`;
                feedback.appendChild(p);
            }
        }

        const nextBtn = document.createElement('button');
        nextBtn.style.marginTop = '16px';
        nextBtn.textContent = currentLevel === 3 ? '▶ VIEW DEBRIEF' : '▶ NEXT MISSION';
        nextBtn.onclick = currentLevel === 3 ? () => gameOver(true) : showLevelSelect;
        feedback.appendChild(document.createElement('br'));
        feedback.appendChild(nextBtn);

    } else {
        // wrong answer — options stay active so they can try again
        feedback.classList.add('wrong');
        feedback.textContent = `✗ WRONG CALL. ${data.reason} -25 INTEGRITY.`;

        if (aiMode) {
            const fbRes = await fetch('/api/ai_feedback', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ level: currentLevel, correct: false, context: data.reason, api_key: apiKey, model: selectedModel })
            });
            const fbData = await fbRes.json();
            if (fbData.feedback) {
                const p = document.createElement('p');
                p.style.cssText = 'margin-top:8px; color:#ff003c; font-size:11px;';
                p.textContent = `[ CLAUDE ] ${fbData.feedback}`;
                feedback.appendChild(p);
            }
        }
    }
}

function showDomainCard(domainInfo) {
    const card = document.getElementById('domain-card');
    card.classList.remove('hidden');
    document.getElementById('domain-name').textContent = domainInfo.domain || '';
    document.getElementById('domain-objective').textContent = domainInfo.objective || '';
    document.getElementById('domain-concept').textContent = domainInfo.key_concept || '';
    const tip = document.getElementById('domain-tip');
    tip.textContent = domainInfo.exam_tip || '';
    tip.className = 'cp-domain-value highlight';
}

function gameOver(won) {
    document.getElementById('game-screen').classList.remove('active');
    document.getElementById('gameover-screen').classList.add('active');

    const title = document.getElementById('gameover-title');
    const msg = document.getElementById('gameover-msg');

    if (won) {
        title.textContent = '// MISSION COMPLETE — DEBRIEF';
        title.style.color = '#f5c518';

        const domainSummary = player.domain_scores
            ? Object.entries(player.domain_scores)
                .filter(([, s]) => s.attempted > 0)
                .map(([d, s]) => `<div style="font-size:12px; color:#8888aa; margin-bottom:4px;">
                    <span style="color:#00d4ff; min-width:280px; display:inline-block;">${d}</span>
                    <span style="color:#f5c518;">${s.correct}/${s.attempted} correct</span>
                </div>`).join('')
            : '';

        msg.innerHTML = `
            <p style="color:#f5c518; font-family:'Rajdhani',sans-serif; font-size:22px; letter-spacing:4px; margin-bottom:20px;">
                ${getRating(player.score, player.health)}
            </p>
            <div style="display:grid; grid-template-columns:1fr 1fr; gap:16px; margin-bottom:24px;">
                <div>
                    <div style="font-size:10px; color:#8888aa; letter-spacing:3px; margin-bottom:4px;">AGENT</div>
                    <div style="font-size:16px; font-family:'Rajdhani',sans-serif; color:#e8e8f4;">${player.name.toUpperCase()}</div>
                </div>
                <div>
                    <div style="font-size:10px; color:#8888aa; letter-spacing:3px; margin-bottom:4px;">FINAL SCORE</div>
                    <div style="font-size:16px; font-family:'Rajdhani',sans-serif; color:#f5c518;">${player.score}</div>
                </div>
                <div>
                    <div style="font-size:10px; color:#8888aa; letter-spacing:3px; margin-bottom:4px;">INTEGRITY</div>
                    <div style="font-size:16px; font-family:'Rajdhani',sans-serif; color:${player.health > 60 ? '#f5c518' : player.health > 30 ? '#ff8800' : '#ff003c'};">${player.health}%</div>
                </div>
                <div>
                    <div style="font-size:10px; color:#8888aa; letter-spacing:3px; margin-bottom:4px;">TOOLS ACQUIRED</div>
                    <div style="font-size:13px; color:#00d4ff;">${player.inventory.join(', ') || 'None'}</div>
                </div>
            </div>
            ${domainSummary ? `
            <div style="border-top:1px solid #2a2a3e; padding-top:16px; margin-bottom:16px;">
                <div style="font-size:10px; color:#8888aa; letter-spacing:3px; margin-bottom:12px;">SECURITY+ DOMAIN PERFORMANCE</div>
                ${domainSummary}
            </div>` : ''}
            <p style="color:#8888aa; font-size:11px;">All threats neutralised, ${player.name}. Stay vigilant.</p>
        `;
    } else {
        title.textContent = '// AGENT DOWN — CONNECTION LOST';
        title.style.color = '#ff003c';

        msg.innerHTML = `
            <p style="color:#ff003c; font-family:'Rajdhani',sans-serif; font-size:22px; letter-spacing:4px; margin-bottom:20px;">INTEGRITY FAILURE</p>
            <p style="margin-bottom:8px; color:#e8e8f4;">Agent: ${player.name.toUpperCase()}</p>
            <p style="margin-bottom:20px; color:#f5c518;">Final score: ${player.score}</p>
            <p style="color:#8888aa; font-size:12px;">You ran out of integrity. The breach was not contained.</p>
        `;
    }

    const restartBtn = document.createElement('button');
    restartBtn.style.marginTop = '24px';
    restartBtn.textContent = '↺ NEW SESSION';
    restartBtn.onclick = () => location.reload();
    msg.appendChild(restartBtn);
}

function getRating(score, health) {
    const total = score + health;
    if (total >= 500) return 'S-TIER // ELITE NETRUNNER';
    if (total >= 400) return 'A-TIER // SENIOR ANALYST';
    if (total >= 300) return 'B-TIER // FIELD OPERATIVE';
    return 'C-TIER // ROOKIE AGENT';
}