# all RPG scenario data lives here, imported by app.py
import random

PORT_SCENARIOS = [
    {'port': 23, 'service': 'Telnet', 'threat': True, 'reason': 'Telnet transmits all data including credentials in plain text. It should always be disabled and replaced with SSH.'},
    {'port': 443, 'service': 'HTTPS', 'threat': False, 'reason': 'HTTPS is expected on a web server and uses TLS encryption. Nothing suspicious here.'},
    {'port': 3389, 'service': 'RDP', 'threat': True, 'reason': 'RDP exposed directly to the internet is one of the most exploited attack vectors for ransomware deployment.'},
    {'port': 22, 'service': 'SSH', 'threat': False, 'reason': 'SSH is a secure encrypted protocol. Expected on Linux servers for remote administration.'},
    {'port': 21, 'service': 'FTP', 'threat': True, 'reason': 'FTP transmits credentials and data in plain text. Should be replaced with SFTP or FTPS.'},
    {'port': 1433, 'service': 'MSSQL', 'threat': True, 'reason': 'A SQL Server port exposed to the internet is a critical risk — databases should never be directly internet-facing.'},
    {'port': 8080, 'service': 'HTTP-Alt', 'threat': True, 'reason': 'An unencrypted web server on a non-standard port suggests a misconfigured or unauthorised service running on the network.'},
    {'port': 161, 'service': 'SNMP', 'threat': True, 'reason': 'SNMP v1/v2 uses community strings sent in plain text and is frequently exploited for network reconnaissance.'},
    {'port': 53, 'service': 'DNS', 'threat': False, 'reason': 'DNS on port 53 is expected on a nameserver. Only suspicious if seen on a workstation or non-DNS device.'},
    {'port': 445, 'service': 'SMB', 'threat': True, 'reason': 'SMB exposed to the internet is extremely dangerous — it was the attack vector for WannaCry and NotPetya ransomware.'},
    {'port': 3306, 'service': 'MySQL', 'threat': True, 'reason': 'MySQL should never be directly exposed to the internet. Database ports should only be accessible internally.'},
    {'port': 80, 'service': 'HTTP', 'threat': False, 'reason': 'HTTP on port 80 is standard for web servers though unencrypted. Acceptable for a public web server redirecting to HTTPS.'},
    {'port': 25, 'service': 'SMTP', 'threat': False, 'reason': 'SMTP on port 25 is expected on a mail server. Only suspicious on non-mail infrastructure.'},
    {'port': 5900, 'service': 'VNC', 'threat': True, 'reason': 'VNC exposed to the internet provides full desktop access and is frequently targeted by attackers for remote takeover.'},
    {'port': 2222, 'service': 'SSH-Alt', 'threat': False, 'reason': 'SSH on a non-standard port is a common hardening technique to reduce automated scanning noise. Not inherently suspicious.'}
]

LOG_SETS = [
    {
        'logs': [
            "09:14:22  user.login  alice@corp.com  IP: 192.168.1.5  SUCCESS",
            "09:15:01  user.login  bob@corp.com  IP: 185.220.101.45  SUCCESS  (TOR exit node)",
            "09:16:44  file.access  charlie@corp.com  IP: 192.168.1.8  SUCCESS"
        ],
        'answer': 1,
        'reason': 'Login from a TOR exit node is a major red flag — TOR is commonly used to anonymise malicious activity and bypass geo-restrictions.'
    },
    {
        'logs': [
            "14:02:11  admin.login  sysadmin  IP: 10.0.0.1  SUCCESS",
            "14:03:55  file.download  sysadmin  IP: 10.0.0.1  200 files downloaded",
            "14:04:01  admin.login  sysadmin  IP: 203.0.113.99  SUCCESS  (outside business hours)"
        ],
        'answer': 2,
        'reason': 'The same account logging in from two different IPs within 66 seconds is impossible without credential theft — this is a classic impossible travel indicator.'
    },
    {
        'logs': [
            "11:30:00  user.login  dave@corp.com  IP: 192.168.1.12  FAILED x5 then SUCCESS",
            "11:31:20  user.login  eve@corp.com  IP: 192.168.1.9  SUCCESS",
            "11:32:45  user.login  frank@corp.com  IP: 192.168.1.14  SUCCESS"
        ],
        'answer': 0,
        'reason': 'Five consecutive failed attempts followed by a success is a textbook brute force pattern — the attacker eventually guessed or cracked the password.'
    },
    {
        'logs': [
            "16:05:11  file.access  grace@corp.com  IP: 192.168.1.20  SUCCESS",
            "16:05:44  user.login  grace@corp.com  IP: 192.168.1.20  SUCCESS",
            "16:06:01  data.export  grace@corp.com  IP: 192.168.1.20  8500 records exported"
        ],
        'answer': 2,
        'reason': 'Exporting 8500 records within one minute of logging in is a strong data exfiltration indicator — normal users do not bulk export thousands of records.'
    },
    {
        'logs': [
            "02:14:33  user.login  henry@corp.com  IP: 41.78.92.14  SUCCESS  (Nigeria)",
            "08:55:12  user.login  henry@corp.com  IP: 192.168.1.6  SUCCESS  (office)",
            "09:01:44  file.access  ida@corp.com  IP: 192.168.1.11  SUCCESS"
        ],
        'answer': 0,
        'reason': 'A login at 2am from Nigeria followed by an office login 6 hours later is an impossible travel scenario — the user cannot physically be in both locations.'
    },
    {
        'logs': [
            "10:22:01  user.login  jack@corp.com  IP: 192.168.1.30  SUCCESS",
            "10:23:15  privilege.escalation  jack@corp.com  IP: 192.168.1.30  ADMIN_GRANTED",
            "10:24:00  user.login  kate@corp.com  IP: 192.168.1.25  SUCCESS"
        ],
        'answer': 1,
        'reason': 'Privilege escalation to admin immediately after login is a critical indicator of lateral movement — attackers escalate privileges to maximise access after initial compromise.'
    },
    {
        'logs': [
            "13:10:05  user.login  liam@corp.com  IP: 192.168.1.7  SUCCESS",
            "13:10:08  user.login  liam@corp.com  IP: 192.168.1.22  SUCCESS",
            "13:10:11  user.login  liam@corp.com  IP: 192.168.1.45  SUCCESS"
        ],
        'answer': 0,
        'reason': 'The same account logging in from three different internal IPs within 6 seconds indicates credential sharing or a compromised account being used by an automated tool.'
    },
    {
        'logs': [
            "15:44:20  file.access  mia@corp.com  IP: 192.168.1.8  SUCCESS",
            "15:45:01  user.login  noah@corp.com  IP: 192.168.1.14  SUCCESS",
            "15:46:33  dns.query  noah@corp.com  IP: 192.168.1.14  c2.malicious-domain.ru  x847 queries"
        ],
        'answer': 2,
        'reason': 'DNS beaconing to an external domain with hundreds of queries in under 2 minutes is a command-and-control (C2) communication pattern used by malware to receive instructions.'
    }
]

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

