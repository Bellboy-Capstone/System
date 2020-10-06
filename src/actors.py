import logging
import random
from datetime import timedelta
from time import sleep

from thespian.actors import Actor, ActorSystem, ActorTypeDispatcher

# https://github.com/malefs/security-smell-detector-python-gist/blob/e90764deb06ae4d3c45e702db7ad00351520348f/gist-hash/b51a9cabd41edae990fd6e844f10ef8e/snippet.py
# https://thespianpy.com/doc/in_depth#outline-container-org9bb4305

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


class BellBoy(ActorTypeDispatcher):
    log = logging.getLogger("BellBoy")

    def receiveMsg_str(self, message, sender):
        self.log.info("Received message %s from sender %s", message, sender)
        if type(message) is str and "start" in message:
            self.startBellboyServices()
        if type(message) is str and "heartbeat" in message:
            print("Got heartbeat message...")
            self.send(self.gui, "heartbeat")
            self.send(self.sensor, "heartbeat")

    def receiveMsg_WakeupMessage(self, message, sender):
        self.log.info("Staying awake.")
        self.wakeupAfter(timedelta(seconds=10))

    def startBellboyServices(self):
        """Starts all other BellBoy system actors."""
        self.log.info("Starting belloboy services...")
        # Create child actors. Ha.
        self.gui = self.createActor(StatusWebGUI)
        self.sensor = self.createActor(Sensor)
        self.send(self.gui, "start")
        self.send(self.sensor, "start")
        self.wakeupAfter(timedelta(seconds=1))


class StatusWebGUI(Actor):
    """Simple actors that inherit from Actor only need to implement recieveMessage."""

    log = logging.getLogger("StatusWebGUI")

    def receiveMessage(self, message, sender):
        self.log.info("Received message %s from sender %s", message, sender)


class Sensor(ActorTypeDispatcher):
    log = logging.getLogger("Sensor")
    parent = None

    def receiveMsg_str(self, message, sender):
        self.log.info("Received message %s from sender %s", message, sender)
        if "start" in message:
            self.parent = sender
            self.wakeupAfter(timedelta(seconds=3))

    def receiveMsg_WakeupMessage(self, message, sender):
        self.log.info("Checking for hand.")
        self.wakeupAfter(timedelta(seconds=3))

        # Randomly detect a hand one in four for now:
        if random.randint(0, 100) < 25:
            self.log.info("Got hand!")
            self.send(self.parent, "Found a hand!")


if __name__ == "__main__":
    # Start each actor in its own process.
    system = ActorSystem("multiprocQueueBase")
    # Without a multiprocessing base, wakeupAfter won't work at all.
    bellboy = system.createActor(BellBoy)
    system.tell(bellboy, "start")
    try:
        while True:
            sleep(5)
            system.tell(bellboy, "heartbeat")
    finally:
        # This call sends an ActorExitRequest to all live actors.
        system.shutdown()
