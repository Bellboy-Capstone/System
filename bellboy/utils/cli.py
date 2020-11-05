"""
Setup of Bellboy run configurations, i.e. logging and run level.

All command line processing here.
"""

import logging
import os
from argparse import ArgumentParser


def configure_logging(log_level):
    """
    configures logging globally through root logger.

    :param log_level: log verbosity
    :type log_level: logging.LEVEL
    """
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


# parse arguments


def configure_bellboy():
    # command line argument parsing
    parser = ArgumentParser(
        prog="python<x> main.py",
        description="Bellboy embedded Python 3 program, for use on Rasperry Pi 3/4 systems.",
        epilog="To develop locally, use DEBUG and LOCAL_STANDALONE settings.",
    )

    # Log Level
    parser.add_argument(
        "-l",
        dest="log_level",
        type=str,
        default="INFO",
        nargs="?",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Log Level: Specify level of logging (default: %(default)s)",
    )

    # Run Configuration (Local/Local-Standalone/Production)
    parser.add_argument(
        "-r",
        dest="run_level",
        default="LOCAL",
        type=str,
        nargs="?",
        choices=["LOCAL", "PRODUCTION"],
        help="Run Level: Specify features to use (default: %(default)s), "
        "LOCAL runs the system contacting services at localhost:8000, "
        "LOCAL_STANDALONE runs the system without networking, "
        "PRODUCTION runs against Heroku-deployed network services.",
    )
    args = parser.parse_args()

    # configure system to chosen settings.
    configure_logging(args.log_level)
    logging.getLogger().info(
        f"Running at log level {args.log_level} and run level {args.run_level}"
    )
