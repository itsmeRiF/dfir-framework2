# Security Policy


# Reporting a Vulnerability

The security of CyberX DFIR and the integrity of digital forensic investigations are important to us.

If you discover a security vulnerability, **please do not disclose it publicly** before it has been reviewed and addressed.

Instead, report it privately to the project maintainers.

Please include:

* Description of the vulnerability
* Steps to reproduce
* Affected version(s)
* Operating system and environment details
* Relevant logs or screenshots
* Proof of Concept (if available)
* Suggested mitigation (optional)

Providing complete information helps us investigate and resolve issues more efficiently.

---

# Responsible Disclosure

We encourage responsible disclosure and appreciate the efforts of security researchers.

Please:

* Allow reasonable time for investigation and remediation.
* Do not publicly disclose vulnerabilities before a fix is available.
* Avoid accessing, modifying, or deleting data that does not belong to you.
* Avoid testing against production systems without authorization.
* Report findings in good faith.

---

# Scope

This policy applies to vulnerabilities affecting CyberX DFIR itself, including:

* Authentication and authorization
* Session management
* Case management
* Evidence management
* File upload and validation
* Timeline generation
* Artifact parsing
* Parser execution
* Plugin loading
* Database interactions
* API endpoints
* Dashboard interface
* Configuration management
* Dependency security

---

# Third-Party Tools and Plugin Security

CyberX DFIR may integrate with external forensic tools, parsers, detection rules, or plugins.

Examples include:

* Volatility
* Hayabusa
* YARA
* Sigma Rules
* Plaso
* Chainsaw
* Velociraptor
* Other community-developed extensions

To maintain a secure and trustworthy forensic environment:

* Download tools only from their official sources.
* Verify checksums or digital signatures whenever they are provided.
* Review third-party plugins before installation.
* Keep external tools updated with their latest security patches.
* Do not execute untrusted or unknown binaries within the CyberX DFIR environment.
* Treat community-contributed plugins as untrusted until they have been reviewed.

CyberX DFIR cannot guarantee the security of external tools or third-party extensions.

---

# Forensic Integrity

Maintaining the integrity of digital evidence is a core principle of CyberX DFIR.

Users should:

* Preserve original evidence whenever possible.
* Work from forensic copies instead of original media.
* Verify cryptographic hashes before and after analysis.
* Maintain proper chain-of-custody documentation.
* Avoid modifying original evidence.
* Record all analysis activities as part of the investigation process.

Failure to follow proper forensic procedures may affect the admissibility and reliability of evidence.

---

# Secure Deployment Recommendations

For production deployments, we recommend:

* Enable HTTPS.
* Use strong authentication.
* Restrict administrative access.
* Store uploaded evidence on secure storage.
* Protect application secrets using environment variables or a secure secrets manager.
* Keep Python and project dependencies updated.
* Apply operating system security updates regularly.
* Perform routine backups of databases and evidence storage.
* Monitor application logs for suspicious activity.
* Use least-privilege permissions for service accounts.

---

# Supply Chain Security

To reduce software supply chain risks:

* Install dependencies only from trusted repositories.
* Review dependency updates before deployment.
* Verify downloaded binaries where possible.
* Avoid installing unnecessary packages.
* Periodically audit project dependencies for known vulnerabilities.

---

# Out of Scope

The following are generally outside the scope of this policy:

* Vulnerabilities in unsupported releases.
* Issues caused by insecure local deployments.
* Operating system vulnerabilities.
* Third-party software defects outside CyberX DFIR.
* Social engineering attacks.
* Denial-of-service testing against production environments.
* Physical access attacks.

---

# Response Process

When a valid vulnerability report is received, project maintainers will aim to:

1. Acknowledge the report.
2. Validate the issue.
3. Assess impact and severity.
4. Develop and test a fix.
5. Release a security update when appropriate.
6. Credit the reporter, where appropriate and with their permission.

Response times may vary depending on the complexity of the issue.

---

# Security Advisories

When appropriate, security fixes may be accompanied by a public advisory describing:

* Affected versions
* Severity
* Impact
* Resolution
* Recommended upgrade path

Sensitive exploit details may be withheld until users have had a reasonable opportunity to apply security updates.

---

# Legal and Ethical Use

CyberX DFIR is intended exclusively for lawful digital forensic investigations, incident response, malware analysis, and cybersecurity research.

Users are responsible for ensuring that the software is used in compliance with applicable laws, organizational policies, and evidence-handling procedures. The project maintainers are not responsible for misuse of the software or third-party tools used alongside it.

---

# Acknowledgements

We sincerely thank security researchers, contributors, and members of the DFIR community who responsibly report vulnerabilities and help improve the security, reliability, and integrity of CyberX DFIR.

--Team CyberX
