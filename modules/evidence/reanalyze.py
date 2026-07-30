"""
CyberX DFIR Framework
Evidence Re-analysis Engine
"""

import os
import shutil
import logging

from database.db import db

from models.evidence import Evidence
from models.memory_process import MemoryProcess
from models.memory_network import MemoryNetwork
from models.memory_ioc import MemoryIOC


logger = logging.getLogger(__name__)


class EvidenceReanalyzer:


    @classmethod
    def run(cls, evidence_id):


        evidence = Evidence.query.get_or_404(
            evidence_id
        )


        case_id = evidence.case_id



        try:

            logger.info(
                "Starting re-analysis for evidence %s",
                evidence_id
            )


            # ======================================
            # Remove previous parsed database data
            # ======================================


            if evidence.artifact_type == "Memory":


                MemoryProcess.query.filter_by(
                    case_id=case_id
                ).delete()


                MemoryNetwork.query.filter_by(
                    case_id=case_id
                ).delete()


                MemoryIOC.query.filter_by(
                    case_id=case_id
                ).delete()



            # ======================================
            # Remove previous output
            # ======================================


            output_dir = os.path.join(

                "output",

                "evidence",

                str(case_id),

                str(evidence_id)

            )


            if os.path.exists(output_dir):

                shutil.rmtree(
                    output_dir
                )


                logger.info(
                    "Removed old output: %s",
                    output_dir
                )



            # ======================================
            # Reset status
            # ======================================
            
            
            evidence.status = "Processing"

            evidence.error_message = None

            evidence.started_at = db.func.now()

            evidence.completed_at = None


            db.session.commit()



            # ======================================
            # Run parser again
            # ======================================


            from modules.evidence.worker import EvidenceWorker


            result = EvidenceWorker.process(
                evidence_id
            )


            logger.info(
                "Re-analysis completed: %s",
                result
            )


            return {


                "success": True,

                "message":
                "Evidence re-analyzed successfully.",

                "result": result

            }



        except Exception as ex:


            db.session.rollback()


            evidence.status = "Failed"

            evidence.error_message = str(ex)


            db.session.commit()


            logger.exception(
                "Re-analysis failed"
            )


            raise