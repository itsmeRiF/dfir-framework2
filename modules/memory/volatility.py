"""
CyberX DFIR Framework
Memory Volatility Parsers
"""

import os
import csv
import logging

from models.memory_process import MemoryProcess
from models.memory_network import MemoryNetwork
from models.memory_ioc import MemoryIOC

from database.db import db


logger = logging.getLogger(__name__)


class VolatilityParser:


    @staticmethod
    def parse_pslist(
        filepath,
        case_id
    ):

        processes = []


        if not os.path.exists(filepath):
            return processes


        with open(
            filepath,
            "r",
            encoding="utf-8",
            errors="ignore"
        ) as f:

            lines = f.readlines()



        for line in lines:


            if not line.strip():
                continue


            if "PID" in line:
                continue


            parts = line.split()


            if len(parts) < 3:
                continue


            try:

                pid = int(parts[0])
                ppid = int(parts[1])


            except:

                continue



            process_name = parts[2]



            processes.append(

                MemoryProcess(

                    case_id=case_id,

                    pid=pid,

                    ppid=ppid,

                    process_name=process_name,

                    risk=(
                        "high"
                        if process_name.lower()
                        in [
                            "powershell.exe",
                            "mimikatz.exe",
                            "cmd.exe"
                        ]
                        else "low"
                    )

                )

            )


        return processes



    @staticmethod
    def parse_netscan(
        filepath,
        case_id
    ):


        networks=[]


        if not os.path.exists(filepath):
            return networks



        with open(
            filepath,
            "r",
            encoding="utf-8",
            errors="ignore"
        ) as f:


            lines=f.readlines()



        for line in lines:


            if "LocalAddr" in line:
                continue


            parts=line.split()



            if len(parts)<5:
                continue



            networks.append(

                MemoryNetwork(

                    case_id=case_id,

                    protocol=parts[0],

                    local_address=parts[1],

                    remote_address=parts[2],

                    state=parts[3],

                    pid=(
                        int(parts[-1])
                        if parts[-1].isdigit()
                        else None
                    )

                )

            )


        return networks




    @staticmethod
    def parse_malfind(
        filepath,
        case_id
    ):


        iocs=[]


        if not os.path.exists(filepath):
            return iocs



        with open(
            filepath,
            "r",
            encoding="utf-8",
            errors="ignore"
        ) as f:


            data=f.read()



        if data.strip():


            iocs.append(

                MemoryIOC(

                    case_id=case_id,

                    ioc_type="Memory Injection",

                    indicator="Malfind Detection",

                    source="Volatility3",

                    severity="high",

                    description=data[:2000]

                )

            )


        return iocs