# Security+ question bank
# mapped to CompTIA Security+ SY0-701 exam objectives

QUESTIONS = [
    # domain 1 — threats attacks and vulnerabilities
    {
        'id': 1,
        'domain': 'Threats, Attacks & Vulnerabilities',
        'objective': '1.1',
        'question': 'An attacker uses a list of commonly used passwords to attempt to log in to multiple accounts. What type of attack is this?',
        'options': ['Brute force', 'Password spraying', 'Dictionary attack', 'Credential stuffing'],
        'answer': 2,
        'explanation': 'A dictionary attack uses a predefined list of common passwords. Brute force tries all combinations. Password spraying tries one common password across many accounts. Credential stuffing uses previously breached username/password pairs.'
    },
    {
        'id': 2,
        'domain': 'Threats, Attacks & Vulnerabilities',
        'objective': '1.1',
        'question': 'A user receives an email appearing to be from their bank asking them to verify their account details by clicking a link. What type of attack is this?',
        'options': ['Vishing', 'Smishing', 'Phishing', 'Whaling'],
        'answer': 2,
        'explanation': 'Phishing is a social engineering attack delivered via email. Vishing is via phone, smishing via SMS. Whaling specifically targets high-profile executives.'
    },
    {
        'id': 3,
        'domain': 'Threats, Attacks & Vulnerabilities',
        'objective': '1.2',
        'question': 'Which of the following best describes a zero-day vulnerability?',
        'options': [
            'A vulnerability that has been patched within 24 hours',
            'A vulnerability that is unknown to the vendor and has no available patch',
            'A vulnerability that affects zero users',
            'A vulnerability discovered on the first day of a penetration test'
        ],
        'answer': 1,
        'explanation': 'A zero-day vulnerability is one that is unknown to the software vendor and therefore has no patch available. Attackers who discover these can exploit them before any defence is possible.'
    },
    {
        'id': 4,
        'domain': 'Threats, Attacks & Vulnerabilities',
        'objective': '1.3',
        'question': 'An attacker intercepts communication between two parties and relays messages between them without either party knowing. What is this called?',
        'options': ['Replay attack', 'Man-in-the-middle attack', 'Session hijacking', 'Eavesdropping'],
        'answer': 1,
        'explanation': 'A man-in-the-middle (MITM) attack involves an attacker secretly intercepting and potentially altering communications between two parties. HTTPS and certificate validation help prevent this.'
    },
    {
        'id': 5,
        'domain': 'Threats, Attacks & Vulnerabilities',
        'objective': '1.3',
        'question': 'Which type of malware encrypts a victim\'s files and demands payment for the decryption key?',
        'options': ['Spyware', 'Ransomware', 'Trojan', 'Rootkit'],
        'answer': 1,
        'explanation': 'Ransomware encrypts files and demands a ransom for the key. Spyware silently collects data. Trojans disguise themselves as legitimate software. Rootkits hide their presence on a system.'
    },

    # domain 2 — architecture and design
    {
        'id': 6,
        'domain': 'Architecture & Design',
        'objective': '2.1',
        'question': 'What security principle ensures that users only have access to the resources they need to perform their job?',
        'options': ['Separation of duties', 'Least privilege', 'Need to know', 'Zero trust'],
        'answer': 1,
        'explanation': 'Least privilege limits user access rights to only what is required for their role. This minimises the damage that can be done if an account is compromised.'
    },
    {
        'id': 7,
        'domain': 'Architecture & Design',
        'objective': '2.1',
        'question': 'Which of the following best describes defence in depth?',
        'options': [
            'Using a single strong firewall to protect a network',
            'Layering multiple security controls so that if one fails others remain',
            'Defending only the most critical systems',
            'Using deep packet inspection on all traffic'
        ],
        'answer': 1,
        'explanation': 'Defence in depth means using multiple layers of security controls. If one layer is bypassed, the next layer provides protection. No single control is relied upon entirely.'
    },
    {
        'id': 8,
        'domain': 'Architecture & Design',
        'objective': '2.2',
        'question': 'A company wants to ensure that no single employee can complete a sensitive financial transaction alone. Which principle does this implement?',
        'options': ['Least privilege', 'Separation of duties', 'Job rotation', 'Mandatory vacation'],
        'answer': 1,
        'explanation': 'Separation of duties requires that critical tasks be split between multiple people to prevent fraud or error. It ensures no single person has end-to-end control over a sensitive process.'
    },
    {
        'id': 9,
        'domain': 'Architecture & Design',
        'objective': '2.4',
        'question': 'Which of the following is an example of multi-factor authentication?',
        'options': [
            'A long complex password',
            'A password and a PIN',
            'A fingerprint scan and a one-time code sent to a phone',
            'Two different passwords'
        ],
        'answer': 2,
        'explanation': 'MFA requires two or more different factor types: something you know (password/PIN), something you have (phone/token), something you are (biometric). A fingerprint and OTP combine two different factor types.'
    },
    {
        'id': 10,
        'domain': 'Architecture & Design',
        'objective': '2.5',
        'question': 'What is the purpose of a DMZ in network architecture?',
        'options': [
            'To store encrypted backups',
            'To provide a buffer zone between the internet and internal network for public-facing services',
            'To isolate infected devices',
            'To monitor internal network traffic'
        ],
        'answer': 1,
        'explanation': 'A DMZ (demilitarised zone) is a network segment that sits between the internet and the internal network. Public-facing servers like web servers are placed here so they can be accessed externally without exposing the internal network.'
    },

    # domain 3 — implementation
    {
        'id': 11,
        'domain': 'Implementation',
        'objective': '3.1',
        'question': 'Which protocol provides encrypted communications for web traffic?',
        'options': ['HTTP', 'FTP', 'HTTPS', 'Telnet'],
        'answer': 2,
        'explanation': 'HTTPS (HTTP Secure) uses TLS to encrypt web traffic between a browser and server. HTTP, FTP and Telnet all transmit data in plain text and should be avoided for sensitive communications.'
    },
    {
        'id': 12,
        'domain': 'Implementation',
        'objective': '3.2',
        'question': 'An organisation wants to ensure that even if an attacker obtains their password database, the passwords cannot be easily recovered. Which technique should they use?',
        'options': ['Encryption', 'Hashing with salt', 'Encoding', 'Tokenisation'],
        'answer': 1,
        'explanation': 'Passwords should be hashed with a unique salt per user. Hashing is one-way so the original password cannot be recovered. Salting prevents rainbow table attacks. Encryption is reversible and therefore less suitable for passwords.'
    },
    {
        'id': 13,
        'domain': 'Implementation',
        'objective': '3.3',
        'question': 'Which of the following wireless security protocols is considered the most secure?',
        'options': ['WEP', 'WPA', 'WPA2', 'WPA3'],
        'answer': 3,
        'explanation': 'WPA3 is the latest and most secure wireless security protocol. WEP is broken and should never be used. WPA and WPA2 have known vulnerabilities. WPA3 introduces stronger encryption and protections against offline dictionary attacks.'
    },
    {
        'id': 14,
        'domain': 'Implementation',
        'objective': '3.4',
        'question': 'What does PKI stand for and what is its primary purpose?',
        'options': [
            'Public Key Infrastructure — manages digital certificates and encryption keys',
            'Private Key Integration — integrates private keys across systems',
            'Public Key Interface — provides an interface for key exchange',
            'Packet Key Inspection — inspects encrypted packets'
        ],
        'answer': 0,
        'explanation': 'PKI (Public Key Infrastructure) is a framework for managing digital certificates and public-key encryption. It enables secure communications by verifying identities through trusted certificate authorities.'
    },
    {
        'id': 15,
        'domain': 'Implementation',
        'objective': '3.5',
        'question': 'Which type of firewall can inspect the contents of packets including application layer data?',
        'options': ['Packet filter', 'Stateful inspection firewall', 'Next-generation firewall', 'Circuit-level gateway'],
        'answer': 2,
        'explanation': 'A next-generation firewall (NGFW) can perform deep packet inspection including application layer analysis. Traditional packet filters only look at headers. Stateful firewalls track connection state but not application content.'
    },

    # domain 4 — operations and incident response
    {
        'id': 16,
        'domain': 'Operations & Incident Response',
        'objective': '4.1',
        'question': 'What is the correct order of the incident response lifecycle?',
        'options': [
            'Identification, Preparation, Containment, Eradication, Recovery, Lessons Learned',
            'Preparation, Identification, Containment, Eradication, Recovery, Lessons Learned',
            'Preparation, Containment, Identification, Eradication, Recovery, Lessons Learned',
            'Identification, Containment, Preparation, Recovery, Eradication, Lessons Learned'
        ],
        'answer': 1,
        'explanation': 'The correct order is: Preparation, Identification, Containment, Eradication, Recovery, Lessons Learned. You must prepare before an incident occurs, then identify it, contain the damage, eradicate the cause, recover systems, and document lessons learned.'
    },
    {
        'id': 17,
        'domain': 'Operations & Incident Response',
        'objective': '4.2',
        'question': 'A security analyst discovers malware on a workstation. What should be the first step?',
        'options': ['Delete the malware immediately', 'Reimage the workstation', 'Isolate the workstation from the network', 'Notify the user'],
        'answer': 2,
        'explanation': 'Containment is the immediate priority. Isolating the infected device prevents the malware from spreading to other systems or communicating with a command and control server. Evidence should be preserved before remediation.'
    },
    {
        'id': 18,
        'domain': 'Operations & Incident Response',
        'objective': '4.3',
        'question': 'What is a chain of custody in digital forensics?',
        'options': [
            'A list of all suspects in a security incident',
            'The documented process of collecting, handling and preserving evidence to maintain its integrity',
            'A record of all network connections during an incident',
            'The hierarchy of who can access forensic evidence'
        ],
        'answer': 1,
        'explanation': 'Chain of custody documents who collected evidence, how it was handled, and where it has been stored. This is critical for legal proceedings as it proves evidence has not been tampered with.'
    },
    {
        'id': 19,
        'domain': 'Operations & Incident Response',
        'objective': '4.4',
        'question': 'Which of the following is an example of a technical control?',
        'options': ['Security awareness training', 'A firewall', 'A security policy', 'A background check'],
        'answer': 1,
        'explanation': 'Technical controls are technology-based safeguards like firewalls, encryption and access controls. Administrative controls include policies and training. Physical controls include locks and security guards.'
    },
    {
        'id': 20,
        'domain': 'Operations & Incident Response',
        'objective': '4.5',
        'question': 'What is the purpose of a SIEM system?',
        'options': [
            'To encrypt sensitive data at rest',
            'To collect and correlate security event logs from multiple sources for analysis',
            'To scan systems for vulnerabilities',
            'To manage user identities and access'
        ],
        'answer': 1,
        'explanation': 'A SIEM (Security Information and Event Management) system aggregates and correlates log data from across an environment to detect threats, generate alerts and support incident investigation.'
    },

    # domain 5 — governance risk and compliance
    {
        'id': 21,
        'domain': 'Governance, Risk & Compliance',
        'objective': '5.1',
        'question': 'What is the difference between a vulnerability and a threat?',
        'options': [
            'They are the same thing',
            'A vulnerability is a weakness, a threat is something that could exploit that weakness',
            'A threat is a weakness, a vulnerability is something that exploits it',
            'A vulnerability is always internal, a threat is always external'
        ],
        'answer': 1,
        'explanation': 'A vulnerability is a weakness in a system. A threat is an actor or event that could exploit that vulnerability. Risk is the likelihood and impact of a threat exploiting a vulnerability.'
    },
    {
        'id': 22,
        'domain': 'Governance, Risk & Compliance',
        'objective': '5.2',
        'question': 'Which regulation specifically governs the protection of personal data for individuals in the European Union?',
        'options': ['HIPAA', 'PCI DSS', 'GDPR', 'SOX'],
        'answer': 2,
        'explanation': 'GDPR (General Data Protection Regulation) governs personal data protection for EU residents. HIPAA covers US healthcare data. PCI DSS covers payment card data. SOX covers financial reporting.'
    },
    {
        'id': 23,
        'domain': 'Governance, Risk & Compliance',
        'objective': '5.3',
        'question': 'What is the purpose of a BCP (Business Continuity Plan)?',
        'options': [
            'To document all security vulnerabilities',
            'To ensure critical business functions can continue during and after a disruption',
            'To outline the steps for responding to a security breach',
            'To define acceptable use of company IT resources'
        ],
        'answer': 1,
        'explanation': 'A BCP ensures an organisation can continue critical operations during disruptions like natural disasters, cyberattacks or system failures. It is broader than a disaster recovery plan which focuses specifically on IT systems.'
    },
    {
        'id': 24,
        'domain': 'Governance, Risk & Compliance',
        'objective': '5.4',
        'question': 'A company accepts the risks associated with running an older unpatched system because the cost of upgrading is too high. What risk strategy is this?',
        'options': ['Risk avoidance', 'Risk transference', 'Risk mitigation', 'Risk acceptance'],
        'answer': 3,
        'explanation': 'Risk acceptance means acknowledging a risk exists and choosing to proceed without additional controls, usually because the cost of mitigation outweighs the potential impact. Risk transference shifts the risk to a third party like an insurer.'
    },
    {
        'id': 25,
        'domain': 'Governance, Risk & Compliance',
        'objective': '5.5',
        'question': 'What does the term "due diligence" mean in a security context?',
        'options': [
            'Responding quickly to security incidents',
            'Researching and understanding risks before making security decisions',
            'Ensuring all staff complete security training',
            'Conducting regular penetration tests'
        ],
        'answer': 1,
        'explanation': 'Due diligence means doing the research and investigation needed to understand risks before making decisions. Due care means taking the appropriate actions once risks are understood. Both are important for governance.'
    },

    # bonus harder questions
    {
        'id': 26,
        'domain': 'Threats, Attacks & Vulnerabilities',
        'objective': '1.4',
        'question': 'An attacker sends millions of requests to a web server causing it to become unavailable to legitimate users. What type of attack is this?',
        'options': ['SQL injection', 'Cross-site scripting', 'Distributed denial of service', 'Buffer overflow'],
        'answer': 2,
        'explanation': 'A DDoS (Distributed Denial of Service) attack overwhelms a target with traffic from multiple sources making it unavailable. SQL injection and XSS are application layer attacks. Buffer overflow exploits memory handling vulnerabilities.'
    },
    {
        'id': 27,
        'domain': 'Implementation',
        'objective': '3.6',
        'question': 'Which of the following best describes the purpose of network segmentation?',
        'options': [
            'To increase network speed',
            'To divide a network into smaller zones to limit the spread of a breach',
            'To reduce the number of IP addresses needed',
            'To simplify network management'
        ],
        'answer': 1,
        'explanation': 'Network segmentation divides a network into isolated zones. If one segment is compromised, the attacker cannot easily move laterally to other segments. VLANs and firewalls are commonly used to implement segmentation.'
    },
    {
        'id': 28,
        'domain': 'Operations & Incident Response',
        'objective': '4.1',
        'question': 'What is the primary purpose of penetration testing?',
        'options': [
            'To monitor network traffic for threats',
            'To simulate real attacks to identify vulnerabilities before attackers do',
            'To test backup and recovery procedures',
            'To audit user access rights'
        ],
        'answer': 1,
        'explanation': 'Penetration testing involves authorised simulated attacks on systems to find vulnerabilities before real attackers do. It differs from vulnerability scanning which is automated and less thorough.'
    },
    {
        'id': 29,
        'domain': 'Architecture & Design',
        'objective': '2.3',
        'question': 'What is the main characteristic of a zero trust security model?',
        'options': [
            'No security controls are trusted',
            'All users inside the network are trusted by default',
            'No user or device is trusted by default regardless of location',
            'Only zero-day threats are considered'
        ],
        'answer': 2,
        'explanation': 'Zero trust assumes no user, device or network segment is inherently trustworthy. Every access request must be verified regardless of whether it comes from inside or outside the network perimeter.'
    },
    {
        'id': 30,
        'domain': 'Governance, Risk & Compliance',
        'objective': '5.1',
        'question': 'Which of the following correctly defines the CIA triad?',
        'options': [
            'Confidentiality, Integrity, Availability',
            'Control, Identity, Authentication',
            'Confidentiality, Investigation, Access',
            'Compliance, Integrity, Authorisation'
        ],
        'answer': 0,
        'explanation': 'The CIA triad is the foundation of information security: Confidentiality (only authorised users can access data), Integrity (data is accurate and unaltered), Availability (systems and data are accessible when needed).'
    }
]

# group questions by domain for domain-based study
DOMAINS = {
    'Threats, Attacks & Vulnerabilities': [q for q in QUESTIONS if q['domain'] == 'Threats, Attacks & Vulnerabilities'],
    'Architecture & Design': [q for q in QUESTIONS if q['domain'] == 'Architecture & Design'],
    'Implementation': [q for q in QUESTIONS if q['domain'] == 'Implementation'],
    'Operations & Incident Response': [q for q in QUESTIONS if q['domain'] == 'Operations & Incident Response'],
    'Governance, Risk & Compliance': [q for q in QUESTIONS if q['domain'] == 'Governance, Risk & Compliance']
}