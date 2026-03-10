# CyberSec RPG

A browser-based cybersecurity training game built with Flask and vanilla JavaScript. Players work through four randomised missions drawn from a pool of eleven scenario types, with an interactive mini-game as the final level. Every scenario maps to a CompTIA Security+ SY0-701 exam objective, making the game useful for both entertainment and certification preparation.

![Python](https://img.shields.io/badge/Python-3.10+-blue) ![Flask](https://img.shields.io/badge/Flask-3.0-lightgrey) ![JavaScript](https://img.shields.io/badge/JavaScript-ES2022-yellow) ![License](https://img.shields.io/badge/License-MIT-green)

---

## Features

- **11 scenario types** across 4 levels — password cracking, port scanning, breach investigation, social engineering, malware analysis, cryptography, access control, vulnerability assessment, terminal hacking, packet tracer, brute force intercept
- **Fully randomised sessions** — levels 1–3 draw randomly from 8 scenario types each run, level 4 is always a mini-game chosen from 3
- **Security+ SY0-701 alignment** — every scenario maps to an exam domain with a domain card shown after each correct answer
- **AI mode** — optional Claude integration generates unique scenarios each run via the Anthropic API
- **Hard mode** — unlocks after completing a full run, increases damage penalties and score multipliers
- **Domain tracker** — live HUD tracks correct/attempted per Security+ domain across the session
- **Cyberpunk 2077 aesthetic** — Rajdhani and Share Tech Mono fonts, CRT scanlines, glitch animations, falling line background

---

## Scenario Types

| Level | Type | Security+ Domain | Objective |
|-------|------|-----------------|-----------|
| 1–3 | Password Cracking | Threats, Attacks & Vulnerabilities | 1.1 |
| 1–3 | Port Scanning | Network Security | 3.3 |
| 1–3 | Breach Investigation | Incident Response | 4.2 |
| 1–3 | Social Engineering | Threats, Attacks & Vulnerabilities | 1.1 |
| 1–3 | Malware Analysis | Threats, Attacks & Vulnerabilities | 1.2 |
| 1–3 | Cryptography | Implementation | 3.2 |
| 1–3 | Access Control | Architecture & Design | 2.1 |
| 1–3 | Vulnerability Assessment | Operations & Incident Response | 4.1 |
| 4 | Terminal Hacking | Operations & Incident Response | 4.1 |
| 4 | Packet Tracer | Network Security | 3.3 |
| 4 | Brute Force Intercept | Implementation | 3.2 |

---

## Setup

**Requirements:** Python 3.10+
```bash
git clone https://github.com/Zfyew/cybersecurityrpg
cd cybersecurityrpg
pip install flask
python app.py
```

Open `http://localhost:5000` in your browser.

---

## AI Mode

AI mode uses the Anthropic API to generate unique scenarios each run instead of drawing from the static pool.

1. Select **Neural Net Mode** on the start screen
2. Enter your Anthropic API key
3. Choose a model — Sonnet 4.6 is recommended for the best balance of speed and quality

AI-generated scenarios are supported for password, port and log levels. All four mini-game types always use static scenarios. The game falls back to static scenarios automatically if the API is unreachable.

Get an API key at [console.anthropic.com](https://console.anthropic.com).

---

## Project Structure
```
cybersecurityrpg/
├── app.py                  # Flask server, API routes, session management
├── data/
│   ├── rpg_scenarios.py    # All scenario data — 11 types, mini-games, domain maps
│   └── security_plus.py    # 30-question Security+ exam bank across 5 domains
├── templates/
│   └── index.html          # Single-page game UI
├── static/
│   ├── style.css           # Cyberpunk theme, responsive for 1080p and 1440p
│   └── game.js             # Game logic, rendering, transitions, mini-games
└── README.md
```

---

## Game Mechanics

| Action | Normal | Hard Mode |
|--------|--------|-----------|
| Level 1 correct | 100 pts | 150 pts |
| Level 2 correct | 200 pts | 300 pts |
| Level 3 correct | 300 pts | 450 pts |
| Level 4 correct | 400 pts | 600 pts |
| Wrong answer | −25 integrity | −35 integrity |
| Complete all 4 levels | +20 integrity, hard mode unlocks | +20 integrity |

**Performance ratings after debrief:**

| Rating | Threshold |
|--------|-----------|
| S-Tier — Elite Netrunner | 600+ |
| A-Tier — Senior Analyst | 450+ |
| B-Tier — Field Operative | 300+ |
| C-Tier — Rookie Agent | Below 300 |

---

## Mini-Games

**Terminal Hacking** — breach a target system by entering the correct sequence of penetration testing commands. Wrong commands cost integrity but the terminal stays open.

**Packet Tracer** — route a packet through an SVG network diagram from source to target. Avoid untrusted nodes such as DMZ servers and unencrypted proxies. Click nodes to build your path then transmit.

**Brute Force Intercept** — three intercepted password hashes are shown with animated crack progress bars running at speeds based on algorithm strength. Identify and click the weakest hash before the attacker cracks it.

---

## Built With

- [Flask](https://flask.palletsprojects.com/) — Python web framework
- [Anthropic API](https://docs.anthropic.com/) — Claude AI for dynamic scenario generation
- [Rajdhani](https://fonts.google.com/specimen/Rajdhani) / [Share Tech Mono](https://fonts.google.com/specimen/Share+Tech+Mono) — Google Fonts
- Vanilla JavaScript — no frontend framework or build tools required

---

## License

MIT
