# DFIR Framework

End-to-end DFIR pipeline with Flask — case management, evidence upload, artifact parsing, timeline, and incident correlation.

## Artifact Analysis Modules

| Type | Extensions | Parser | Output |
|------|-----------|--------|--------|
| **EVTX** | `.evtx` | Hayabusa | Sigma-detected events |
| **Prefetch** | `.pf` | Native SCCA/MAM parser | Execution history, LOLbin detection |
| **JumpList** | `.automaticDestinations-ms`, `.customDestinations-ms` | OLE + LNK parser | Recent app targets, suspicious paths |
| **Registry** | `SYSTEM`, `SOFTWARE`, `SAM`, `NTUSER.DAT`, etc. | python-registry | Run keys, services, persistence |
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

## Upload Flow

1. Create a case
2. Go to **Add Evidence**
3. Select artifact type (or rely on auto-detection from extension)
4. Upload file — parser runs automatically
5. Review **Events**, **Timeline**, and **Incidents**

## Project Structure

```
modules/
  parser/
    artifact_router.py   # Routes file → correct parser
    prefetch.py          # Prefetch analysis
    jumplist.py          # JumpList analysis
    registry_parser.py   # Registry hive analysis
    memory.py            # RAM dump analysis
  analysis/
    artifact_ioc.py      # Suspicious pattern detection
  engine/
    incident_engine.py   # Extended with artifact incidents
```

## Notes
Made with <3 in India
