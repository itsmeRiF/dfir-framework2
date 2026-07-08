"""IOC and suspicious-pattern checks for Windows artifact analysis."""

SUSPICIOUS_EXECUTABLES = {
    "powershell.exe", "cmd.exe", "wscript.exe", "cscript.exe", "mshta.exe",
    "rundll32.exe", "regsvr32.exe", "certutil.exe", "bitsadmin.exe",
    "msbuild.exe", "installutil.exe", "regasm.exe", "schtasks.exe",
    "psexec.exe", "procdump.exe", "mimikatz.exe", "nc.exe", "ncat.exe",
}

SUSPICIOUS_PATH_FRAGMENTS = (
    "\\temp\\", "\\tmp\\", "\\appdata\\local\\temp\\",
    "\\programdata\\", "\\users\\public\\", "\\windows\\temp\\",
)

SUSPICIOUS_REGISTRY_VALUES = (
    "powershell", "cmd.exe", "wscript", "mshta", "rundll32",
    "regsvr32", "certutil", "bitsadmin", "javascript:", "vbscript:",
    "http://", "https://", "\\temp\\", "appdata\\local\\temp",
)

MEMORY_IOC_PATTERNS = (
    ("mimikatz", "critical", "Mimikatz_String"),
    ("sekurlsa::", "critical", "Credential_Dump_Command"),
    ("lsadump::", "critical", "LSA_Dump_Command"),
    ("Invoke-Mimikatz", "critical", "PowerShell_Mimikatz"),
    ("-enc ", "high", "Encoded_PowerShell"),
    ("FromBase64String", "high", "Base64_Decode_Activity"),
    ("IEX(", "high", "PowerShell_IEX"),
    ("DownloadString", "high", "PowerShell_Download"),
    ("\\temp\\", "medium", "Temp_Path_Reference"),
)


def prefetch_severity(executable_name: str) -> str:
    name = (executable_name or "").lower()
    if name in SUSPICIOUS_EXECUTABLES:
        return "high"
    if any(p in name for p in SUSPICIOUS_PATH_FRAGMENTS):
        return "medium"
    return "informational"


def jumplist_severity(target_path: str) -> str:
    path = (target_path or "").lower()
    if any(p in path for p in SUSPICIOUS_PATH_FRAGMENTS):
        return "high"
    for exe in SUSPICIOUS_EXECUTABLES:
        if exe in path:
            return "high"
    return "informational"


def registry_severity(key_path: str, value_data: str) -> str:
    combined = f"{key_path} {value_data}".lower()
    if any(ioc in combined for ioc in SUSPICIOUS_REGISTRY_VALUES):
        return "high"
    if "run" in key_path.lower() or "service" in key_path.lower():
        return "medium"
    return "informational"


def memory_pattern_severity(pattern: str) -> tuple[str, str]:
    for needle, severity, rule_id in MEMORY_IOC_PATTERNS:
        if needle.lower() in pattern.lower():
            return severity, rule_id
    return "informational", "Memory_String_Match"
