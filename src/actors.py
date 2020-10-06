import logging
from datetime import timedelta
from time import sleep

from thespian.actors import Actor, ActorSystem

# https://github.com/malefs/security-smell-detector-python-gist/blob/e90764deb06ae4d3c45e702db7ad00351520348f/gist-hash/b51a9cabd41edae990fd6e844f10ef8e/snippet.py
# https://thespianpy.com/doc/in_depth#outline-container-org9bb4305


class BellBoy(Actor):
    def receiveMessage(self, message, sender):
        logging.info("BellBoy got message %s", message)
        if type(message) is str and "start" in message:
            self.startBellboyServices()
        if type(message) is str and "heartbeat" in message:
            print("Got heartbeat message...")
            self.send(self.gui, "heartbeat")
            self.send(self.sensor, "heartbeat")
        else:
            self.wakeupAfter(timedelta(seconds=1), "wakeup")

    def startBellboyServices(self):
        """Starts all other BellBoy system actors."""
        logging.info("Starting belloboy services...")
        self.gui = self.createActor(StatusWebGUI)
        self.sensor = self.createActor(Sensor)
        self.send(self.gui, "start")
        self.send(self.sensor, "start")


class StatusWebGUI(Actor):
    def receiveMessage(self, message, sender):
        logging.info("StatusWebGUI got message %s", message)


class Sensor(Actor):
    def receiveMessage(self, message, sender):
        logging.info("Sensor got message %s", message)


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
        system.shutdown()