# extra password pools for more variety
PASSWORDS_EXTRA = [
    [
        {"password": "summer2024!", "weak": True},
        {"password": "mP9#kL2$vNx8", "weak": False},
        {"password": "welcome1", "weak": True},
        {"password": "Qx4!rW9@mKp3", "weak": False},
        {"password": "admin123", "weak": True},
        {"password": "Bv7$nR2!kXp5", "weak": False}
    ],
    [
        {"password": "football99", "weak": True},
        {"password": "hJ3$mPx8!kNv", "weak": False},
        {"password": "abc123", "weak": True},
        {"password": "Lp5#wQ9@rMx2", "weak": False},
        {"password": "dragon2023", "weak": True},
        {"password": "Nt8!vK3$pXm7", "weak": False}
    ],
    [
        {"password": "michael1985", "weak": True},
        {"password": "Wx6@kN4!rPm9", "weak": False},
        {"password": "sunshine", "weak": True},
        {"password": "Jv2$mL8#xKp5", "weak": False},
        {"password": "pass@word1", "weak": True},
        {"password": "Rn7!pX3$vKm4", "weak": False}
    ]
]

def get_random_passwords(hard_mode=False):
    if hard_mode:
        return PASSWORDS_HARD
    # randomly pick from easy set or one of the extra pools
    pool = [PASSWORDS_EASY] + PASSWORDS_EXTRA
    return random.choice(pool)

# maps each level to its Security+ domain
DOMAIN_MAP = {
    1: {
        'domain': 'Threats, Attacks & Vulnerabilities',
        'objective': '1.1 — Compare and contrast different types of social engineering techniques and password attacks',
        'key_concept': 'Weak passwords are one of the most exploited attack vectors. Dictionary attacks, brute force and credential stuffing all rely on weak or reused passwords. The Security+ exam expects you to know common attack types and mitigation strategies like MFA and password policies.',
        'exam_tip': 'Know the difference between brute force, dictionary attack, credential stuffing and password spraying.'
    },
    2: {
        'domain': 'Network Security',
        'objective': '3.3 — Given a scenario, implement secure network designs and protocols',
        'key_concept': 'Port scanning is a core reconnaissance technique. Understanding which ports and services are inherently insecure (Telnet, FTP, RDP exposed externally) versus expected is essential for network hardening. The exam tests your knowledge of common ports and their associated risks.',
        'exam_tip': 'Memorise common port numbers and their services. Know which are considered insecure and why.'
    },
    3: {
        'domain': 'Incident Response',
        'objective': '4.2 — Given a scenario, apply the appropriate incident response procedure',
        'key_concept': 'Log analysis is a fundamental incident response skill. Security analysts must identify indicators of compromise (IOCs) in log data. Common IOCs include impossible travel, brute force patterns, TOR exit nodes and unusual data access volumes.',
        'exam_tip': 'Understand the incident response lifecycle: Preparation, Identification, Containment, Eradication, Recovery, Lessons Learned.'
    }
}