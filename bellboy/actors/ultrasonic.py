import logging
import time
from threading import Thread

from actors.generic import GenericActor
from actors.lead import GPIO

from collections import deque
from thespian.actors import ActorAddress, ActorTypeDispatcher

from utils.messages import *
from utils.UltrasonicRanging import pulseIn


# conversion factors
US_PER_SEC = 1000000
MS_PER_SEC = 1000

# constants
BUFFER_SIZE = 6000  # 6000 entries at a polling rate of 100 ms = 600 secs of data = 5 mins.

class UltrasonicActor(GenericActor):
    """
    Class for the ultrasonic sensor. Contains a polling thread which can be run or stopped on message request.
    """

    def __init__(self):
        super().__init__()

        # define private attributes
        # the following are set on setup request
        self._trigPin = 0
        self._echoPin = 0
        self._max_depth_cm = 0.0
        self._pulse_width = 0.0
        self._time_out = 0.0
        self.parent = None

        # the following are set on poll request
        self._eventFunc = None
        self._poll_period = 0.0

        # for data collection and polling
        self._buffer = deque(maxlen=BUFFER_SIZE)
        self._sensor_thread = Thread(target=self._sensor_loop)
        self._terminate_thread = True

    def _setup_sensor(self, trigPin, echoPin, max_depth_cm, pulse_width_us=10):
        """setup sensor paramaters"""
        self._trigPin = trigPin
        self._echoPin = echoPin
        self._max_depth_cm = max_depth_cm
        self._pulse_width = pulse_width_us
        self._time_out = max_depth_cm * 60 * 0.000001
        GPIO.setmode(
            GPIO.BOARD
        )  # TODO: why isnt setting mode in lead actor reflecting in here..
        self.log.info(
            str.format("mode: {}", GPIO.getmode())
        )  # use PHYSICAL GPIO Numbering

    def _sensor_loop(self):
        """
        sensor loop, every period it:
            - stores a depth reading, and
            - analyzes recent readings to test for an event
        until thread terminate flag is raised.
        """
        self.log.info(
            str.format("mode: {}", GPIO.getmode())
        )  # use PHYSICAL GPIO Numbering

        GPIO.setup(self._trigPin, GPIO.OUT)
        GPIO.setup(self._echoPin, GPIO.IN)

        while not self._terminate_thread:

            # send ultrasonic ping
            t0 = time.time()
            GPIO.output(self._trigPin, GPIO.HIGH)
            time.sleep(self._pulse_width / US_PER_SEC)
            GPIO.output(self._trigPin, GPIO.LOW)

            # calculate distance from reflected ping
            pingTime = pulseIn(self._echoPin, GPIO.HIGH, self._time_out / 0.000001)
            distance = pingTime * 340.0 / 2.0 / 10000.0

            self._buffer.appendleft(distance)
            self.log.debug(
                str.format(
                    "Ultrasonic depth recorded: {}", self._buffer[len(self._buffer) - 1]
                )
            )

            # check for event, if occurred send msg to subscriber
            event = self._eventFunc(self._buffer)
            if event:
                self.send(self.parent, event)

            # sleep till next period
            dt_sec = time.time() - t0  # TO-DO: ensure dt_sec < poll_period
            time.sleep(self._poll_period / MS_PER_SEC - dt_sec)

        self.log.info("polling thread terminated")

        # cleanup pins, so none are left on
        GPIO.cleanup(self._trigPin)
        GPIO.cleanup(self._echoPin)
        self.log.debug(
            str.format("cleared GPIO pins {}, {}", self._trigPin, self._echoPin)
        )

    def _begin_poling(self):
        """
        Begins running the polling thread.
        """
        self._terminate_thread = False
        self.log.info("starting sensor's thread")
        self._sensor_thread.start()

    def _stop_polling(self):
        self.log.debug("Stopping the UltraSonic detection loop...")
        self._terminate_thread = True

    # --------------------------#
    # MESSAGE HANDLING METHODS #
    # --------------------------#

    def receiveMsg_SensorReq(self, message, sender):
        """
        responding to simple sensor requests
        """

        self.log.info(str.format("Received message {} from {}", message, sender))

        if message == SensorReq.STOP:
            print("here")
            if sender != self.parent:
                self.log.warning("Received STOP req from unauthorized sender!")
                return
            self._stop_polling()


    def receiveMsg_SensorReqMsg(self, message, sender):
        self.log.info(str.format("Received message {} from {}", message, sender))

        if message.type == SensorReq.SETUP:
            # setup sensor
            self._setup_sensor(
                trigPin=message.trigPin,
                echoPin=message.echoPin,
                max_depth_cm=message.maxDepth_cm,
                pulse_width_us=message.pulseWidth_us,
            )
            self.send(self.parent, SensorResp.READY)

        elif message.type == SensorReq.POLL:
            if sender != self.parent:
                self.log.warning("Received POLL req from unauthorized sender!")
                return

            self._eventFunc = message.sensorEventFunc
            self._poll_period = message.pollPeriod_ms
            self._begin_polling()
