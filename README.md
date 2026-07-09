# 🛡️ CyberX | DFIR Framework

**End-to-End Digital Forensics & Incident Response Framework**

Case Management • Evidence Processing • Artifact Parsing • Timeline Analysis • Incident Correlation

---

## 📌 Overview

CyberX DFIR Framework is a modular **Digital Forensics and Incident Response (DFIR)** platform built using Flask.

The framework provides a unified investigation workspace for:

📁 Case Management\
📤 Evidence Upload & Processing\
🔍 Artifact Analysis\
🕒 Timeline Reconstruction\
🚨 Incident Detection & Correlation\
📊 Investigation Data Export

All forensic artifacts are normalized into a common **Event Model**, allowing investigators to analyze artifacts across:

* Events Explorer
* Timeline View
* Incident Dashboard

---

# 🔎 Artifact Analysis Modules

| Artifact             | Extensions                                            | Parser / Engine              | Output                                          |
| -------------------- | ----------------------------------------------------- | ---------------------------- | ----------------------------------------------- |
| ✅ Windows Event Logs | `.evtx`                                               | Hayabusa + Sigma Rules       | Threat detections, suspicious activities        |
| ✅ Registry Hives     | SYSTEM, SOFTWARE, SAM, NTUSER.DAT                     | Registry Parser              | Persistence mechanisms, configuration artifacts |
| ✅ Prefetch Files     | `.pf`                                                 | Prefetch Parser              | Execution history, LOLBin detection             |
| ✅ Jump Lists         | `.automaticDestinations-ms`, `.customDestinations-ms` | OLE + LNK Parser             | Recent applications, accessed files             |
| ✅ Memory Dumps      | `.raw`, `.mem`, `.dmp`, `.vmem`                       | Volatility3 + IOC Extraction | Processes, network artifacts, memory analysis   |

---

# 🏗️ DFIR Processing Pipeline

```
                Evidence Upload
                       |
                       ↓
              Artifact Identification
                       |
        +--------------+--------------+
        |              |              |
      EVTX        Registry       Memory
        |              |              |
    Hayabusa      Hive Parser   Volatility3
        |              |              |
        +--------------+--------------+
                       |
                       ↓
              Normalized Event Model
                       |
          +------------+------------+
          |                         |
       Timeline              Incident Engine
          |                         |
          ↓                         ↓
 Investigation View          Threat Detection
```

---

# ⚙️ Installation

## Clone Repository

```bash
git clone https://github.com/itsmeRiF/dfir-framework2.git

cd dfir-framework2
```

---

## Create Virtual Environment

```bash
python -m venv .venv

.venv\Scripts\activate
```

---

## Install Requirements

```bash
pip install -r requirements.txt
```

---

## Create user

```bash
python bootstrap.py
```

---

## Start Application

```bash
python app.py
```

Access:

```
http://127.0.0.1:1338
```

Default Credentials:

```
Username: analyst
Password: analyst123
```

---

# For Event Logs Analysis

Download Hayabusa and place:

```
hayabusa.exe
```

inside:

```
tools/
```

Before first use:

```bash
cd tools

hayabusa.exe update-rules
```

This downloads:

* Sigma Detection Rules
* Detection Metadata
* Hayabusa Rule Configuration

---

# 🗺️ Development Roadmap

## Phase 1 — Core Windows Artifacts ✅

* [x] Windows Event Logs (EVTX)
* [x] Registry Hives
* [x] Prefetch Files
* [x] Jump Lists
* [x] Memory Dumps


## To-do:
* [ ] Display summary of RAM Analysis
* [ ] Running processes
* [ ] Active network connections

## Phase 2 — Advanced Artifact Support 🚧

* [ ] Browser History


## Phase 3 — File System Forensics 🔮

* [ ] Master File Table (MFT)
* [ ] USN Journal
* [ ] SRUM Database
* [ ] Recycle Bin Analysis

---

# 🚀 Current Features

✅ Case Management\
✅ Evidence Repository\
✅ Artifact Auto Detection\
✅ Hayabusa Integration\
✅ Sigma Rule Detection\
✅ Event Normalization\
✅ Timeline Analysis\
✅ Incident Correlation\
✅ Severity Classification\
✅ CSV Export

---

# 🔮 Future Integrations

* Volatility3 Memory Framework
* YARA Malware Detection
* MITRE ATT&CK Mapping
* Threat Intelligence Integration
* IOC Extraction Engine
* Automated Investigation Reports

---


# 👥 Contributors

Thanks to all contributors who helped build and test this CyberX DFIR Framework.

<a href="https://github.com/itsmeRiF/dfir-framework2/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=itsmeRiF/dfir-framework2" />
</a>

<p align="center">

Made with ❤️ in India 🇮🇳

<b>CyberX DFIR Framework</b>

</p>
