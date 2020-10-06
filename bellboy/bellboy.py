# the bellboy app
import argparse
import logging
import os

import sensors
from sensors import UltrasonicSensor

# cmd line argument handling

parser = argparse.ArgumentParser()
parser.add_argument('loglevel', metavar='log_level', default="INFO", nargs="?",
                    choices=['DEBUG', 'INFO', 'WARNING', "ERROR"],
                    help='specify level of logging (default: %(default)s)')
args = parser.parse_args()


# configures logging.
# first method called during main, so logging configured here will be used for all modules.
def configure_logging(log_level):
    log_filename = "bellboy_log.txt"
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # create file logging handler & console logging handler
    fh = logging.FileHandler(log_filename)
    fh.setLevel(log_level)
    ch = logging.StreamHandler()
    ch.setLevel(log_level)

    # create formatter and add it to the handlers
    formatter = logging.Formatter("%(asctime)s :: %(levelname)s :: %(name)s :: %(funcName)s() :: %(message)s")
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


def main():
    configure_logging(logging.getLevelName(args.loglevel))
    poll_period_us = 60*1000  # 60 ms
    sensors.init_sensor_module()

    ult_sensor = UltrasonicSensor(poll_period_us)
    try:
        ult_sensor.init_sensor()
        ult_sensor.begin()
        ult_sensor.join()

    except KeyboardInterrupt:
        pass

    finally:
        sensors.teardown_sensor_module()


if __name__ == '__main__':
    main()
