let player = null;
let currentLevel = null;
let selectedLog = null;
let aiMode = false;
let apiKey = null;
let selectedModel = 'claude-sonnet-4-6';
let levelAnswered = false;

const BASE_HINTS = {
    password: "Look for passwords that use common words, keyboard patterns or just numbers. Length and complexity are what separate weak from strong.",
    port: "Think about whether this service should ever be publicly exposed. Some protocols are outdated and send data unencrypted.",
    logs: "Look for patterns that break normal user behaviour — unusual IPs, impossible login timing, or bulk data access.",
    social_engineering: "Check the sender domain carefully. Look for urgency, threats, and links that don't match the claimed sender.",
    malware: "Focus on what the process is doing, not what it claims to be. Look at CPU usage, network connections and persistence mechanisms.",
    cryptography: "Think about whether the data needs to be recovered later. Hashing is one-way, encryption is reversible. Match the tool to the requirement.",
    access_control: "Apply least privilege — grant only the minimum access needed to do the job. Nothing more.",
    vulnerability: "Distinguish between fixing the root cause and implementing a compensating control. Patching is a fix, a WAF is a control."
}

// ── transition helpers ────────────────────────────────────────────────────────

function showLoadingBar() {
    const bar = document.getElementById('loading-bar');
    bar.style.width = '0%';
    bar.classList.remove('done');
    bar.style.opacity = '1';
    setTimeout(() => bar.style.width = '70%', 50);
}

function completeLoadingBar() {
    const bar = document.getElementById('loading-bar');
    bar.classList.add('done');
    setTimeout(() => {
        bar.style.width = '0%';
        bar.classList.remove('done');
    }, 700);
}

function screenFlash() {
    const flash = document.getElementById('screen-flash');
    if (!flash) return;
    flash.classList.remove('flash');
    void flash.offsetWidth;
    flash.classList.add('flash');
}

function glitchTitle(el) {
    if (!el) return;
    el.classList.remove('glitch');
    void el.offsetWidth;
    el.classList.add('glitch');
    setTimeout(() => el.classList.remove('glitch'), 400);
}

function popValue(id) {
    const el = document.getElementById(id);
    if (!el) return;
    el.classList.remove('pop');
    void el.offsetWidth;
    el.classList.add('pop');
    setTimeout(() => el.classList.remove('pop'), 300);
}

function transitionPanels(fromId, toId, callback) {
    const from = document.getElementById(fromId);
    const to = toId ? document.getElementById(toId) : null;

    if (from) {
        from.classList.add('fade-out');
        setTimeout(() => {
            from.classList.remove('active', 'fade-out');
            if (callback) callback();
            if (to) {
                to.classList.add('active', 'fade-in');
                setTimeout(() => to.classList.remove('fade-in'), 400);
            }
        }, 300);
    } else {
        if (to) {
            to.classList.add('active', 'fade-in');
            setTimeout(() => to.classList.remove('fade-in'), 400);
        }
        if (callback) callback();
    }
}

// ── boot animation ────────────────────────────────────────────────────────────

function animateIntro() {
    const lines = document.querySelectorAll('.boot-line');
    lines.forEach((line, i) => {
        line.style.setProperty('--d', `${i * 0.4}s`);
    });
}

animateIntro();

// ── mode selection ────────────────────────────────────────────────────────────

function selectMode(mode) {
    document.getElementById('mode-base').classList.remove('active');
    document.getElementById('mode-ai').classList.remove('active');
    document.getElementById(`mode-${mode}`).classList.add('active');
    document.getElementById('ai-fields').style.display = mode === 'ai' ? 'block' : 'none';
    if (mode === 'base') { aiMode = false; apiKey = null; }
}

// ── start game ────────────────────────────────────────────────────────────────

async function startGame() {
    const name = document.getElementById('player-name').value.trim();
    if (!name) { document.getElementById('player-name').focus(); return; }

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

    screenFlash();

    const res = await fetch('/api/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, ai_mode: aiMode })
    });

    const data = await res.json();
    player = data.player;

    setTimeout(() => {
        document.getElementById('intro-screen').classList.remove('active');
        const gameScreen = document.getElementById('game-screen');
        gameScreen.classList.add('active', 'fade-in');
        setTimeout(() => gameScreen.classList.remove('fade-in'), 400);
        updateHUD();
        updateDomainTracker();
        loadLevelMeta();
    }, 200);
}

