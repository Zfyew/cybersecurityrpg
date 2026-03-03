// game state
let player = null;
let currentLevel = null;
let selectedLog = null;

// stagger the intro lines so they appear one by one
function animateIntro() {
    const lines = document.querySelectorAll('.type-line');
    lines.forEach((line, i) => {
        line.style.animationDelay = `${i * 0.4}s`;
    });
}

animateIntro();

async function startGame() {
    const name = document.getElementById('player-name').value.trim();
    if (!name) {
        document.getElementById('player-name').focus();
        return;
    }

    const res = await fetch('/api/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name })
    });

    const data = await res.json();
    player = data.player;

    document.getElementById('intro-screen').classList.remove('active');
    document.getElementById('game-screen').classList.add('active');
    updateHUD();
}

// allow pressing Enter on the name input
document.getElementById('player-name').addEventListener('keydown', e => {
    if (e.key === 'Enter') startGame();
});

function updateHUD() {
    if (!player) return;
    document.getElementById('hud-name').textContent = player.name;
    document.getElementById('hud-health').textContent = player.health;
    document.getElementById('hud-score').textContent = player.score;
    document.getElementById('hud-tools').textContent = player.inventory.length ? player.inventory.join(', ') : 'None';

    const bar = document.getElementById('health-bar');
    bar.style.width = player.health + '%';
    bar.style.background = player.health > 60 ? '#00ff41' : player.health > 30 ? '#ffbd2e' : '#ff4444';

    const completed = player.completed || [];

    for (let i = 1; i <= 3; i++) {
        const card = document.getElementById(`level-${i}-card`);
        const status = document.getElementById(`level-${i}-status`);

        if (completed.includes(i)) {
            // completed — show as done, not clickable
            card.classList.remove('locked');
            card.style.opacity = '0.4';
            card.style.cursor = 'not-allowed';
            status.textContent = 'COMPLETE';
            card.onclick = null;
        } else if (i <= player.level) {
            card.classList.remove('locked');
            card.style.opacity = '1';
            card.style.cursor = 'pointer';
            status.textContent = 'AVAILABLE';
            card.onclick = () => loadLevel(i);
        } else {
            card.classList.add('locked');
            card.style.opacity = '1';
            status.textContent = 'LOCKED';
            card.onclick = null;
        }
    }

    if (player.health <= 0) gameOver(false);
}

function showLevelSelect() {
    document.getElementById('level-panel').classList.remove('active');
    document.getElementById('level-select').classList.add('active');
    document.getElementById('feedback').classList.add('hidden');
}

async function loadLevel(num) {
    currentLevel = num;
    selectedLog = null;

    const res = await fetch(`/api/level/${num}`);
    if (!res.ok) return;
    const data = await res.json();

    document.getElementById('level-select').classList.remove('active');
    document.getElementById('level-panel').classList.add('active');
    document.getElementById('level-title').textContent = `// ${data.title.toUpperCase()}`;
    document.getElementById('level-desc').textContent = data.description;
    document.getElementById('feedback').classList.add('hidden');
    document.getElementById('feedback').className = 'feedback hidden';

    const content = document.getElementById('level-content');
    content.innerHTML = '';

    if (data.type === 'password') renderPasswordLevel(data, content);
    else if (data.type === 'port') renderPortLevel(data, content);
    else if (data.type === 'logs') renderLogLevel(data, content);
}

function renderPasswordLevel(data, container) {
    const grid = document.createElement('div');
    grid.className = 'password-grid';

    data.passwords.forEach((p, i) => {
        const btn = document.createElement('button');
        btn.className = 'password-btn';
        btn.textContent = p.password;
        btn.onclick = () => submitAnswer(i);
        grid.appendChild(btn);
    });

    container.appendChild(grid);
}

