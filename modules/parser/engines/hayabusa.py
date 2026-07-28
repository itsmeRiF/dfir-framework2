"""
CyberX DFIR
Hayabusa Engine Wrapper
"""

import csv
import logging
import os
import subprocess
import tempfile

from config import Config

from modules.parser.exceptions import (
    ParserExecutionError
)


logger = logging.getLogger(__name__)


class HayabusaEngine:


    name = "hayabusa"


    @classmethod
    def parse(
        cls,
        filepath
    ):

        try:

            cls._check_binary()


            if not os.path.exists(filepath):

                raise FileNotFoundError(
                    filepath
                )


            output_csv = "hayabusa_test.csv"


            command = [

                Config.HAYABUSA_PATH,

                "csv-timeline",

                "-f",
                filepath,

                "-o",
                output_csv,

                "-w"

            ]


            logger.info(
                "Executing Hayabusa: %s",
                " ".join(command)
            )


            result = subprocess.run(

                command,

                stdout=subprocess.PIPE,

                stderr=subprocess.PIPE,

                text=True,

                encoding="utf-8",

                errors="ignore",

                timeout=600

            )


            print(
            "========== HAYABUSA STDOUT =========="
            )

            print(
            result.stdout
            )


            print(
            "========== HAYABUSA STDERR =========="
            )

            print(
            result.stderr
            )


            if result.returncode != 0:

                raise ParserExecutionError(
                    result.stderr
                )


            if not os.path.exists(
                output_csv
            ):

                raise ParserExecutionError(
                    "Hayabusa did not generate CSV"
                )


            return cls._read_csv(
                output_csv
            )


        except Exception as exc:

            logger.exception(
                "Hayabusa execution failed"
            )

            raise ParserExecutionError(
                str(exc)
            )


    @staticmethod
    def _check_binary():

        if not os.path.exists(
            Config.HAYABUSA_PATH
        ):

            raise ParserExecutionError(
                "Hayabusa executable not found"
            )


    @staticmethod
    def _output_file():

        fd, path = tempfile.mkstemp(
            suffix=".csv"
        )

        os.close(fd)

        return path


    @staticmethod
    def _read_csv(
        csv_file
    ):

        events = []


        with open(

            csv_file,

            "r",

            encoding="utf-8",

            errors="ignore"

        ) as file:


            reader = csv.DictReader(
                file
            )


            for row in reader:

                events.append(
                    row
                )


        return events