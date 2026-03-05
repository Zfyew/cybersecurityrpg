import random

PORT_SCENARIOS = [
    {'port': 23, 'service': 'Telnet', 'threat': True, 'reason': 'Telnet transmits all data including credentials in plain text. It should always be disabled and replaced with SSH.'},
    {'port': 443, 'service': 'HTTPS', 'threat': False, 'reason': 'HTTPS is expected on a web server and uses TLS encryption. Nothing suspicious here.'},
    {'port': 3389, 'service': 'RDP', 'threat': True, 'reason': 'RDP exposed directly to the internet is one of the most exploited attack vectors for ransomware deployment.'},
    {'port': 22, 'service': 'SSH', 'threat': False, 'reason': 'SSH is a secure encrypted protocol. Expected on Linux servers for remote administration.'},
    {'port': 21, 'service': 'FTP', 'threat': True, 'reason': 'FTP transmits credentials and data in plain text. Should be replaced with SFTP or FTPS.'},
    {'port': 1433, 'service': 'MSSQL', 'threat': True, 'reason': 'A SQL Server port exposed to the internet is a critical risk — databases should never be directly internet-facing.'},
    {'port': 8080, 'service': 'HTTP-Alt', 'threat': True, 'reason': 'An unencrypted web server on a non-standard port suggests a misconfigured or unauthorised service.'},
    {'port': 161, 'service': 'SNMP', 'threat': True, 'reason': 'SNMP v1/v2 uses community strings sent in plain text and is frequently exploited for network reconnaissance.'},
    {'port': 53, 'service': 'DNS', 'threat': False, 'reason': 'DNS on port 53 is expected on a nameserver. Only suspicious if seen on a workstation.'},
    {'port': 445, 'service': 'SMB', 'threat': True, 'reason': 'SMB exposed to the internet is extremely dangerous — it was the attack vector for WannaCry and NotPetya ransomware.'},
    {'port': 3306, 'service': 'MySQL', 'threat': True, 'reason': 'MySQL should never be directly exposed to the internet. Database ports should only be accessible internally.'},
    {'port': 80, 'service': 'HTTP', 'threat': False, 'reason': 'HTTP on port 80 is standard for web servers. Acceptable for a public web server redirecting to HTTPS.'},
    {'port': 25, 'service': 'SMTP', 'threat': False, 'reason': 'SMTP on port 25 is expected on a mail server. Only suspicious on non-mail infrastructure.'},
    {'port': 5900, 'service': 'VNC', 'threat': True, 'reason': 'VNC exposed to the internet provides full desktop access and is frequently targeted for remote takeover.'},
    {'port': 2222, 'service': 'SSH-Alt', 'threat': False, 'reason': 'SSH on a non-standard port is a common hardening technique to reduce automated scanning noise.'}
]

