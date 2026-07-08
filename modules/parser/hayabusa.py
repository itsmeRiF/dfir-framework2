import os
import subprocess
import pandas as pd

from dateutil import parser as dateparser



def run_hayabusa(evtx_path, output_dir, tool_path):


    os.makedirs(
        output_dir,
        exist_ok=True
    )


    evtx_path = os.path.abspath(
        evtx_path
    )

    tool_path = os.path.abspath(
        tool_path
    )


    output_file = os.path.join(
        output_dir,
        "hayabusa.csv"
    )


    evtx_dir = os.path.dirname(
        evtx_path
    )


    cmd = [

        tool_path,

        "csv-timeline",

        "-d",

        evtx_dir,

        "-o",

        output_file,

        "-w",

        "-p",

        "standard",

        "-C",

        "-q"

    ]


    print(
        "Running:",
        " ".join(cmd)
    )


    result = subprocess.run(

        cmd,

        cwd=os.path.dirname(tool_path),

        capture_output=True,

        text=True,

        encoding="utf-8",

        errors="ignore"

    )


    print(result.stdout)


    if result.stderr:

        print(result.stderr)



    if not os.path.exists(output_file):

        raise Exception(

            "Hayabusa did not generate CSV\n"

            + result.stderr

        )



    df = pd.read_csv(
        output_file
    ).fillna("")


    events=[]


    for _,row in df.iterrows():


        try:

            ts=dateparser.parse(
                row["Timestamp"]
            )

        except:

            ts=None



        events.append({

            "timestamp":ts,

            "computer":row.get(
                "Computer",
                ""
            ),

            "channel":row.get(
                "Channel",
                ""
            ),

            "event_id":str(
                row.get(
                    "EventID",
                    ""
                )
            ),

            "record_id":str(
                row.get(
                    "RecordID",
                    ""
                )
            ),

            "rule_title":row.get(
                "RuleTitle",
                ""
            ),

            "rule_id":row.get(
                "RuleID",
                ""
            ),

            "severity":row.get(
                "Level",
                ""
            ),

            "details":row.get(
                "Details",
                ""
            ),

            "extra_info":row.get(
                "ExtraFieldInfo",
                ""
            )

        })


    return events
