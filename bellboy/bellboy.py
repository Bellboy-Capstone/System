# the bellboy app
import argparse
import logging
import os

from thespian.actors import Actor, ActorSystem, ActorTypeDispatcher

import sensors
from sensors import UltrasonicSensor


class BellBoy(ActorTypeDispatcher):
    """Lead actor. Starts other actors and co-ordinates system actions."""

    log = logging.getLogger(__name__)
    event_count = 0

    # ---- MESSAGE HANDLING --- #
    # for now all messages are strings. TO DO change that
    def receiveMsg_str(self, message, sender):
        """Handles string messages sent to the BellBoy actor"""
        self.log.info("Received message %s from sender %s", message, sender)

        if message == "start":
            self.startBellboyServices()

        elif "heartbeat" in message:
            print("Got heartbeat message...")
            self.send(self.gui, "heartbeat")
            self.send(self.sensor, "heartbeat")

        elif message == "sensorModuleRdy":
            # sensor module ready, so request for sensors here
            log.debug("Requesting ultrasonic sensor")
            self.send(self.sensor_handler, "UltrasonicSensorReq")

        elif "sensorReady" in message:
            # sensor response message in form sensorReady-sensorAddress
            # store address of the assigned sensor
            # once weve been assigned an ultrasonic sensor,
            # begin polling data from it, and tell it what event youre waiting on
            self.sensor = message.split("-")[1]
            log.debug("sending begin polling request to sensor")
            self.send(self.sensor, "poll")

        elif "sensorEventOccured" in message:
            # once a sensorEvent happens, the message will describe the event.
            event_count += 1
            log.debug(str.format("event #{}: {}", event_count, message))

            if event_count == 5:
                self.send(self.sensor, "pause")


    def receiveMsg_WakeupMessage(self, message, sender):
        self.log.info("Staying awake.")
        self.wakeupAfter(timedelta(seconds=10))


    # -- START SYSTEM --- #
    def startBellboyServices(self):
        """Starts all other BellBoy system actors."""
        self.log.info("Starting bellboy services.")

        # Create child actors. Ha.
        # stores the address of the actor, not the actual object.
        self.gui = self.createActor(StatusWebGUI)
        self.sensor_handler = self.createActor(sensors.SensorModule)
        self.send(self.sensor_handler, "init")


def configure_logging(log_level):
    """configures logging globally through root logger.
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


def main():
    # cmd line argument handling
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "loglevel",
        metavar="log_level",
        default="INFO",
        nargs="?",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="specify level of logging (default: %(default)s)",
    )
    args = parser.parse_args()

    configure_logging(logging.getLevelName(args.loglevel))

    # create multiprocessing system, housing all our actors
    system = ActorSystem("multiprocQueueBase")

    # create lead actor
    bellboy = system.createActor(BellBoy)
    system.tell(bellboy, "start")


if __name__ == "__main__":
    main()