document.getElementById('player-name').addEventListener('keydown', e => {
    if (e.key === 'Enter') startGame();
});

// ── level meta ────────────────────────────────────────────────────────────────

async function loadLevelMeta() {
    const res = await fetch('/api/level_meta');
    if (!res.ok) return;
    const data = await res.json();

    const descriptions = {
        'password': 'Identify the weakest credential before the attacker does.',
        'port': 'Analyse an exposed network service and decide whether to block it.',
        'logs': 'Hunt the attacker through live log data.',
        'social_engineering': 'Analyse a flagged email for phishing indicators.',
        'malware': 'Identify a threat from endpoint behavioural telemetry.',
        'cryptography': 'Choose the correct cryptographic approach for the scenario.',
        'access_control': 'Evaluate an access request against least privilege.',
        'vulnerability': 'Determine the correct mitigation for a critical CVE.'
    };

    data.meta.forEach((m, i) => {
        const num = i + 1;
        const nameEl = document.getElementById(`level-${num}-name`);
        const domainEl = document.getElementById(`level-${num}-domain`);
        const descEl = document.getElementById(`level-${num}-desc`);
        if (nameEl) nameEl.textContent = m.title.toUpperCase();
        if (domainEl) domainEl.textContent = `Security+ — ${m.domain}`;
        if (descEl) descEl.textContent = descriptions[m.type] || 'Investigate and neutralise the threat.';
    });
}

// ── HUD ───────────────────────────────────────────────────────────────────────

function updateHUD() {
    if (!player) return;

    document.getElementById('hud-name').textContent = player.name.toUpperCase();
    document.getElementById('hud-health').textContent = player.health;
    document.getElementById('hud-score').textContent = player.score;
    document.getElementById('hud-tools').textContent = player.inventory.length
        ? player.inventory.map(t => t.toUpperCase()).join(' / ') : 'NONE';

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
    bar.style.width = Math.max(0, player.health) + '%';
    bar.style.background = player.health > 60 ? '#f5c518' : player.health > 30 ? '#ff8800' : '#ff003c';

    const certBar = document.getElementById('cert-bar');
    if (certBar) certBar.style.width = (player.cert_progress || 0) + '%';

    const completed = player.completed || [];
    for (let i = 1; i <= 3; i++) {
        const card = document.getElementById(`level-${i}-card`);
        const status = document.getElementById(`level-${i}-status`);
        if (!card || !status) continue;

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
        pill.textContent = scores.attempted > 0 ? `${shortName}: ${scores.correct}/${scores.attempted}` : shortName;
        pill.title = domain;
        container.appendChild(pill);
    });
}

// ── navigation ────────────────────────────────────────────────────────────────

function showLevelSelect() {
    screenFlash();
    transitionPanels('level-panel', 'level-select', null);
    document.getElementById('feedback').classList.add('hidden');
    document.getElementById('domain-card').classList.add('hidden');
    levelAnswered = false;
    updateDomainTracker();
    loadLevelMeta();
}

// ── load level ────────────────────────────────────────────────────────────────

