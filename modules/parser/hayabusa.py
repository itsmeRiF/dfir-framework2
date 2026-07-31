import os
import subprocess
import pandas as pd

from dateutil import parser as dateparser



def get_value(row, *keys):

    """
    Safely fetch value from Hayabusa CSV row
    supporting multiple versions
    """

    for key in keys:

        if key in row.index:

            value = row.get(key)

            if pd.notna(value):

                value = str(value).strip()

                if value:
                    return value


    return ""




def run_hayabusa(
        evtx_path,
        output_dir,
        tool_path
):


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
        "\n========== HAYABUSA =========="
    )

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



    print(
        result.stdout
    )



    if result.stderr:

        print(
            result.stderr
        )



    if not os.path.exists(output_file):

        raise Exception(

            "Hayabusa did not generate CSV\n"
            +
            result.stderr

        )



    df = pd.read_csv(
        output_file,
        dtype=str
    ).fillna("")



    print(
        "\n========== HAYABUSA CSV COLUMNS =========="
    )

    print(
        df.columns.tolist()
    )

    print(
        "==========================================\n"
    )



    events = []



    for _, row in df.iterrows():


        # ----------------------------
        # Timestamp
        # ----------------------------

        timestamp_raw = get_value(
            row,
            "Timestamp",
            "Time",
            "datetime"
        )


        try:

            timestamp = dateparser.parse(
                timestamp_raw
            )

        except:

            timestamp = None



        # ----------------------------
        # Build normalized event
        # ----------------------------


        event = {


            "timestamp": timestamp,


            "computer": get_value(
                row,
                "Computer",
                "ComputerName",
                "Hostname"
            ),



            "channel": get_value(
                row,
                "Channel",
                "LogFile",
                "Log"
            ),



            "event_id": get_value(
                row,
                "EventID",
                "Event ID"
            ),



            "record_id": get_value(
                row,
                "RecordID",
                "Record ID"
            ),



            "rule_title": get_value(
                row,
                "RuleTitle",
                "Rule Title",
                "Title",
                "Rule",
                "RuleName"
            ),



            "rule_id": get_value(
                row,
                "RuleID",
                "Rule ID"
            ),



            "severity": get_value(
                row,
                "Level",
                "Severity"
            ),



            "details": get_value(
                row,
                "Details",
                "Message",
                "Description"
            ),



            "extra_info": get_value(
                row,
                "ExtraFieldInfo",
                "Extra Field Info"
            ),



            "raw": row.to_dict()

        }



        events.append(
            event
        )



    print(
        f"Hayabusa events parsed: {len(events)}"
    )


    return events