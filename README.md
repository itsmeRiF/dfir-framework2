# CyberX | DFIR Framework

End-to-end DFIR pipeline with Flask — case management, evidence upload, artifact parsing, timeline, and incident correlation.

## Artifact Analysis Modules

| Type | Extensions | Parser | Output |
|------|-----------|--------|--------|
| **EVTX** | `.evtx` | Hayabusa | Sigma-detected events |
| **Prefetch** | `.pf` | Execution history | LOLbin detection |
| **JumpList** | `.automaticDestinations-ms`, `.customDestinations-ms` | OLE + LNK parser | Recent app targets, suspicious paths |
| **Registry** | `SYSTEM`, `SOFTWARE`, `SAM`, `NTUSER.DAT`, etc. | Suspicious hive paths | Persistence mechanisms of malware
| **Memory** | `.raw`, `.mem`, `.dmp`, `.vmem` | Strings IOC + optional Volatility3 | Process/network/malfind + string IOCs |

All parsed records normalize into the shared **Event** model so they appear in Events, Timeline, and Incidents views.

## Setup

```bash
cd dfir-framework2
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python bootstrap.py
python app.py

---Then, do this if you are using this tool for the first time----
cd tools/
hayabusa.exe update-rules
```

Open http://127.0.0.1:1338 — login with `analyst` / `analyst123`.

Place `hayabusa.exe` in the `tools/` folder for EVTX analysis

```


## Road Map | Artifact Support Status

* [x] Event Logs
* [x] Registry Hives
* [x] Prefetch Files
* [x] Jump Lists
* [x] Memory Dumps
* [ ] Browser History

## Notes
Made with ❤️ in India
