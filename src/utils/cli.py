import logging
import os
from argparse import ArgumentParser


class CLI:
    """Opens the program with specific networking and logging settings."""

    args = None
    log_file = ""
    run_level = ""

    def parse_args(self):
        parser = ArgumentParser()

        # Log Level
        parser.add_argument(
            "loglevel",
            metavar="log_level",
            default="INFO",
            nargs="?",
            choices=["DEBUG", "INFO", "WARNING", "ERROR"],
            help="specify level of logging (default: %(default)s)",
        )

        # Log File
        parser.add_argument(
            "loglevel",
            metavar="log_level",
            default="INFO",
            nargs="?",
            choices=["DEBUG", "INFO", "WARNING", "ERROR"],
            help="specify level of logging (default: %(default)s)",
        )

        # Run Configuration (Local/Local-Standalone/Production)
        parser.add_argument(
            "loglevel",
            metavar="log_level",
            default="INFO",
            nargs="?",
            choices=["DEBUG", "INFO", "WARNING", "ERROR"],
            help="specify level of logging (default: %(default)s)",
        )

        self.args = parser.parse_args()
        self.configure_logging(logging.getLevelName(self.args.loglevel))

    def configure_logging(self, log_level):
        log_filename = "bellboy_log.txt"
        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)

        # create file logging handler & console logging handler
        fh = logging.FileHandler(log_filename)
        fh.setLevel(log_level)
        ch = logging.StreamHandler()
        ch.setLevel(log_level)

        # create formatter and add it to the handlers
        formatter = logging.Formatter(
            "%(asctime)s :: %(levelname)s :: %(name)s :: %(funcName)s() :: %(message)s"
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        # add the handlers to the logger
        root_logger.addHandler(fh)
        root_logger.addHandler(ch)
        root_logger.info(
            "Logging configured to console and {} at {} level".format(
                os.path.abspath(log_filename),
                logging.getLevelName(root_logger.getEffectiveLevel()),
            )
        )