function renderPortLevel(data, container) {
    // animate the scan output line by line
    const output = document.createElement('div');
    output.className = 'scan-output';

    const lines = [
        `> initiating port scan...`,
        `> target: 192.168.1.${Math.floor(Math.random() * 254) + 1}`,
        `> scanning common ports...`,
        `>`,
        `> PORT     SERVICE    STATE`,
        `> ──────────────────────────`,
        `> ${String(data.port).padEnd(9)}${data.service.padEnd(11)}OPEN`,
        `>`,
        `> scan complete.`
    ];

    lines.forEach((line, i) => {
        const p = document.createElement('p');
        p.className = 'scan-line';
        p.textContent = line;
        output.appendChild(p);
        // stagger each line appearing
        setTimeout(() => p.classList.add('visible'), i * 200);
    });

    container.appendChild(output);

    const actions = document.createElement('div');
    actions.className = 'port-actions';

    const blockBtn = document.createElement('button');
    blockBtn.className = 'btn-block';
    blockBtn.textContent = 'BLOCK PORT';
    blockBtn.onclick = () => submitAnswer(true);

    const allowBtn = document.createElement('button');
    allowBtn.className = 'btn-allow';
    allowBtn.textContent = 'LEAVE OPEN';
    allowBtn.onclick = () => submitAnswer(false);

    actions.appendChild(blockBtn);
    actions.appendChild(allowBtn);
    container.appendChild(actions);
}

function renderLogLevel(data, container) {
    const intro = document.createElement('p');
    intro.style.cssText = 'color:#888; margin-bottom:16px; font-size:13px;';
    intro.textContent = 'Click the suspicious log entry then confirm your selection.';
    container.appendChild(intro);

    data.logs.forEach((log, i) => {
        const entry = document.createElement('div');
        entry.className = 'log-entry';
        entry.textContent = log;
        entry.onclick = () => {
            document.querySelectorAll('.log-entry').forEach(e => e.classList.remove('selected'));
            entry.classList.add('selected');
            selectedLog = i;
        };
        container.appendChild(entry);
    });

    const confirmBtn = document.createElement('button');
    confirmBtn.style.marginTop = '20px';
    confirmBtn.textContent = 'CONFIRM SELECTION';
    confirmBtn.onclick = () => {
        if (selectedLog === null) return;
        submitAnswer(selectedLog);
    };
    container.appendChild(confirmBtn);
}

async function submitAnswer(answer) {
    const res = await fetch('/api/answer', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ level: currentLevel, answer })
    });

    const data = await res.json();
    player = data.player;
    updateHUD();

    const feedback = document.getElementById('feedback');
    feedback.classList.remove('hidden', 'wrong');

    if (data.correct) {
        feedback.textContent = `✓ Correct. ${data.reason} +${data.points} points.`;
        if (player.level > currentLevel || currentLevel === 3) {
            const nextBtn = document.createElement('button');
            nextBtn.className = 'next-btn';
            nextBtn.textContent = currentLevel === 3 ? 'VIEW RESULTS' : 'NEXT MISSION →';
            nextBtn.onclick = currentLevel === 3 ? () => gameOver(true) : showLevelSelect;
            feedback.appendChild(document.createElement('br'));
            feedback.appendChild(nextBtn);
        }
    } else {
        feedback.classList.add('wrong');
        feedback.textContent = `✗ Wrong call. ${data.reason} -25 health.`;
        const retryBtn = document.createElement('button');
        retryBtn.className = 'next-btn';
        retryBtn.textContent = 'TRY AGAIN';
        retryBtn.onclick = () => loadLevel(currentLevel);
        feedback.appendChild(document.createElement('br'));
        feedback.appendChild(retryBtn);
    }
}

function gameOver(won) {
    document.getElementById('game-screen').classList.remove('active');
    document.getElementById('gameover-screen').classList.add('active');

    const msg = document.getElementById('gameover-msg');
    if (won) {
        msg.innerHTML = `
            <p style="color:#00ff41; font-size:18px; margin-bottom:16px;">// MISSION COMPLETE</p>
            <p>Agent: ${player.name}</p>
            <p>Final score: ${player.score}</p>
            <p>Health remaining: ${player.health}</p>
            <p>Tools acquired: ${player.inventory.join(', ') || 'None'}</p>
            <br>
            <p style="color:#888;">All threats neutralised.</p>
        `;
    } else {
        msg.innerHTML = `
            <p style="color:#ff4444; font-size:18px; margin-bottom:16px;">// AGENT DOWN</p>
            <p>Agent: ${player.name}</p>
            <p>Final score: ${player.score}</p>
            <p style="color:#888; margin-top:12px;">You ran out of health.</p>
        `;
    }
}