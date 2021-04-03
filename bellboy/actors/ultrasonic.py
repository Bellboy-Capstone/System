import time
from datetime import datetime
from threading import Thread

import gpiozero
from actors.generic import GenericActor
from collections import deque
from gpiozero import DistanceSensor
from gpiozero.pins.mock import MockFactory
from utils.messages import Response, SensorMsg, SensorReq, SensorResp


# conversion factors
US_PER_SEC = 1000000.0
MS_PER_SEC = 1000.0

# constants
# 6000 entries at a polling rate of 100 ms = 600 secs of data = 5 mins.
BUFFER_SIZE = 6000


class UltrasonicActor(GenericActor):
    """
    Class for the ultrasonic sensor.

    Contains a polling thread which can be run or stopped on message
    request.
    """

    def __init__(self):
        super().__init__()

        # define private attributes
        # the following are set on setup request
        self._trigPin = 0
        self._echoPin = 0
        self._max_depth_cm = 0.0
        self._sensor = None
        self._detection_timeout_seconds = 3
        self._last_detection_time = datetime.now()

        # the following are set on poll request
        self._eventFunc = None
        self._poll_period = 0.0

        # for data collection and polling
        self._buffer = deque(maxlen=BUFFER_SIZE)
        self._sensor_thread = None
        self._terminate_thread = True

    # --------------------------#
    # STATE MODIFYING METHODS   #
    # --------------------------#

    def _setup_sensor(self, trigPin, echoPin, max_depth_cm):
        """setup sensor paramaters."""
        self._trigPin = trigPin
        self._echoPin = echoPin
        self._max_depth_cm = max_depth_cm

        if not self.TEST_MODE:
            try:
                import RPi  # noqa
            except ImportError:
                self.log.warning("Not on RPI - Offtarget mode on")
                self.TEST_MODE = True

        if self.TEST_MODE:
            gpiozero.Device.pin_factory = MockFactory()
            # TODO should this be "globally" set in the test suites...
            # but then will it even be recognized in other domains...

        self._sensor = DistanceSensor(
            echo=self._echoPin, trigger=self._trigPin, max_distance=max_depth_cm / 100.0
        )

        self.status = SensorResp.SET

    def _sensor_loop(self):
        """
        sensor loop, every period it:

            - stores a depth reading, and
            - analyzes recent readings to test for an event
        until thread terminate flag is raised.
        """
        self.status = SensorResp.POLLING
        self._buffer.clear()
        self.log.info("starting sensor loop")
        while not self._terminate_thread:

            t0 = time.time()
            if not self.TEST_MODE:
                self._buffer.appendleft(self._sensor.distance * 100.0)

                # check for event
                event = self._eventFunc(self._buffer)

                # send event if last one not too recent
                now = datetime.now()
                timegap = now.timestamp() - self._last_detection_time.timestamp()
                if event:
                    # Make sure at least <timeout seconds> have passed between activations.
                    if timegap < self._detection_timeout_seconds:
                        self.log.debug(
                            "Sensor cooldown period in effect, last event occured %s sec ago",
                            timegap,
                        )
                    else:
                        self.send(self.parent, event)

                    self._last_detection_time = now

            # sleep till next period, or next mltiple of period
            dt_msec = (time.time() - t0) * MS_PER_SEC
            if dt_msec > self._poll_period:
                self.log.warning(
                    "operation took %s ms, consider having a longer poll period.",
                    dt_msec,
                )

            time.sleep(((self._poll_period - dt_msec) % self._poll_period) / MS_PER_SEC)

        self.log.info("polling thread terminated")
        self.status = SensorResp.SET

    def _begin_polling(self):
        """Begins running the polling thread."""
        self._terminate_thread = False
        self._sensor_thread = Thread(target=self._sensor_loop)
        self._sensor_thread.start()
        self.status = SensorResp.POLLING

    def _stop_polling(self):
        if self._terminate_thread:
            self.log.debug("no thread to stop")
            return

        self.log.debug("Stopping the Ultrasonic detection loop...")
        self._terminate_thread = True

    def _clear(self):
        self._trigPin = 0
        self._echoPin = 0
        self._max_depth_cm = 0.0

        self._sensor.close()

        self._eventFunc = None
        self._poll_period = 0.0

        self._buffer.clear()
        self.log.debug("cleared sensor")
        self.status = Response.READY

    # --------------------------#
    # MESSAGE HANDLING METHODS  #
    # --------------------------#

    def receiveMsg_SensorReq(self, message, sender):
        """responding to simple sensor requests."""

        self.log.info("Received message %s from %s", message, self.nameOf(sender))

        # ignore unauthorized requests
        if sender != self.parent:
            self.log.warning("Received %s req from unauthorized sender!", message)

            self.send(sender, Response.UNAUTHORIZED)
            return

        if message == SensorReq.STOP:
            self._stop_polling()

        elif message == SensorReq.CLEAR:
            if self.status == SensorResp.POLLING:
                self.log.warning(
                    "Polling sensor must be stopped before it can be cleared!"
                )
                self.send(sender, Response.FAIL)
                return
            self._clear()

    def receiveMsg_SensorMsg(self, message: SensorMsg, sender):
        self.log.info("Received message %s from %s", message, self.nameOf(sender))

        if sender != self.parent:
            self.log.warning("Received %s req from unauthorized sender!", message.type)
            self.send(sender, Response.UNAUTHORIZED)
            return

        if message.type == SensorReq.SETUP:
            self._setup_sensor(
                trigPin=message.trigPin,
                echoPin=message.echoPin,
                max_depth_cm=message.maxDepth_cm,
            )

        elif message.type == SensorReq.POLL:
            if self.status != SensorResp.SET:
                self.log.warning("Sensor isn't setup to start polling!")
                self.send(sender, Response.FAIL)
                return

            self._eventFunc = message.sensorEventFunc
            self._poll_period = message.pollPeriod_ms
            self._begin_polling()

        self.send(sender, self.status)

    # ----------#
    # OVERRIDES #
    # ----------#

    def teardown(self):
        """Sensor teardown, ensures polling thread is dead."""
        self._stop_polling()
        self._clear()

    def summary(self):
        """sends a summary of the actor."""
        return SensorMsg(
            type=Response.SUMMARY,
            trigPin=self._trigPin,
            echoPin=self._echoPin,
            maxDepth_cm=self._max_depth_cm,
        )
