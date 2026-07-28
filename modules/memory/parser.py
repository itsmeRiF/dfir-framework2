import os

from modules.memory.pslist import parse_pslist
from modules.memory.netscan import parse_netscan
from modules.memory.malfind import parse_malfind



def parse_memory_folder(folder):

    results = {}


    pslist = os.path.join(
        folder,
        "pslist.txt"
    )

    if os.path.exists(pslist):

        results["processes"] = parse_pslist(
            pslist
        )


    netscan = os.path.join(
        folder,
        "netscan.txt"
    )


    if os.path.exists(netscan):

        results["network"] = parse_netscan(
            netscan
        )


    malfind = os.path.join(
        folder,
        "malfind.txt"
    )


    if os.path.exists(malfind):

        results["malfind"] = parse_malfind(
            malfind
        )


    return results