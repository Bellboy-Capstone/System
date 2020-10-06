import logging
import time
from datetime import timedelta
from time import sleep

import RPi.GPIO as GPIO
from thespian.actors import Actor, ActorSystem, ActorTypeDispatcher

# Logging
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

# Sensor
trigPin = 16
echoPin = 18
MAX_DISTANCE = 220
timeOut = MAX_DISTANCE * 60

GPIO.cleanup()
GPIO.setmode(GPIO.BOARD)  # use PHYSICAL GPIO Numbering
GPIO.setup(trigPin, GPIO.OUT)  # set trigPin to OUTPUT mode
GPIO.setup(echoPin, GPIO.IN)  # set echoPin to INPUT mode

# Resources
# https://github.com/malefs/security-smell-detector-python-gist/blob/e90764deb06ae4d3c45e702db7ad00351520348f/gist-hash/b51a9cabd41edae990fd6e844f10ef8e/snippet.py
# https://thespianpy.com/doc/in_depth#outline-container-org9bb4305


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
    distances = []
    parent = None

    def receiveMsg_str(self, message, sender):
        self.log.info("Received message %s from sender %s", message, sender)
        if "start" in message:
            self.parent = sender
            self.wakeupAfter(timedelta(seconds=3))
        if "heartbeat" in message:
            self.log.info("Past 10 readings: %s", self.distances)

    def receiveMsg_WakeupMessage(self, message, sender):
        self.wakeupAfter(timedelta(seconds=0.1))
        distance = self.measure()
        self.distances.append(distance)
        # self.log.info("Raw distance is: %f", distance)
        self.analyzeDistance()

        # Prune extra elements
        while len(self.distances) > 10:
            del self.distances[0]

    def analyzeDistance(self):
        average = sum(self.distances) / len(self.distances)
        self.log.info("Average distance: %i cm", average)
        return average

    def measure(self):
        # Pulse HIGH for 10us
        GPIO.output(trigPin, GPIO.HIGH)
        time.sleep(0.00001)
        GPIO.output(trigPin, GPIO.LOW)

        # Wait for output to go high.
        t0 = time.time()
        while GPIO.input(echoPin) != GPIO.HIGH:
            # If pin fails to go high, time out.
            if (time.time() - t0) > timeOut * 0.000001:
                self.log.error("Ultrasonic sensor init timed out.")
                return 0

        # Record start time
        t0 = time.time()
        while GPIO.input(echoPin) == GPIO.HIGH:
            # Return zero if timeout.
            if (time.time() - t0) > timeOut * 0.000001:
                self.log.error("Ultrasonic reading timed out.")
                return 0

        pulseTime = (time.time() - t0) * 1000000
        # Sound travels at 340m/s, distance is half that time.
        distance = pulseTime * 340.0 / 2.0 / 10000.0
        return distance


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
        GPIO.cleanup()
