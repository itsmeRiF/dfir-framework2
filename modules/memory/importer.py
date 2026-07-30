"""
Memory Artifact Importer
"""

import os

from database.db import db

from models.memory_process import MemoryProcess
from models.memory_network import MemoryNetwork
from models.memory_ioc import MemoryIOC

from modules.memory.volatility import VolatilityParser


class MemoryImporter:

    @classmethod
    def import_memory(
        cls,
        case_id,
        output_dir
    ):

        # --------------------------------------------------
        # Remove previous memory analysis for this case
        # --------------------------------------------------

        MemoryProcess.query.filter_by(
            case_id=case_id
        ).delete()

        MemoryNetwork.query.filter_by(
            case_id=case_id
        ).delete()

        MemoryIOC.query.filter_by(
            case_id=case_id
        ).delete()

        db.session.commit()

        # --------------------------------------------------
        # Build file paths
        # --------------------------------------------------

        pslist = os.path.join(
            output_dir,
            "windows_pslist_PsList.txt"
        )

        netscan = os.path.join(
            output_dir,
            "windows_netscan_NetScan.txt"
        )

        malfind = os.path.join(
            output_dir,
            "windows_malfind_Malfind.txt"
        )
        


        pstree = os.path.join(
            output_dir,
            "windows_pstree_PsTree.txt"
        )


        # --------------------------------------------------
        # Parse artifacts
        # --------------------------------------------------

        processes = VolatilityParser.parse_pslist(
            pslist,
            case_id
        )


        tree_processes = VolatilityParser.parse_pstree(
            pstree,
            case_id
        )

        processes.extend(
            tree_processes
        )


        networks = VolatilityParser.parse_netscan(
            netscan,
            case_id
        )

        iocs = VolatilityParser.parse_malfind(
            malfind,
            case_id
        )

        unique = {}

        for p in processes:

            key = (
                p.pid,
                p.process_name
            )

            unique[key]=p


        processes=list(unique.values())

        # --------------------------------------------------
        # Save to database
        # --------------------------------------------------

        try:

            if processes:
                db.session.add_all(processes)

            if networks:
                db.session.add_all(networks)

            if iocs:
                db.session.add_all(iocs)

            db.session.commit()

        except Exception:

            db.session.rollback()
            raise

        # --------------------------------------------------
        # Return summary
        # --------------------------------------------------

        return {

            "processes": len(processes),

            "network": len(networks),

            "ioc": len(iocs)

        }
        
        
        
        