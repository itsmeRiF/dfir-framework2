import subprocess
import os
from datetime import datetime


BASE_DIR = os.path.dirname(
    os.path.dirname(__file__)
)


HAYABUSA_PATH = os.path.join(
    BASE_DIR,
    "tools",
    "hayabusa.exe"
)


OUTPUT_DIR = os.path.join(
    BASE_DIR,
    "outputs",
    "hayabusa"
)



def run_hayabusa(evtx_folder):


    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True
    )


    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )


    output_file = os.path.join(
        OUTPUT_DIR,
        f"timeline_{timestamp}.csv"
    )


    command = [

        HAYABUSA_PATH,

        "csv-timeline",

        "-d",

        evtx_folder,

        "-o",

        output_file,

        "--no-wizard"

    ]


    try:

        result = subprocess.run(

            command,

            stdout=subprocess.PIPE,

            stderr=subprocess.PIPE,

            text=True,

            timeout=1800

        )


        if result.returncode != 0:

            raise Exception(
                result.stderr
            )


        return output_file



    except Exception as e:

        raise Exception(
            f"Hayabusa failed: {e}"
        )
