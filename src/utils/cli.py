import logging
import os
from argparse import ArgumentParser

from src.utils.constants import LogLevels, RunLevels

global log_level
global run_level


class CLI:
    """Opens the program with specific networking and logging settings."""

    args = None
    log_file = ""

    def setup(self, args):

        # Use the global/static variables for run/log level
        global run_level
        global log_level

        parser = ArgumentParser(
            prog="python<x> main.py",
            description="Bellboy embedded Python 3 program, for use on Rasperry Pi 3/4 systems.",
            epilog="To develop locally, use DEBUG and LOCAL_STANDALONE settings."

        )
        log = logging.getLogger("CLI")

        # Log Level
        parser.add_argument(
            "-l",
            dest="log_level",
            type=str,
            default=LogLevels.DEBUG.name,
            nargs="?",
            choices=LogLevels.get_names(),
            help="Log Level: Specify level of logging (default: %(default)s)",
        )

        # Run Configuration (Local/Local-Standalone/Production)
        parser.add_argument(
            "-r",
            dest="run_level",
            default=RunLevels.LOCAL_STANDALONE.name,
            type=str,
            nargs="?",
            choices=RunLevels.get_names(),
            help="Run Level: Specify features to use (default: %(default)s), "
                 "LOCAL runs the system contacting services at localhost:8000, "
                 "LOCAL_STANDALONE runs the system without networking, "
                 "PRODUCTION runs against Heroku-deployed network services.",
        )

        log.debug("Parsing arguments: %s", args)
        parsed_args = parser.parse_args(args[1:])

        # Persist args to class as enums:
        run_level = RunLevels[parsed_args.run_level]
        log_level = LogLevels[parsed_args.log_level]

        log.info(f"Running at log level {log_level.name} and run level {run_level.name}")

        self.configure_logging(main=True)

    @staticmethod
    def configure_logging(main=False):

        # Use the global log level
        global log_level

        log_level_str = logging.getLevelName(log_level.name)
        log_filename = "bellboy_log.txt"
        root_logger = logging.getLogger()
        root_logger.setLevel(log_level_str)

        # create file logging handler & console logging handler
        fh = logging.FileHandler(log_filename)
        ch = logging.StreamHandler()

        # create formatter and add it to the handlers
        formatter = logging.Formatter(
            "%(asctime)s :: %(levelname)s :: %(name)s :: %(funcName)s() :: %(message)s"
        )

        # add the handlers to the logger
        root_logger.addHandler(fh)
        root_logger.addHandler(ch)

        # Set formatter and levels on all handlers:
        for handler in root_logger.handlers:
            handler.setFormatter(formatter)
            handler.setLevel(log_level_str)

        # If configuring for the first time, log:
        if main:
            root_logger.info(
                "Logging configured to console and {} at {} level".format(
                    os.path.abspath(log_filename),
                    logging.getLevelName(root_logger.getEffectiveLevel()),
                )
            )
