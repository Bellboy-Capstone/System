import time
from threading import Thread

from collections import deque

from actors.generic import GenericActor
from actors.lead import GPIO
from utils.messages import (
    Request,
    Response,
    SensorReq,
    SensorReqMsg,
    SensorRespMsg,
    SensorResp,
)
from utils.UltrasonicRanging import pulseIn


# conversion factors
US_PER_SEC = 1000000.0
MS_PER_SEC = 1000.0

# constants
# 6000 entries at a polling rate of 100 ms = 600 secs of data = 5 mins.
BUFFER_SIZE = 6000


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

        """[summary]
        """

    def _setup_sensor(self, trigPin, echoPin, max_depth_cm, pulse_width_us=10):
        """setup sensor paramaters"""
        self._trigPin = trigPin
        self._echoPin = echoPin
        self._max_depth_cm = max_depth_cm
        self._pulse_width = pulse_width_us
        self._time_out = max_depth_cm * 60 * 0.000001
        self.status = SensorResp.READY

        if not self.TEST_MODE:
            GPIO.setmode(GPIO.BOARD)
            # TODO: why isnt setting mode in lead actor reflecting in here..

    def _sensor_loop(self):
        """
        sensor loop, every period it:
            - stores a depth reading, and
            - analyzes recent readings to test for an event
        until thread terminate flag is raised.
        """
        self.status = SensorResp.POLLING
        self._buffer.clear()

        # testing mode enabled, dont want to use actual GPIO.
        if not self.TEST_MODE:
            GPIO.setup(self._trigPin, GPIO.OUT)
            GPIO.setup(self._echoPin, GPIO.IN)

        while not self._terminate_thread:
            distance = 0.0
            t0 = time.time()

            if not self.TEST_MODE:
                # send ultrasonic ping
                t0 = time.time()
                GPIO.output(self._trigPin, GPIO.HIGH)
                time.sleep(self._pulse_width / US_PER_SEC)
                GPIO.output(self._trigPin, GPIO.LOW)

                # calculate distance from reflected ping
                pingTime = pulseIn(self._echoPin, GPIO.HIGH, self._time_out / 0.000001)
                distance = pingTime * 340.0 / 2.0 / 10000.0

            self._buffer.appendleft(distance)
            # check for event, if occurred send msg to subscriber
            event = self._eventFunc(self._buffer)
            if event:
                self.send(self.parent, event)

            # sleep till next period
            dt_sec = time.time() - t0  # TO-DO: ensure dt_sec < poll_period
            time.sleep(self._poll_period / MS_PER_SEC - dt_sec)

        self.log.info("polling thread terminated")

        # cleanup pins, so none are left on
        if not self.TEST_MODE:
            GPIO.cleanup(self._trigPin)
            GPIO.cleanup(self._echoPin)
            self.log.debug(
                str.format("cleared GPIO pins {}, {}", self._trigPin, self._echoPin)
            )
        self.status = SensorResp.READY

    # --------------------------#
    # STATE MODIFYING METHODS   #
    # --------------------------#

    def _begin_polling(self):
        """
        Begins running the polling thread.
        """
        self._terminate_thread = False
        self.log.info("starting sensor's thread")
        self._sensor_thread.start()
        self.status = SensorResp.POLLING

    def _stop_polling(self):
        self.log.debug("Stopping the UltraSonic detection loop...")
        self._terminate_thread = True
        self.status = SensorResp.READY

    def _clear(self):
        self._trigPin = 0
        self._echoPin = 0
        self._max_depth_cm = 0.0
        self._pulse_width = 0.0
        self._time_out = 0.0

        self._eventFunc = None
        self._poll_period = 0.0

        self._buffer.clear()
        self.log.debug("cleared sensor")
        self.status = Response.READY

    # --------------------------#
    # MESSAGE HANDLING METHODS  #
    # --------------------------#

    def receiveMsg_SensorReq(self, message, sender):
        """
        responding to simple sensor requests
        """

        self.log.info(str.format("Received message {} from {}", message, sender))

        if message == SensorReq.STOP:
            if sender != self.parent:
                self.log.warning("Received STOP req from unauthorized sender!")
                self.send(sender, Response.UNAUTHORIZED)
                return

            self._stop_polling()

        elif message == SensorReq.CLEAR:
            if self.status == SensorResp.POLLING:
                self.log.warning(
                    "Polling sensor must be stopped before it can be cleared!"
                )
                self.send(sender, Response.FAIL)
                return

            if sender != self.parent:
                self.log.warning("Received POLL req from unauthorized sender!")
                self.send(sender, Response.UNAUTHORIZED)
                return

            self._clear()

        self.send(sender, self.status)

    def receiveMsg_SensorReqMsg(self, message, sender):
        self.log.info(str.format("Received message {} from {}", message, sender))

        if message.type == SensorReq.SETUP:
            # setup sensor
            if sender != self.parent:
                self.log.warning("Received SETUP req from unauthorized sender!")
                self.send(sender, Response.UNAUTHORIZED)
                return

            self._setup_sensor(
                trigPin=message.trigPin,
                echoPin=message.echoPin,
                max_depth_cm=message.maxDepth_cm,
                pulse_width_us=message.pulseWidth_us,
            )

        elif message.type == SensorReq.POLL:
            if self.status != SensorResp.READY:
                self.log.warning("Sensor isn't setup to start polling!")
                self.send(sender, Response.FAIL)
                return

            if sender != self.parent:
                self.log.warning("Received POLL req from unauthorized sender!")
                self.send(sender, Response.UNAUTHORIZED)
                return

            self._eventFunc = message.sensorEventFunc
            self._poll_period = message.pollPeriod_ms
            self._begin_polling()

        self.send(sender, self.status)

    def receiveMsg_SummaryReq(self, message, sender):
        """sends a summary of the actor."""
        self.send(
            sender,
            SensorRespMsg(
                respType=SensorResp.SUMMARY,
                trigPin=self._trigPin,
                echoPin=self._echoPin,
                maxDepth_cm=self._max_depth_cm,
                pulseWidth_us=self._pulse_width,
            ),
        )
