"""
Memory Artifact Importer
"""

from database.db import db

from modules.memory.volatility import VolatilityParser



class MemoryImporter:


    @classmethod
    def import_memory(
        cls,
        case_id,
        output_dir
    ):


        processes=[]
        networks=[]
        iocs=[]



        pslist = (
            output_dir,
            "windows_pslist_PsList.txt"
        )


        netscan = (
            output_dir,
            "windows_netscan_NetScan.txt"
        )


        malfind = (
            output_dir,
            "windows_malfind_Malfind.txt"
        )



        processes.extend(

            VolatilityParser.parse_pslist(

                "/".join(pslist),

                case_id
            )

        )



        networks.extend(

            VolatilityParser.parse_netscan(

                "/".join(netscan),

                case_id
            )

        )



        iocs.extend(

            VolatilityParser.parse_malfind(

                "/".join(malfind),

                case_id
            )

        )



        if processes:
            db.session.bulk_save_objects(
                processes
            )


        if networks:
            db.session.bulk_save_objects(
                networks
            )


        if iocs:
            db.session.bulk_save_objects(
                iocs
            )


        db.session.commit()



        return {

            "processes":len(processes),

            "network":len(networks),

            "ioc":len(iocs)

        }