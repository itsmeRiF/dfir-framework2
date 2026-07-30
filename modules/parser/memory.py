"""RAM dump / memory image analysis."""

import os
import re
import sys
import subprocess
from datetime import datetime

from flask import current_app

from modules.analysis.artifact_ioc import MEMORY_IOC_PATTERNS
from modules.parser.event_helpers import make_event


MAX_STRING_SCAN_BYTES = 64 * 1024 * 1024


PROCESS_HINTS = (
    b"powershell.exe",
    b"cmd.exe",
    b"rundll32.exe",
    b"mshta.exe",
    b"wscript.exe",
    b"mimikatz",
    b"lsass.exe",
    b"svchost.exe",
)



def _extract_strings(data: bytes, min_len: int = 6):

    ascii_strings = re.findall(
        rb"[\x20-\x7e]{%d,}" % min_len,
        data
    )

    wide_strings = re.findall(
        rb"(?:[\x20-\x7e]\x00){%d,}" % min_len,
        data
    )


    results = set()


    for s in ascii_strings:
        results.add(
            s.decode(
                "ascii",
                errors="ignore"
            )
        )


    for s in wide_strings:
        results.add(
            s.decode(
                "utf-16-le",
                errors="ignore"
            )
        )


    return results




def _detect_dump_type(filepath):

    with open(filepath,"rb") as f:

        header=f.read(16)


    if header[:4] == b"PAGE":
        return "Windows Crash Dump"


    if header[:4] == b"\x4d\x5a":
        return "Hibernation / Hybrid Dump"


    if header[:8] == b"MDMPMDMP":
        return "Minidump"


    return "Raw Memory Dump"


    

def _get_volatility_command():
    """
    Return Volatility3 execution command
    """

    vol_path = current_app.config.get(
        "VOLATILITY_PATH"
    )

    if not vol_path:
        return None


    if vol_path.endswith(".py"):

        return [
            sys.executable,
            vol_path
        ]


    return [
        vol_path
    ]


    
def _run_volatility(filepath: str, output_dir: str) -> list[dict]:

    events = []

    vol_path = current_app.config.get(
        "VOLATILITY_PATH"
    )

    if not vol_path:
        print("VOLATILITY PATH NOT CONFIGURED")
        return events


    if not os.path.exists(vol_path):
        print("VOLATILITY FILE NOT FOUND:", vol_path)
        return events


    vol_cmd = [
        sys.executable,
        vol_path
    ]

    
    plugins = (

        (
            "windows.pslist.PsList",
            "Process List"
        ),

        (
            "windows.pstree.PsTree",
            "Process Tree"
        ),

        (
            "windows.netscan.NetScan",
            "Network Connections"
        ),

        (
            "windows.malfind.Malfind",
            "Suspicious Memory Regions"
        ),

    )



    for plugin, label in plugins:


        try:


            result = subprocess.run(

                [
                    *vol_cmd,
                    "-f",
                    filepath,
                    plugin
                ],

                capture_output=True,

                text=True,

                timeout=300,

                errors="ignore"

            )



            print("==============================")
            print("VOLATILITY CMD:")
            print(
                [
                    *vol_cmd,
                    "-f",
                    filepath,
                    plugin
                ]
            )
            print("PLUGIN:", plugin)
            print("RETURN:", result.returncode)

            print("STDERR:")
            print(
                result.stderr[:500]
            )

            print("==============================")



            output = (

                (result.stdout or "")

                +

                "\n"

                +

                (result.stderr or "")

            )



            if not output.strip():

                continue



            filename = (
                plugin
                .replace(".", "_")
                +
                ".txt"
            )


            report_path = os.path.join(
                output_dir,
                filename
            )



            with open(
                report_path,
                "w",
                encoding="utf-8",
                errors="ignore"
            ) as fh:

                fh.write(output)



            line_count = len(
                [
                    x
                    for x in output.splitlines()
                    if x.strip()
                ]
            )



            events.append(

                make_event(

                    timestamp=datetime.utcnow(),

                    computer=os.path.basename(filepath),

                    channel="Memory",

                    event_id=(
                        "MEM-"
                        +
                        plugin.split(".")[-1].upper()
                    ),

                    rule_title=(
                        "Volatility: "
                        +
                        label
                    ),

                    rule_id=(
                        "VOL_"
                        +
                        plugin.split(".")[-1].upper()
                    ),

                    severity=(
                        "medium"
                        if "malfind" in plugin.lower()
                        else "informational"
                    ),

                    details=(
                        f"{label} extracted "
                        f"({line_count} lines). "
                        f"Report: {report_path}"
                    ),

                    extra_info=output[:2000]

                )

            )


        except subprocess.TimeoutExpired:


            print(
                "Volatility timeout:",
                plugin
            )

            continue



        except Exception as ex:


            print(
                "Volatility error:",
                plugin,
                ex
            )

            continue



    return events





def parse_memory_dump(
        filepath,
        output_dir=None
):


    output_dir = output_dir or os.path.dirname(filepath)


    os.makedirs(
        output_dir,
        exist_ok=True
    )



    events=[]



    dump_type=_detect_dump_type(filepath)


    size=os.path.getsize(filepath)



    events.append(

        make_event(

            timestamp=datetime.utcnow(),

            computer=os.path.basename(filepath),

            channel="Memory",

            event_id="MEM-INFO",

            rule_title="Memory Dump Identified",

            rule_id="MEMORY_DUMP_INFO",

            severity="informational",

            details=
            f"{dump_type} | Size {size:,} bytes"

        )

    )



    with open(filepath,"rb") as f:

        sample=f.read(
            min(
                size,
                MAX_STRING_SCAN_BYTES
            )
        )



    strings=_extract_strings(sample)



    for text in strings:


        lower=text.lower()


        for needle,severity,rule_id in MEMORY_IOC_PATTERNS:


            if needle.lower() in lower:


                events.append(

                    make_event(

                        timestamp=datetime.utcnow(),

                        channel="Memory",

                        event_id=
                        f"IOC-{rule_id}",

                        rule_title="Memory IOC Match",

                        rule_id=rule_id,

                        severity=severity,

                        details=text[:500]

                    )

                )

                break




    for hint in PROCESS_HINTS:


        if hint.lower() in sample.lower():


            name=hint.decode()


            events.append(

                make_event(

                    timestamp=datetime.utcnow(),

                    channel="Memory",

                    event_id=f"PROC-{name.upper()}",

                    rule_title="Process String Found",

                    rule_id="MEM_PROCESS_STRING",

                    severity="medium",

                    details=name

                )

            )




    events.extend(

        _run_volatility(

            filepath,

            output_dir

        )

    )


    return events