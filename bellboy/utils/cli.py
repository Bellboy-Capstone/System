"""Bellboy command line argument processing goes here."""

import logging
import logging.config
import os
from argparse import ArgumentParser


log_filename = "bellboy.log"


def get_bellboy_configs():
    """
    Retrieve bellboy configuration information from command line arguments.

    :return: configs
    :rtype: dict
    """
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

    # using log config dictionary for actor logging, check thespian docs for more
    configs = {}
    configs["logcfg"] = {
        "version": 1,
        "formatters": {
            "standard": {
                "format": "%(asctime)s :: %(levelname)s :: %(name)s :: %(funcName)s() :: %(message)s"
            },
        },
        "handlers": {
            "fh": {
                "class": "logging.FileHandler",
                "filename": log_filename,
                "formatter": "standard",
                "level": args.log_level,
            },
            "sh": {
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
                "formatter": "standard",
                "level": args.log_level,
            },
        },
        "loggers": {"": {"handlers": ["fh", "sh"], "level": logging.DEBUG}},
    }

    configs["run_level"] = args.run_level
    configs["log_level"] = args.log_level
    logging.config.dictConfig(configs["logcfg"])
    logging.getLogger().info(
        str.format(
            "Logging configured to console and {} at {} level",
            os.path.abspath(log_filename),
            logging.getLevelName(logging.getLevelName(args.log_level)),
        )
    )

    return configs