async function loadLevel(num) {
    currentLevel = num;
    selectedLog = null;
    levelAnswered = false;

    showLoadingBar();
    screenFlash();

    const card = document.getElementById(`level-${num}-card`);
    if (card) {
        card.classList.add('pulse');
        setTimeout(() => card.classList.remove('pulse'), 400);
    }

    const params = aiMode
        ? `?ai_mode=true&api_key=${encodeURIComponent(apiKey)}&model=${encodeURIComponent(selectedModel)}`
        : '';

    const res = await fetch(`/api/level/${num}${params}`);
    if (!res.ok) { completeLoadingBar(); return; }
    const data = await res.json();

    completeLoadingBar();

    // fade out level select, then show level panel
    const levelSelect = document.getElementById('level-select');
    const levelPanel = document.getElementById('level-panel');

    levelSelect.classList.add('fade-out');
    setTimeout(() => {
        levelSelect.classList.remove('active', 'fade-out');
        levelPanel.classList.add('active', 'fade-in');
        setTimeout(() => levelPanel.classList.remove('fade-in'), 400);
    }, 300);

    document.getElementById('level-title').textContent = data.title.toUpperCase();
    setTimeout(() => glitchTitle(document.getElementById('level-title')), 400);

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
    hintBtn.onclick = () => showHint(data.type, data);
    hintWrap.appendChild(hintBtn);
    const hintBox = document.createElement('div');
    hintBox.className = 'cp-hint-box';
    hintBox.id = 'hint-box';
    hintWrap.appendChild(hintBox);
    content.appendChild(hintWrap);

    if (data.type === 'password') renderPasswordLevel(data, content);
    else if (data.type === 'port') renderPortLevel(data, content);
    else if (data.type === 'logs') renderLogLevel(data, content);
    else if (data.type === 'social_engineering') renderSocialEngineering(data, content);
    else if (data.type === 'malware') renderMalware(data, content);
    else if (data.type === 'cryptography') renderCryptography(data, content);
    else if (data.type === 'access_control') renderAccessControl(data, content);
    else if (data.type === 'vulnerability') renderVulnerability(data, content);
}

// ── hints ─────────────────────────────────────────────────────────────────────

async function showHint(levelType, levelData) {
    const hintBox = document.getElementById('hint-box');
    hintBox.classList.add('visible');
    hintBox.textContent = aiMode ? '[ QUERYING CLAUDE... ]' : (BASE_HINTS[levelType] || 'Think carefully about the security implications.');

    if (!aiMode) return;

    let context = `Level type: ${levelType}. `;
    if (levelType === 'password') context += `Passwords: ${levelData.passwords?.map(p => p.password).join(', ')}`;
    else if (levelType === 'port') context += `Port ${levelData.port} running ${levelData.service}`;
    else if (levelType === 'logs') context += `Logs: ${levelData.logs?.join(' | ')}`;
    else if (levelType === 'social_engineering') context += `Email from: ${levelData.email?.from}, subject: ${levelData.email?.subject}`;
    else if (levelType === 'malware') context += `Behaviours: ${levelData.behaviours?.join(', ')}`;
    else if (levelType === 'cryptography') context += `Scenario: ${levelData.scenario}`;
    else if (levelType === 'access_control') context += `Request from ${levelData.request?.user} for ${levelData.request?.requesting}`;
    else if (levelType === 'vulnerability') context += `CVE: ${levelData.cve}`;

    try {
        const res = await fetch('/api/ai_hint', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ context, api_key: apiKey, model: selectedModel })
        });
        const d = await res.json();
        hintBox.textContent = d.hint || 'Could not reach Claude.';
    } catch (e) {
        hintBox.textContent = 'Connection to Claude failed.';
    }
}

// ── lock options ──────────────────────────────────────────────────────────────

function lockAllOptions() {
    document.querySelectorAll('.cp-password-btn, .cp-btn-block, .cp-btn-allow, .cp-option-btn, .cp-confirm-btn').forEach(btn => {
        btn.onclick = null;
        btn.style.opacity = '0.4';
        btn.style.cursor = 'not-allowed';
    });
    document.querySelectorAll('.cp-log-entry').forEach(e => {
        e.onclick = null;
        e.style.cursor = 'default';
    });
}

// ── render functions ──────────────────────────────────────────────────────────

