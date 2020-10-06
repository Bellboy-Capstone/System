# the bellboy app
import argparse
import logging
import os

# import sensors

log_filename = "bellboy_log.txt"

# cmd line argument handling

parser = argparse.ArgumentParser()
parser.add_argument(
    "loglevel",
    metavar="log_level",
    default="INFO",
    required=False,
    choices=["DEBUG", "INFO", "WARNING", "ERROR"],
    help="specify level of logging (default: %(default)s)",
)
args = parser.parse_args()


# configures logging.
# first method called during main, so logging configured here will be used for all modules.
def configure_logging(log_level):

    logger = logging.getLogger("bellboy_main")
    logger.setLevel(log_level)

    # create file logging handler & console logging handler
    fh = logging.FileHandler(log_filename)
    fh.setLevel(log_level)
    ch = logging.StreamHandler()
    ch.setLevel(log_level)

    # create formatter and add it to the handlers
    formatter = logging.Formatter(
        "%(asctime)s :: %(name)s :: %(levelname)s :: %(message)s"
    )
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)
    logger.info(
        "Logging configured to console and {} at {} level".format(
            os.path.abspath(log_filename),
            logging.getLevelName(logger.getEffectiveLevel()),
        )
    )


def main():
    configure_logging(logging.getLevelName(args.loglevel))


if __name__ == "__main__":
    main()