LOG_SETS = [
    {
        'logs': [
            "09:14:22  user.login  alice@corp.com  IP: 192.168.1.5  SUCCESS",
            "09:15:01  user.login  bob@corp.com  IP: 185.220.101.45  SUCCESS  (TOR exit node)",
            "09:16:44  file.access  charlie@corp.com  IP: 192.168.1.8  SUCCESS"
        ],
        'answer': 1,
        'reason': 'Login from a TOR exit node is a major red flag — TOR is commonly used to anonymise malicious activity.'
    },
    {
        'logs': [
            "14:02:11  admin.login  sysadmin  IP: 10.0.0.1  SUCCESS",
            "14:03:55  file.download  sysadmin  IP: 10.0.0.1  200 files downloaded",
            "14:04:01  admin.login  sysadmin  IP: 203.0.113.99  SUCCESS  (outside business hours)"
        ],
        'answer': 2,
        'reason': 'The same account logging in from two different IPs within 66 seconds is impossible without credential theft — classic impossible travel.'
    },
    {
        'logs': [
            "11:30:00  user.login  dave@corp.com  IP: 192.168.1.12  FAILED x5 then SUCCESS",
            "11:31:20  user.login  eve@corp.com  IP: 192.168.1.9  SUCCESS",
            "11:32:45  user.login  frank@corp.com  IP: 192.168.1.14  SUCCESS"
        ],
        'answer': 0,
        'reason': 'Five consecutive failed attempts followed by a success is a textbook brute force pattern.'
    },
    {
        'logs': [
            "16:05:11  file.access  grace@corp.com  IP: 192.168.1.20  SUCCESS",
            "16:05:44  user.login  grace@corp.com  IP: 192.168.1.20  SUCCESS",
            "16:06:01  data.export  grace@corp.com  IP: 192.168.1.20  8500 records exported"
        ],
        'answer': 2,
        'reason': 'Exporting 8500 records within one minute of logging in is a strong data exfiltration indicator.'
    },
    {
        'logs': [
            "02:14:33  user.login  henry@corp.com  IP: 41.78.92.14  SUCCESS  (Nigeria)",
            "08:55:12  user.login  henry@corp.com  IP: 192.168.1.6  SUCCESS  (office)",
            "09:01:44  file.access  ida@corp.com  IP: 192.168.1.11  SUCCESS"
        ],
        'answer': 0,
        'reason': 'A login at 2am from Nigeria followed by an office login 6 hours later is an impossible travel scenario.'
    },
    {
        'logs': [
            "10:22:01  user.login  jack@corp.com  IP: 192.168.1.30  SUCCESS",
            "10:23:15  privilege.escalation  jack@corp.com  IP: 192.168.1.30  ADMIN_GRANTED",
            "10:24:00  user.login  kate@corp.com  IP: 192.168.1.25  SUCCESS"
        ],
        'answer': 1,
        'reason': 'Privilege escalation to admin immediately after login is a critical indicator of lateral movement.'
    },
    {
        'logs': [
            "13:10:05  user.login  liam@corp.com  IP: 192.168.1.7  SUCCESS",
            "13:10:08  user.login  liam@corp.com  IP: 192.168.1.22  SUCCESS",
            "13:10:11  user.login  liam@corp.com  IP: 192.168.1.45  SUCCESS"
        ],
        'answer': 0,
        'reason': 'The same account logging in from three different IPs within 6 seconds indicates an automated tool or compromised credentials.'
    },
    {
        'logs': [
            "15:44:20  file.access  mia@corp.com  IP: 192.168.1.8  SUCCESS",
            "15:45:01  user.login  noah@corp.com  IP: 192.168.1.14  SUCCESS",
            "15:46:33  dns.query  noah@corp.com  IP: 192.168.1.14  c2.malicious-domain.ru  x847 queries"
        ],
        'answer': 2,
        'reason': 'DNS beaconing to an external domain with hundreds of queries is a command-and-control communication pattern used by malware.'
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
    pool = [PASSWORDS_EASY] + PASSWORDS_EXTRA
    return random.choice(pool)

# social engineering scenarios
SOCIAL_ENGINEERING_SCENARIOS = [
    {
        'email': {
            'from': 'it-support@c0rp-helpdesk.com',
            'subject': 'URGENT: Your account will be suspended in 24 hours',
            'body': 'Dear Employee, Our systems have detected unusual activity on your account. You must verify your credentials immediately or your account will be permanently suspended. Click here to verify: http://corp-login.suspicious-domain.ru/verify'
        },
        'flags': [
            'Sender domain is misspelled — c0rp not corp',
            'Urgency tactics to pressure immediate action',
            'Link goes to a suspicious external domain (.ru)',
            'Threatening language about account suspension'
        ],
        'question': 'How many red flags can you identify in this email?',
        'options': ['1 red flag', '2 red flags', '3 red flags', '4 red flags'],
        'answer': 3,
        'reason': 'There are 4 red flags: misspelled sender domain, urgency/pressure tactics, suspicious external link, and threatening language — all classic phishing indicators.'
    },
    {
        'email': {
            'from': 'ceo.johnson@company-secure.net',
            'subject': 'Confidential wire transfer needed — do not discuss',
            'body': 'Hi, I\'m in a meeting and need you to urgently process a wire transfer of $47,500 to a new vendor. This is time sensitive and confidential. Do not discuss with anyone. I will explain later. Send confirmation to this email only.'
        },
        'flags': [
            'CEO email domain does not match company domain',
            'Requests financial action urgently',
            'Instructs recipient to keep it secret',
            'Asks for confirmation to external email'
        ],
        'question': 'This is an example of which attack type?',
        'options': ['Phishing', 'Whaling / BEC', 'Smishing', 'Vishing'],
        'answer': 1,
        'reason': 'This is a Business Email Compromise (BEC) / whaling attack — impersonating a CEO to authorise fraudulent financial transactions. BEC attacks cost businesses billions annually.'
    },
    {
        'email': {
            'from': 'noreply@paypa1.com',
            'subject': 'Your payment of $299.99 has been processed',
            'body': 'Thank you for your purchase. A payment of $299.99 has been charged to your account ending in 4832. If you did not authorise this transaction, call us immediately at 1-800-555-0199 or click here to dispute: http://paypal-dispute.fakesite.com'
        },
        'flags': [
            'Domain is paypa1.com — the l is replaced with a 1',
            'Creates panic about unauthorised charge',
            'Phone number provided cannot be verified',
            'Dispute link goes to a fake domain'
        ],
        'question': 'What technique does this email primarily use?',
        'options': ['Baiting', 'Pretexting', 'Fear and urgency', 'Quid pro quo'],
        'answer': 2,
        'reason': 'This phishing email uses fear and urgency — fabricating an unauthorised charge to panic the recipient into clicking a malicious link or calling a fake support number.'
    }
]

# malware analysis scenarios
MALWARE_SCENARIOS = [
    {
        'description': 'A workstation is exhibiting the following behaviour:',
        'behaviours': [
            'CPU usage spikes to 95% overnight when no user is logged in',
            'Outbound connections to multiple cryptocurrency pool addresses detected',
            'System fan running constantly at maximum speed',
            'No user-visible popups or file changes observed'
        ],
        'question': 'What type of malware is most likely responsible?',
        'options': ['Ransomware', 'Cryptojacker', 'Keylogger', 'Rootkit'],
        'answer': 1,
        'reason': 'Cryptojacking malware hijacks system resources to mine cryptocurrency in the background. Key indicators are high CPU usage when idle and connections to crypto mining pools — with no visible symptoms to the user.'
    },
    {
        'description': 'A finance department workstation shows these indicators:',
        'behaviours': [
            'All files on the local drive and mapped network shares now have .locked extension',
            'Desktop wallpaper changed to a ransom note',
            'A README_DECRYPT.txt file appears in every folder',
            'Network activity shows large outbound transfers before file changes began'
        ],
        'question': 'What should be the FIRST response action?',
        'options': [
            'Pay the ransom to recover files quickly',
            'Reimage the workstation immediately',
            'Isolate the device from the network immediately',
            'Run antivirus to remove the malware'
        ],
        'answer': 2,
        'reason': 'Immediate network isolation is the correct first step — the malware already encrypted network shares showing it is spreading. Isolation prevents further damage. Evidence must be preserved before reimaging.'
    },
    {
        'description': 'Security tools flag the following on an executive laptop:',
        'behaviours': [
            'A process named svchost32.exe is running from C:\\Users\\AppData\\Temp',
            'The process is capturing keystrokes and sending them to 185.220.x.x every 60 seconds',
            'No alerts triggered at the time of initial infection 3 weeks ago',
            'The process restarts automatically after being manually killed'
        ],
        'question': 'What combination of malware characteristics does this exhibit?',
        'options': [
            'Ransomware with persistence mechanism',
            'Keylogger with C2 exfiltration and persistence',
            'Worm with lateral movement capability',
            'Adware with tracking functionality'
        ],
        'answer': 1,
        'reason': 'This is a keylogger with command-and-control exfiltration and persistence — it captures credentials, sends them to an attacker-controlled server every 60 seconds, and uses auto-restart to survive reboots.'
    }
]

# cryptography scenarios
CRYPTO_SCENARIOS = [
    {
        'scenario': 'A healthcare company needs to store patient records in a database. The records must be protected so that even if the database is stolen, the data cannot be read. The data also needs to be searchable.',
        'question': 'Which approach is most appropriate?',
        'options': [
            'Encrypt the entire database with AES-256',
            'Hash all records with SHA-256',
            'Encrypt sensitive fields with AES-256, store non-sensitive fields in plain text',
            'Use Base64 encoding on all records'
        ],
        'answer': 2,
        'reason': 'Field-level AES-256 encryption protects sensitive data while keeping non-sensitive fields searchable. Full database encryption prevents searching. Hashing is one-way and cannot be decrypted. Base64 is encoding not encryption.'
    },
    {
        'scenario': 'A developer needs to store user passwords in a database. The passwords must never be recoverable even by database administrators.',
        'question': 'Which method should be used?',
        'options': [
            'AES-256 encryption with a master key',
            'MD5 hashing',
            'bcrypt hashing with a unique salt per user',
            'SHA-1 hashing'
        ],
        'answer': 2,
        'reason': 'bcrypt with unique salts is the correct approach — it is a slow one-way hash designed for passwords, making brute force attacks impractical. MD5 and SHA-1 are fast and broken. AES is reversible and inappropriate for passwords.'
    },
    {
        'scenario': 'Two companies need to securely exchange an encryption key over an untrusted public network for the first time, without having met before.',
        'question': 'Which protocol enables this?',
        'options': [
            'AES key exchange',
            'Diffie-Hellman key exchange',
            'RSA direct transmission',
            'SHA-256 key derivation'
        ],
        'answer': 1,
        'reason': 'Diffie-Hellman allows two parties to establish a shared secret over an insecure channel without transmitting the key itself. This is the foundation of TLS and many modern secure protocols.'
    }
]

# access control scenarios
ACCESS_CONTROL_SCENARIOS = [
    {
        'request': {
            'user': 'Sarah Chen — Marketing Manager',
            'requesting': 'Full read/write access to the finance database',
            'justification': 'I sometimes need to pull revenue figures for marketing reports'
        },
        'question': 'Should this access request be approved as submitted?',
        'options': [
            'Yes — managers should have broad access',
            'No — grant read-only access to a specific reporting view instead',
            'No — deny completely, marketing should never see financial data',
            'Yes — the justification is reasonable'
        ],
        'answer': 1,
        'reason': 'Least privilege principle — grant only the minimum access needed. Read-only access to a specific reporting view satisfies the business need without exposing the full finance database to write access.'
    },
    {
        'request': {
            'user': 'James Porter — IT Help Desk Technician',
            'requesting': 'Domain Admin privileges',
            'justification': 'I need to reset user passwords and unlock accounts daily'
        },
        'question': 'What is the correct response?',
        'options': [
            'Approve — help desk needs admin access to do their job',
            'Deny — help desk should have no elevated privileges',
            'Approve a limited delegated permission to reset passwords only',
            'Escalate to the CISO for approval'
        ],
        'answer': 2,
        'reason': 'Domain Admin is far more than needed for password resets. Delegated permissions allow specific tasks like password resets without granting full domain control — this is the least privilege principle in practice.'
    },
    {
        'request': {
            'user': 'Automated backup service account',
            'requesting': 'Local administrator rights on all 200 workstations',
            'justification': 'Required to access all folders during nightly backup jobs'
        },
        'question': 'What is the security concern with this request?',
        'options': [
            'Service accounts should never run backups',
            'A compromised service account with local admin on 200 machines enables rapid lateral movement across the entire estate',
            'The backup schedule is outside business hours which is suspicious',
            'There is no security concern — this is standard practice'
        ],
        'answer': 1,
        'reason': 'Over-privileged service accounts are a critical risk — if compromised they become a master key to the entire environment. The correct approach is granular permissions scoped only to backup directories.'
    }
]

# vulnerability scenarios
VULNERABILITY_SCENARIOS = [
    {
        'cve': 'CVE-2021-44228 (Log4Shell)',
        'description': 'A critical RCE vulnerability in Apache Log4j allows attackers to execute arbitrary code by sending a specially crafted string to any application that logs user input using Log4j.',
        'cvss': '10.0 CRITICAL',
        'affected': 'Any Java application using Log4j 2.0-beta9 through 2.14.1',
        'question': 'What is the correct immediate mitigation priority?',
        'options': [
            'Disable all Java applications until patched',
            'Apply the Log4j patch to 2.15.0+, identify all affected systems, implement WAF rules to block exploit strings',
            'Monitor logs for exploit attempts and respond if detected',
            'Isolate the internet-facing servers only'
        ],
        'answer': 1,
        'reason': 'Log4Shell (CVSS 10.0) requires immediate patching of all affected Log4j instances, full asset discovery to find every affected system, and WAF rules as a temporary control — in that priority order.'
    },
    {
        'cve': 'CVE-2017-0144 (EternalBlue)',
        'description': 'A vulnerability in the Windows SMB protocol allows remote code execution without authentication. Exploited by WannaCry and NotPetya ransomware campaigns affecting hundreds of thousands of systems.',
        'cvss': '9.8 CRITICAL',
        'affected': 'Windows XP through Windows Server 2008 R2 without MS17-010 patch',
        'question': 'An organisation has 50 unpatched Windows Server 2008 R2 machines that cannot be immediately patched due to legacy application dependencies. What is the best interim control?',
        'options': [
            'Accept the risk until applications can be migrated',
            'Disable SMBv1 and block port 445 at the network perimeter and between segments',
            'Install antivirus on all 50 servers',
            'Move servers to a separate VLAN with no controls'
        ],
        'answer': 1,
        'reason': 'Disabling SMBv1 removes the vulnerable protocol and blocking port 445 at network boundaries prevents exploitation while patching is planned — defence in depth without requiring immediate downtime.'
    },
    {
        'cve': 'SQL Injection — OWASP A03:2021',
        'description': 'A web application passes unsanitised user input directly into SQL queries. An attacker can manipulate queries to extract, modify or delete database contents.',
        'cvss': '9.1 CRITICAL',
        'affected': 'Web application login form and search functionality',
        'question': 'Which fix addresses the root cause rather than just reducing exposure?',
        'options': [
            'Deploy a Web Application Firewall to block SQL injection patterns',
            'Implement parameterised queries / prepared statements in the application code',
            'Restrict database user permissions to read-only',
            'Rate limit login attempts to slow down attacks'
        ],
        'answer': 1,
        'reason': 'Parameterised queries fix the root cause by separating SQL code from user data — the database never interprets user input as code. WAF and permission restrictions are compensating controls, not fixes.'
    }
]

# all scenario types available for random selection
ALL_SCENARIO_TYPES = [
    'password',
    'port',
    'logs',
    'social_engineering',
    'malware',
    'cryptography',
    'access_control',
    'vulnerability'
]

# domain mappings for all scenario types
DOMAIN_MAP = {
    'password': {
        'domain': 'Threats, Attacks & Vulnerabilities',
        'objective': '1.1 — Compare and contrast different types of password attacks',
        'key_concept': 'Weak passwords are one of the most exploited attack vectors. Dictionary attacks, brute force and credential stuffing all rely on weak or reused passwords.',
        'exam_tip': 'Know the difference between brute force, dictionary attack, credential stuffing and password spraying.'
    },
    'port': {
        'domain': 'Network Security',
        'objective': '3.3 — Given a scenario, implement secure network designs',
        'key_concept': 'Understanding which ports are inherently insecure is essential for network hardening. Telnet, FTP and RDP exposed externally are common attack vectors.',
        'exam_tip': 'Memorise common port numbers and their services. Know which are considered insecure and why.'
    },
    'logs': {
        'domain': 'Incident Response',
        'objective': '4.2 — Given a scenario, apply the appropriate incident response procedure',
        'key_concept': 'Log analysis is a fundamental incident response skill. Common IOCs include impossible travel, brute force patterns, TOR nodes and unusual data access.',
        'exam_tip': 'Understand the incident response lifecycle: Preparation, Identification, Containment, Eradication, Recovery, Lessons Learned.'
    },
    'social_engineering': {
        'domain': 'Threats, Attacks & Vulnerabilities',
        'objective': '1.1 — Compare and contrast different types of social engineering techniques',
        'key_concept': 'Social engineering exploits human psychology rather than technical vulnerabilities. Phishing, whaling and BEC attacks rely on urgency, authority and fear.',
        'exam_tip': 'Know the difference between phishing, spear phishing, whaling, vishing, smishing and BEC attacks.'
    },
    'malware': {
        'domain': 'Threats, Attacks & Vulnerabilities',
        'objective': '1.2 — Given a scenario, analyse potential indicators to determine the type of attack',
        'key_concept': 'Different malware types leave different indicators. Ransomware encrypts files, cryptojackers consume CPU, keyloggers exfiltrate keystrokes, rootkits hide their presence.',
        'exam_tip': 'Be able to identify malware type from behavioural indicators — file changes, network connections, CPU usage, persistence mechanisms.'
    },
    'cryptography': {
        'domain': 'Implementation',
        'objective': '3.2 — Given a scenario, implement cryptographic protocols',
        'key_concept': 'Choosing the right cryptographic approach depends on the use case. Symmetric encryption for bulk data, asymmetric for key exchange, hashing for integrity and passwords.',
        'exam_tip': 'Know AES, RSA, Diffie-Hellman, SHA, bcrypt and when each is appropriate. Know why MD5 and SHA-1 are deprecated.'
    },
    'access_control': {
        'domain': 'Architecture & Design',
        'objective': '2.1 — Explain the importance of security concepts in an enterprise environment',
        'key_concept': 'Least privilege means granting only the minimum access required. Over-privileged accounts are a major attack surface — especially service accounts.',
        'exam_tip': 'Understand least privilege, separation of duties, need-to-know and zero trust. Know how they apply to both users and service accounts.'
    },
    'vulnerability': {
        'domain': 'Operations & Incident Response',
        'objective': '4.1 — Given a scenario, use the appropriate tool to assess organisational security',
        'key_concept': 'Vulnerability management involves identifying, prioritising and remediating vulnerabilities. CVSS scores indicate severity. Patching is the fix — WAFs and network controls are compensating controls.',
        'exam_tip': 'Understand CVE, CVSS scoring and the difference between a fix (patching, code change) and a compensating control (WAF, network block).'
    }
}

# titles and descriptions for each scenario type
SCENARIO_META = {
    'password': {
        'title': 'Password Cracking',
        'description': 'A user account has been flagged. Identify the weakest password before the attacker does.'
    },
    'port': {
        'title': 'Port Scanning',
        'description': 'An unknown device appeared on the network. Analyse the open port and decide whether to block it.'
    },
    'logs': {
        'title': 'Breach Investigation',
        'description': 'Alerts are firing. Read the logs and identify which entry shows the attacker.'
    },
    'social_engineering': {
        'title': 'Social Engineering',
        'description': 'An email has been flagged by your filtering system. Analyse it for phishing indicators.'
    },
    'malware': {
        'title': 'Malware Analysis',
        'description': 'Endpoint telemetry has flagged unusual behaviour. Identify the threat and the correct response.'
    },
    'cryptography': {
        'title': 'Cryptography',
        'description': 'A developer needs your advice on protecting sensitive data. Choose the correct cryptographic approach.'
    },
    'access_control': {
        'title': 'Access Control',
        'description': 'A user has submitted an access request. Evaluate it against the principle of least privilege.'
    },
    'vulnerability': {
        'title': 'Vulnerability Assessment',
        'description': 'A critical CVE has been identified in your environment. Determine the correct mitigation strategy.'
    }
}

# ── mini-game scenarios ───────────────────────────────────────────────────────

TERMINAL_SCENARIOS = [
    {
        'objective': 'Gain access to the target server at 10.0.0.47',
        'target': '10.0.0.47',
        'sequence': ['nmap', 'ssh', 'exploit', 'sudo'],
        'prompts': {
            'nmap': {
                'output': [
                    '> Starting Nmap scan on 10.0.0.47...',
                    '> PORT     STATE  SERVICE',
                    '> 22/tcp   open   ssh',
                    '> 80/tcp   open   http',
                    '> 3306/tcp open   mysql',
                    '> Scan complete. SSH port open.'
                ],
                'hint': 'SSH is open. Try connecting.'
            },
            'ssh': {
                'output': [
                    '> Attempting SSH connection to 10.0.0.47...',
                    '> Connected as guest@10.0.0.47',
                    '> Limited shell access granted.',
                    '> You need higher privileges.'
                ],
                'hint': 'You are in but need root. Look for an exploit.'
            },
            'exploit': {
                'output': [
                    '> Searching exploit database...',
                    '> CVE-2023-4911 found — glibc privilege escalation',
                    '> Exploit loaded. Ready to execute.',
                    '> Run sudo to escalate privileges.'
                ],
                'hint': 'Exploit loaded. Escalate now.'
            },
            'sudo': {
                'output': [
                    '> Executing privilege escalation...',
                    '> root@10.0.0.47:~# ',
                    '> ROOT ACCESS GRANTED',
                    '> Target compromised.'
                ],
                'hint': ''
            }
        },
        'wrong_responses': [
            'Command not recognised. Try a different approach.',
            'Access denied. That sequence is incorrect.',
            'Invalid command for current context.',
            'Firewall blocked that attempt. Try again.'
        ],
        'domain': 'Operations & Incident Response',
        'reason': 'This sequence mirrors real penetration testing methodology — reconnaissance with nmap, initial access via SSH, exploitation of a known CVE, then privilege escalation to root.'
    },
    {
        'objective': 'Extract credentials from the database at 192.168.1.100',
        'target': '192.168.1.100',
        'sequence': ['nmap', 'sqlmap', 'dump', 'exfil'],
        'prompts': {
            'nmap': {
                'output': [
                    '> Scanning 192.168.1.100...',
                    '> PORT     STATE  SERVICE',
                    '> 3306/tcp open   mysql',
                    '> 80/tcp   open   http',
                    '> Database port exposed. Possible SQL injection vector.'
                ],
                'hint': 'A database is exposed. Try SQL injection tooling.'
            },
            'sqlmap': {
                'output': [
                    '> Running sqlmap against 192.168.1.100:80...',
                    '> Injection point found in login form',
                    '> Database: corp_users',
                    '> Tables: credentials, sessions, audit_log',
                    '> Ready to dump credentials table.'
                ],
                'hint': 'Injection confirmed. Dump the data.'
            },
            'dump': {
                'output': [
                    '> Dumping credentials table...',
                    '> admin:5f4dcc3b5aa765d61d8327deb882cf99',
                    '> user1:e10adc3949ba59abbe56e057f20f883e',
                    '> 47 records extracted. Hashes are MD5.',
                    '> Ready to exfiltrate.'
                ],
                'hint': 'Data dumped. Exfiltrate to complete the mission.'
            },
            'exfil': {
                'output': [
                    '> Opening encrypted tunnel...',
                    '> Transferring 47 credential records...',
                    '> Transfer complete.',
                    '> MISSION COMPLETE — credentials extracted.'
                ],
                'hint': ''
            }
        },
        'wrong_responses': [
            'Command not found in current context.',
            'That operation failed. Wrong approach.',
            'Access denied. Reconsider your method.',
            'Invalid sequence. The target is hardened against that.'
        ],
        'domain': 'Operations & Incident Response',
        'reason': 'This mirrors a real SQL injection attack chain — reconnaissance, injection testing with sqlmap, data extraction, and exfiltration over an encrypted channel.'
    }
]

PACKET_TRACER_SCENARIOS = [
    {
        'objective': 'Route the packet from workstation to the secure database without passing through the untrusted DMZ node',
        'nodes': [
            {'id': 'ws', 'label': 'WORKSTATION', 'x': 0, 'y': 2, 'type': 'source'},
            {'id': 'fw1', 'label': 'FIREWALL', 'x': 1, 'y': 2, 'type': 'safe'},
            {'id': 'dmz', 'label': 'DMZ NODE', 'x': 2, 'y': 1, 'type': 'danger'},
            {'id': 'sw1', 'label': 'CORE SWITCH', 'x': 2, 'y': 2, 'type': 'safe'},
            {'id': 'ids', 'label': 'IDS SENSOR', 'x': 2, 'y': 3, 'type': 'safe'},
            {'id': 'db', 'label': 'DATABASE', 'x': 3, 'y': 2, 'type': 'target'}
        ],
        'connections': [
            ['ws', 'fw1'],
            ['fw1', 'dmz'],
            ['fw1', 'sw1'],
            ['fw1', 'ids'],
            ['dmz', 'db'],
            ['sw1', 'db'],
            ['ids', 'db']
        ],
        'correct_path': ['ws', 'fw1', 'sw1', 'db'],
        'reason': 'Traffic should route through the firewall and core switch — never through the DMZ which is an untrusted zone for public-facing services, not internal database access.'
    },
    {
        'objective': 'Route the packet from the remote user to the internal server via the VPN gateway — avoid the unencrypted proxy',
        'nodes': [
            {'id': 'remote', 'label': 'REMOTE USER', 'x': 0, 'y': 1, 'type': 'source'},
            {'id': 'internet', 'label': 'INTERNET', 'x': 1, 'y': 1, 'type': 'safe'},
            {'id': 'proxy', 'label': 'HTTP PROXY', 'x': 2, 'y': 0, 'type': 'danger'},
            {'id': 'vpn', 'label': 'VPN GATEWAY', 'x': 2, 'y': 2, 'type': 'safe'},
            {'id': 'fw', 'label': 'FIREWALL', 'x': 3, 'y': 1, 'type': 'safe'},
            {'id': 'srv', 'label': 'INTERNAL SERVER', 'x': 4, 'y': 1, 'type': 'target'}
        ],
        'connections': [
            ['remote', 'internet'],
            ['internet', 'proxy'],
            ['internet', 'vpn'],
            ['proxy', 'fw'],
            ['vpn', 'fw'],
            ['fw', 'srv']
        ],
        'correct_path': ['remote', 'internet', 'vpn', 'fw', 'srv'],
        'reason': 'Remote users should always connect via VPN to encrypt traffic end-to-end. Routing through an unencrypted HTTP proxy exposes credentials and session data to interception.'
    }
]

BRUTE_FORCE_SCENARIOS = [
    {
        'objective': 'Three password hashes have been intercepted. Identify which algorithm is weakest and will crack first — then intercept it before the attacker does.',
        'hashes': [
            {
                'algorithm': 'MD5',
                'hash': '5f4dcc3b5aa765d61d8327deb882cf99',
                'speed': 'VERY FAST',
                'crack_time': 3,
                'weak': True,
                'info': 'MD5 is broken. GPUs can compute 10 billion MD5 hashes per second.'
            },
            {
                'algorithm': 'bcrypt',
                'hash': '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.iK8i',
                'speed': 'VERY SLOW',
                'crack_time': 15,
                'weak': False,
                'info': 'bcrypt is designed to be slow. Cost factor 12 means ~250ms per hash.'
            },
            {
                'algorithm': 'SHA-1',
                'hash': 'aaf4c61ddcc5e8a2dabede0f3b482cd9aea9434d',
                'speed': 'FAST',
                'crack_time': 7,
                'weak': False,
                'info': 'SHA-1 is deprecated but still much slower than MD5 for password cracking.'
            }
        ],
        'answer': 0,
        'reason': 'MD5 is critically weak for password storage — it has no salt and can be computed at billions of hashes per second using modern GPUs. bcrypt is the correct choice for password hashing.'
    },
    {
        'objective': 'An attacker has obtained a password database. Three hashing algorithms are in use. Identify which account will be compromised first.',
        'hashes': [
            {
                'algorithm': 'bcrypt',
                'hash': '$2b$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy',
                'speed': 'SLOW',
                'crack_time': 12,
                'weak': False,
                'info': 'bcrypt with cost factor 10. Computationally expensive by design.'
            },
            {
                'algorithm': 'SHA-256',
                'hash': '6b86b273ff34fce19d6b804eff5a3f5747ada4eaa22f1d49c01e52ddb7875b4b',
                'speed': 'MODERATE',
                'crack_time': 8,
                'weak': False,
                'info': 'SHA-256 is a fast hash — not designed for passwords. Better than MD5 but still vulnerable.'
            },
            {
                'algorithm': 'MD5',
                'hash': 'cfcd208495d565ef66e7dff9f98764da',
                'speed': 'VERY FAST',
                'crack_time': 2,
                'weak': True,
                'info': 'MD5 — completely broken for password storage. No salt, trivially fast to crack.'
            }
        ],
        'answer': 2,
        'reason': 'MD5 with no salt is trivially cracked in seconds. This directly maps to Security+ objective 3.2 — understanding why password hashing algorithms must be slow and salted.'
    }
]

MINIGAME_TYPES = ['terminal', 'packet_tracer', 'brute_force']

DOMAIN_MAP_MINIGAMES = {
    'terminal': {
        'domain': 'Operations & Incident Response',
        'objective': '4.1 — Given a scenario, use the appropriate tool to assess organisational security',
        'key_concept': 'Penetration testing follows a methodology: reconnaissance, scanning, exploitation, post-exploitation. Tools like nmap, sqlmap and metasploit are used by both attackers and defenders.',
        'exam_tip': 'Know the phases of a penetration test: planning, reconnaissance, scanning, exploitation, post-exploitation, reporting.'
    },
    'packet_tracer': {
        'domain': 'Network Security',
        'objective': '3.3 — Given a scenario, implement secure network architecture concepts',
        'key_concept': 'Network segmentation controls traffic flow between zones. DMZs are for public-facing services, not internal traffic. VPNs encrypt remote access. Traffic should always flow through security controls.',
        'exam_tip': 'Understand DMZ architecture, network segmentation, VPN placement and why traffic flows matter for security.'
    },
    'brute_force': {
        'domain': 'Implementation',
        'objective': '3.2 — Given a scenario, implement cryptographic protocols',
        'key_concept': 'Password hashing algorithms must be slow and salted. MD5 and SHA-1 are broken for password storage. bcrypt, scrypt and Argon2 are designed specifically for passwords because they are computationally expensive.',
        'exam_tip': 'Know MD5 and SHA-1 are deprecated. Know bcrypt, scrypt and Argon2 are correct for passwords. Know the difference between hashing, encryption and encoding.'
    }
}

def get_random_passwords(hard_mode=False):
    if hard_mode:
        return PASSWORDS_HARD
    pool = [PASSWORDS_EASY] + PASSWORDS_EXTRA
    return random.choice(pool)