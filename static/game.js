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