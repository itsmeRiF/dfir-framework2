# Contributing to CyberX DFIR

First off, thank you for considering contributing to **CyberX DFIR**.

CyberX DFIR is an open-source Digital Forensics and Incident Response framework designed to simplify forensic investigations, evidence management, timeline analysis, memory forensics, and incident response workflows.

Every contribution—whether it is fixing a bug, improving documentation, adding new parsers, or suggesting new features—is greatly appreciated.

---

# Table of Contents

* Code of Conduct
* Ways to Contribute
* Getting Started
* Development Setup
* Branching Strategy
* Coding Standards
* Commit Message Guidelines
* Pull Request Process
* Reporting Bugs
* Suggesting Features
* Security Issues
* Documentation Contributions
* License

---

# Code of Conduct

Please be respectful to all contributors.

We expect everyone participating in this project to:

* Be respectful
* Be constructive
* Welcome new contributors
* Keep discussions professional
* Avoid offensive language or personal attacks

---

# Ways to Contribute

You can contribute in many ways:

* Fix bugs
* Improve documentation
* Add new forensic artifact parsers
* Improve existing modules
* Build new DFIR workflows
* Add Sigma or detection rules
* Improve UI/UX
* Optimize database queries
* Improve testing
* Suggest new features
* Review Pull Requests

---

# Getting Started

## 1. Fork the Repository

Create your own fork of the repository.

## 2. Clone your Fork

```bash
git clone https://github.com/itsmeRiF/dfir-framework2.git
```

Move into the project directory.

```bash
cd dfir-framework2
```

---

## 3. Create a Virtual Environment

Windows

```bash
python -m venv venv

venv\Scripts\activate
```

Linux / macOS

```bash
python3 -m venv venv

source venv/bin/activate
```

---

## 4. Install Dependencies

```bash
pip install -r requirements.txt
```

---

Follow the instructions through https://github.com/itsmeRiF/dfir-framework2#create-user
---

# Branching Strategy

Never commit directly to the main branch.

Create a feature branch:

```bash
git checkout -b feature/my-new-feature
```

Examples:

```
feature/evtx-parser

feature/memory-dashboard

bugfix/hash-calculation

docs/update-readme

refactor/parser-router
```

---

# Coding Standards

Please follow these guidelines:

## Python

* Follow PEP 8
* Maximum line length: 100–120 characters
* Use meaningful variable names
* Use type hints where appropriate
* Keep functions small and focused
* Add docstrings for public functions

Example:

```python
def calculate_hash(file_path: str) -> str:
    """Calculate SHA256 hash of a file."""
```

---

## HTML

* Use semantic HTML
* Keep indentation consistent
* Avoid inline CSS whenever possible
* Prefer reusable components

---

## JavaScript

* Use meaningful function names
* Avoid global variables
* Comment complex logic
* Prefer modern ES6 syntax

---

## CSS

* Reuse existing styles
* Keep naming consistent
* Avoid duplicate CSS

---

# Project Structure

Please place code in the correct location.

Example:

```
models/
routes/
modules/
templates/
static/
database/
migrations/
instance/
tests/
```

Avoid creating unnecessary top-level folders.

---

# Commit Message Guidelines

Use clear commit messages.

Good examples:

```
Add EVTX parser

Fix timeline sorting

Improve dashboard performance

Refactor evidence service

Update documentation
```

Avoid messages like:

```
fix

update

changes

done

test
```

---

# Pull Request Process

Before opening a Pull Request:

* Sync with the latest main branch.
* Ensure the application starts without errors.
* Verify that existing functionality still works.
* Update documentation if needed.
* Add tests where applicable.

A Pull Request should include:

* Description of changes
* Screenshots (if UI changes)
* Steps to test
* Related Issue number (if any)

Example:

```
## Summary

Added Windows Prefetch parser.

## Changes

- Added parser
- Added database model
- Added UI page

## Testing

Successfully tested using Windows 11 sample images.

## Related Issue

Fixes #42
```

---

# Reporting Bugs

When reporting bugs, please include:

* Operating System
* Python version
* Browser (if applicable)
* Error message
* Stack trace
* Screenshots
* Steps to reproduce
* Expected behavior
* Actual behavior

---

# Suggesting Features

When suggesting a feature, include:

* Problem statement
* Proposed solution
* Expected benefits
* Possible implementation details
* Screenshots or mockups (optional)

---

# Security Issues

Please **do not** report security vulnerabilities through public GitHub Issues.

Instead, privately contact the project maintainers with:

* Vulnerability description
* Steps to reproduce
* Impact assessment
* Proof of Concept (if available)

Responsible disclosure is appreciated.

---

# Documentation Contributions

Documentation improvements are always welcome.

Examples:

* README updates
* Installation guides
* API documentation
* Screenshots
* Tutorials
* Architecture diagrams
* Example workflows

---

# Testing

Before submitting code, verify:

* Application starts successfully.
* No new warnings or errors.
* Database migrations work.
* Upload functionality works.
* Evidence parsing works.
* Timeline generation works.
* Dashboard loads correctly.

---

# Review Process

Every Pull Request will be reviewed for:

* Code quality
* Security
* Performance
* Readability
* Documentation
* Backward compatibility

Changes may be requested before merging.

---

# License

By contributing to CyberX DFIR, you agree that your contributions will be licensed under the same license as this project.

---

# Thank You

Thank you for helping improve **CyberX DFIR**.

Your contributions help make digital forensic investigations more efficient, accessible, and reliable for the security community.

Let's try to build code and share for free as in free bread!
Happy Coding!

Regards,
itsmeRiF
