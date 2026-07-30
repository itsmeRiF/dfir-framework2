"""
CyberX DFIR Framework
Memory Volatility Parsers
"""

import os
import logging

from models.memory_process import MemoryProcess
from models.memory_network import MemoryNetwork
from models.memory_ioc import MemoryIOC


logger = logging.getLogger(__name__)


class VolatilityParser:


    # =====================================================
    # PSLIST
    # =====================================================

    @staticmethod
    def parse_pslist(filepath, case_id):

        processes = []

        seen = set()


        if not os.path.exists(filepath):

            logger.warning(
                "PsList file missing: %s",
                filepath
            )

            return processes



        with open(
            filepath,
            "r",
            encoding="utf-8",
            errors="ignore"
        ) as f:


            for line in f:


                line = line.strip()


                if not line:
                    continue



                if (
                    line.startswith("Volatility")
                    or line.startswith("PID")
                    or line.startswith("Offset")
                ):
                    continue



                parts = line.split()


                if len(parts) < 3:
                    continue



                try:

                    pid = int(parts[0])
                    ppid = int(parts[1])

                except ValueError:

                    continue



                process_name = parts[2]


                key = (
                    pid,
                    ppid,
                    process_name.lower()
                )


                if key in seen:
                    continue


                seen.add(key)



                processes.append(

                    MemoryProcess(

                        case_id=case_id,

                        pid=pid,

                        ppid=ppid,

                        process_name=process_name,

                        risk=(

                            "high"

                            if process_name.lower()

                            in (

                                "powershell.exe",
                                "cmd.exe",
                                "mimikatz.exe"

                            )

                            else "low"

                        )

                    )

                )


        logger.info(
            "PsList parsed: %d",
            len(processes)
        )


        return processes





    # =====================================================
    # PSTREE
    # =====================================================

    @staticmethod
    def parse_pstree(filepath, case_id):

        processes = []

        seen = set()


        if not os.path.exists(filepath):

            logger.warning(
                "PsTree file missing: %s",
                filepath
            )

            return processes



        with open(
            filepath,
            "r",
            encoding="utf-8",
            errors="ignore"
        ) as f:


            for line in f:


                line=line.strip()


                if not line:
                    continue



                if (
                    line.startswith("Volatility")
                    or line.startswith("PID")
                    or line.startswith("Offset")
                ):
                    continue



                parts=line.split()



                if len(parts) < 3:
                    continue



                try:

                    pid=int(parts[0])
                    ppid=int(parts[1])


                except ValueError:

                    continue



                process_name=parts[2]



                key=(

                    pid,

                    ppid,

                    process_name.lower()

                )



                if key in seen:
                    continue



                seen.add(key)



                processes.append(

                    MemoryProcess(

                        case_id=case_id,

                        pid=pid,

                        ppid=ppid,

                        process_name=process_name,

                        risk="low"

                    )

                )


        logger.info(
            "PsTree parsed: %d",
            len(processes)
        )


        return processes





    # =====================================================
    # NETSCAN
    # =====================================================

    @staticmethod
    def parse_netscan(filepath, case_id):

        networks=[]

        seen=set()


        if not os.path.exists(filepath):

            logger.warning(
                "NetScan file missing: %s",
                filepath
            )

            return networks



        with open(
            filepath,
            "r",
            encoding="utf-8",
            errors="ignore"
        ) as f:


            for line in f:


                line=line.rstrip("\n")



                if not line:
                    continue



                if (
                    line.startswith("Volatility")
                    or line.startswith("Offset")
                ):
                    continue



                parts=line.split("\t")



                if len(parts)<9:
                    continue



                offset=parts[0].strip()

                proto=parts[1].strip()



                if not offset.startswith("0x"):
                    continue



                if proto not in (

                    "TCPv4",
                    "TCPv6",
                    "UDPv4",
                    "UDPv6"

                ):
                    continue



                try:


                    local_address=f"{parts[2]}:{parts[3]}"

                    remote_address=f"{parts[4]}:{parts[5]}"

                    state=parts[6].strip()


                    pid=None


                    if parts[7].isdigit():

                        pid=int(parts[7])



                    process_name=parts[8].strip()



                    key=(

                        proto,

                        local_address,

                        remote_address,

                        state,

                        pid,

                        process_name.lower()

                    )



                    if key in seen:
                        continue



                    seen.add(key)



                    networks.append(

                        MemoryNetwork(

                            case_id=case_id,

                            protocol=proto,

                            local_address=local_address,

                            remote_address=remote_address,

                            state=state,

                            pid=pid,

                            process_name=process_name

                        )

                    )


                except Exception:


                    logger.exception(
                        "NetScan parsing failed"
                    )

                    continue



        logger.info(
            "NetScan parsed: %d",
            len(networks)
        )


        return networks





    # =====================================================
    # MALFIND
    # =====================================================

    @staticmethod
    def parse_malfind(filepath, case_id):

        iocs=[]


        if not os.path.exists(filepath):

            logger.warning(
                "Malfind file missing: %s",
                filepath
            )

            return iocs



        with open(
            filepath,
            "r",
            encoding="utf-8",
            errors="ignore"
        ) as f:

            lines=f.readlines()



        findings=[]

        current=[]



        for line in lines:


            line=line.strip()


            if not line:
                continue



            if line.startswith("PID:"):


                if current:

                    findings.append(
                        "\n".join(current)
                    )


                current=[line]


            else:

                current.append(line)



        if current:

            findings.append(
                "\n".join(current)
            )



        seen=set()



        for finding in findings:


            fingerprint=hash(
                finding[:500]
            )


            if fingerprint in seen:
                continue



            seen.add(
                fingerprint
            )



            iocs.append(

                MemoryIOC(

                    case_id=case_id,

                    ioc_type="Memory Injection",

                    indicator="Malfind Detection",

                    source="Volatility3",

                    severity="high",

                    description=finding[:2000]

                )

            )



        logger.info(
            "Malfind parsed: %d",
            len(iocs)
        )


        return iocs