function renderPasswordLevel(data, container) {
    const label = document.createElement('p');
    label.style.cssText = 'font-size:12px; color:#8888aa; margin-bottom:14px; letter-spacing:1px;';
    label.textContent = '// IDENTIFY THE WEAKEST PASSWORD IN THIS SET';
    container.appendChild(label);

    const shuffled = [...data.passwords].sort(() => Math.random() - 0.5);
    const grid = document.createElement('div');
    grid.className = 'cp-password-grid';

    shuffled.forEach(p => {
        const btn = document.createElement('button');
        btn.className = 'cp-password-btn';
        btn.textContent = p.password;
        const originalIndex = data.passwords.findIndex(orig => orig.password === p.password);
        btn.onclick = () => { if (!levelAnswered) submitAnswer(originalIndex); };
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
    blockBtn.onclick = () => { if (!levelAnswered) submitAnswer(true); };

    const allowBtn = document.createElement('button');
    allowBtn.className = 'cp-btn-allow';
    allowBtn.textContent = '◻ LEAVE OPEN';
    allowBtn.onclick = () => { if (!levelAnswered) submitAnswer(false); };

    actions.appendChild(blockBtn);
    actions.appendChild(allowBtn);
    container.appendChild(actions);
}

function renderLogLevel(data, container) {
    const label = document.createElement('p');
    label.style.cssText = 'font-size:12px; color:#8888aa; margin-bottom:14px; letter-spacing:1px;';
    label.textContent = '// SELECT THE SUSPICIOUS LOG ENTRY THEN CONFIRM';
    container.appendChild(label);

    const indices = [0, 1, 2].sort(() => Math.random() - 0.5);
    indices.forEach(i => {
        const entry = document.createElement('div');
        entry.className = 'cp-log-entry';
        entry.textContent = data.logs[i];
        entry.onclick = () => {
            if (levelAnswered) return;
            document.querySelectorAll('.cp-log-entry').forEach(e => e.classList.remove('selected'));
            entry.classList.add('selected');
            selectedLog = i;
        };
        container.appendChild(entry);
    });

    const confirmBtn = document.createElement('button');
    confirmBtn.className = 'cp-confirm-btn';
    confirmBtn.style.marginTop = '18px';
    confirmBtn.textContent = '▶ CONFIRM SELECTION';
    confirmBtn.onclick = () => { if (!levelAnswered && selectedLog !== null) submitAnswer(selectedLog); };
    container.appendChild(confirmBtn);
}

function renderSocialEngineering(data, container) {
    const emailBox = document.createElement('div');
    emailBox.style.cssText = 'background:#06060a; border:1px solid #2a2a3e; margin-bottom:20px;';

    const emailHeader = document.createElement('div');
    emailHeader.style.cssText = 'padding:14px 18px; border-bottom:1px solid #2a2a3e;';
    emailHeader.innerHTML = `
        <div style="font-size:11px; color:#8888aa; margin-bottom:6px;">FROM: <span style="color:#ff8800;">${data.email.from}</span></div>
        <div style="font-size:11px; color:#8888aa; margin-bottom:6px;">SUBJECT: <span style="color:#e8e8f4;">${data.email.subject}</span></div>
        <div style="font-size:10px; color:#555566;">TO: you@corp.com</div>
    `;
    emailBox.appendChild(emailHeader);

    const emailBody = document.createElement('div');
    emailBody.style.cssText = 'padding:18px; font-size:13px; color:#d0d0e8; line-height:1.7;';
    emailBody.textContent = data.email.body;
    emailBox.appendChild(emailBody);
    container.appendChild(emailBox);

    renderOptions(data, container);
}

function renderMalware(data, container) {
    const contextEl = document.createElement('p');
    contextEl.style.cssText = 'font-size:12px; color:#8888aa; margin-bottom:14px;';
    contextEl.textContent = data.context;
    container.appendChild(contextEl);

    const list = document.createElement('div');
    list.style.cssText = 'background:#06060a; border:1px solid #2a2a3e; border-left:2px solid #ff003c; padding:16px 18px; margin-bottom:20px;';

    data.behaviours.forEach(b => {
        const item = document.createElement('p');
        item.style.cssText = 'font-size:12px; color:#d0d0e8; margin-bottom:8px; padding-left:12px;';
        item.textContent = `▸ ${b}`;
        list.appendChild(item);
    });
    container.appendChild(list);

    renderOptions(data, container);
}

function renderCryptography(data, container) {
    const scenarioBox = document.createElement('div');
    scenarioBox.style.cssText = 'background:#06060a; border:1px solid #2a2a3e; border-left:2px solid #00d4ff; padding:18px; margin-bottom:20px; font-size:13px; color:#d0d0e8; line-height:1.7;';
    scenarioBox.textContent = data.scenario;
    container.appendChild(scenarioBox);

    renderOptions(data, container);
}

function renderAccessControl(data, container) {
    const reqBox = document.createElement('div');
    reqBox.style.cssText = 'background:#06060a; border:1px solid #2a2a3e; margin-bottom:20px;';

    const reqHeader = document.createElement('div');
    reqHeader.style.cssText = 'padding:10px 18px; border-bottom:1px solid #2a2a3e; font-size:10px; color:#8888aa; letter-spacing:2px;';
    reqHeader.textContent = '// ACCESS REQUEST';
    reqBox.appendChild(reqHeader);

    const reqBody = document.createElement('div');
    reqBody.style.cssText = 'padding:16px 18px;';
    reqBody.innerHTML = `
        <div style="margin-bottom:10px;"><span style="font-size:10px; color:#8888aa; letter-spacing:2px; display:block; margin-bottom:3px;">USER</span><span style="font-size:13px; color:#e8e8f4;">${data.request.user}</span></div>
        <div style="margin-bottom:10px;"><span style="font-size:10px; color:#8888aa; letter-spacing:2px; display:block; margin-bottom:3px;">REQUESTING</span><span style="font-size:13px; color:#f5c518;">${data.request.requesting}</span></div>
        <div><span style="font-size:10px; color:#8888aa; letter-spacing:2px; display:block; margin-bottom:3px;">JUSTIFICATION</span><span style="font-size:13px; color:#d0d0e8;">${data.request.justification}</span></div>
    `;
    reqBox.appendChild(reqBody);
    container.appendChild(reqBox);

    renderOptions(data, container);
}

function renderVulnerability(data, container) {
    const cveBox = document.createElement('div');
    cveBox.style.cssText = 'background:#06060a; border:1px solid #2a2a3e; margin-bottom:20px;';

    const cveHeader = document.createElement('div');
    cveHeader.style.cssText = 'padding:10px 18px; border-bottom:1px solid #2a2a3e; display:flex; justify-content:space-between; align-items:center;';
    cveHeader.innerHTML = `
        <span style="font-size:14px; color:#f5c518; font-family:'Rajdhani',sans-serif; font-weight:700; letter-spacing:2px;">${data.cve}</span>
        <span style="font-size:11px; color:#ff003c; letter-spacing:1px;">${data.cvss}</span>
    `;
    cveBox.appendChild(cveHeader);

    const cveBody = document.createElement('div');
    cveBody.style.cssText = 'padding:16px 18px;';
    cveBody.innerHTML = `
        <p style="font-size:12px; color:#d0d0e8; line-height:1.7; margin-bottom:12px;">${data.cve_description}</p>
        <p style="font-size:11px; color:#8888aa;"><span style="color:#00d4ff;">AFFECTED:</span> ${data.affected}</p>
    `;
    cveBox.appendChild(cveBody);
    container.appendChild(cveBox);

    renderOptions(data, container);
}

function renderOptions(data, container) {
    const label = document.createElement('p');
    label.style.cssText = 'font-size:12px; color:#8888aa; margin-bottom:14px; letter-spacing:1px;';
    label.textContent = `// ${data.question.toUpperCase()}`;
    container.appendChild(label);

    const optionsWrap = document.createElement('div');
    optionsWrap.style.cssText = 'display:flex; flex-direction:column; gap:10px;';

    data.options.forEach((opt, i) => {
        const btn = document.createElement('button');
        btn.className = 'cp-option-btn';
        btn.style.cssText = 'text-align:left; padding:14px 18px; font-size:13px; background:#0d0d15; border:1px solid #2a2a3e; color:#d0d0e8; clip-path:none; letter-spacing:0px; font-family:"Share Tech Mono",monospace; font-weight:400; line-height:1.5;';
        btn.textContent = `${String.fromCharCode(65 + i)}. ${opt}`;
        btn.onmouseover = () => { if (!levelAnswered) { btn.style.borderColor = '#f5c518'; btn.style.color = '#f5c518'; } };
        btn.onmouseout = () => { if (!levelAnswered) { btn.style.borderColor = '#2a2a3e'; btn.style.color = '#d0d0e8'; } };
        btn.onclick = () => { if (!levelAnswered) submitAnswer(i); };
        optionsWrap.appendChild(btn);
    });

    container.appendChild(optionsWrap);
}

// ── submit answer ─────────────────────────────────────────────────────────────

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
    feedback.className = 'cp-feedback';

    if (data.correct) {
        levelAnswered = true;
        lockAllOptions();
        popValue('hud-score');

        feedback.textContent = `◈ CORRECT. ${data.reason} +${data.points} pts`;
        feedback.classList.add('flash-correct');
        setTimeout(() => feedback.classList.remove('flash-correct'), 500);

        if (data.domain_info) showDomainCard(data.domain_info);

        if (aiMode) {
            try {
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
            } catch (e) {}
        }

        const nextBtn = document.createElement('button');
        nextBtn.style.marginTop = '16px';
        nextBtn.textContent = currentLevel === 3 ? '▶ VIEW DEBRIEF' : '▶ NEXT MISSION';
        nextBtn.onclick = currentLevel === 3 ? () => gameOver(true) : showLevelSelect;
        feedback.appendChild(document.createElement('br'));
        feedback.appendChild(nextBtn);

    } else {
        feedback.classList.add('wrong');
        feedback.textContent = `✗ WRONG CALL. ${data.reason} -25 INTEGRITY.`;
        feedback.classList.add('shake');
        setTimeout(() => feedback.classList.remove('shake'), 400);
        popValue('hud-health');

        if (aiMode) {
            try {
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
            } catch (e) {}
        }
    }
}

// ── domain card ───────────────────────────────────────────────────────────────

function showDomainCard(domainInfo) {
    const card = document.getElementById('domain-card');
    card.classList.remove('hidden', 'slide-in');
    void card.offsetWidth;
    card.classList.add('slide-in');
    document.getElementById('domain-name').textContent = domainInfo.domain || '';
    document.getElementById('domain-objective').textContent = domainInfo.objective || '';
    document.getElementById('domain-concept').textContent = domainInfo.key_concept || '';
    const tip = document.getElementById('domain-tip');
    tip.textContent = domainInfo.exam_tip || '';
    tip.className = 'cp-domain-value highlight';
}

// ── game over ─────────────────────────────────────────────────────────────────

function getRating(score, health) {
    const total = score + health;
    if (total >= 500) return 'S-TIER // ELITE NETRUNNER';
    if (total >= 400) return 'A-TIER // SENIOR ANALYST';
    if (total >= 300) return 'B-TIER // FIELD OPERATIVE';
    return 'C-TIER // ROOKIE AGENT';
}

function gameOver(won) {
    screenFlash();
    setTimeout(() => {
        document.getElementById('game-screen').classList.remove('active');
        const goScreen = document.getElementById('gameover-screen');
        goScreen.classList.add('active', 'fade-in');
        setTimeout(() => goScreen.classList.remove('fade-in'), 400);

        const title = document.getElementById('gameover-title');
        const msg = document.getElementById('gameover-msg');

        if (won) {
            title.textContent = '// MISSION COMPLETE — DEBRIEF';
            title.style.color = '#f5c518';

            const domainSummary = player.domain_scores
                ? Object.entries(player.domain_scores)
                    .filter(([, s]) => s.attempted > 0)
                    .map(([d, s]) => `
                        <div style="font-size:12px; color:#8888aa; margin-bottom:4px;">
                            <span style="color:#00d4ff; min-width:280px; display:inline-block;">${d}</span>
                            <span style="color:#f5c518;">${s.correct}/${s.attempted} correct</span>
                        </div>`).join('')
                : '';

            msg.innerHTML = `
                <p style="color:#f5c518; font-family:'Rajdhani',sans-serif; font-size:22px; letter-spacing:4px; margin-bottom:20px;">${getRating(player.score, player.health)}</p>
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

    }, 200);
}