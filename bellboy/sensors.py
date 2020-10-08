import logging
import time
from threading import Thread

import RPi.GPIO as GPIO
from thespian.actors import ActorTypeDispatcher

from UltrasonicRanging import pulseIn


logger = logging.getLogger(__name__)

# conversion factors
US_PER_SEC = 1000000


class SensorModule(ActorTypeDispatcher):
    """SensorModule actor handles sensors which connect to RPI.
    Sensors can only be created through a request to this module
    """

    logger = logging.getLogger("SensorModule")

    def __init__(self):
        self._ready = False
        self.sensors = []

    def init_sensor_module(self):
        self.logger.info("initializing sensor module")
        GPIO.setmode(GPIO.BOARD)  # use PHYSICAL GPIO Numbering
        self.logger.debug("GPIO mode set to BOARD")
        self._ready = True

    def teardown_sensor_module(self):
        self.logger.info("tearing down sensor module")

        # end any running threads
        self.logger.debug("ending sensor threads ...")
        for sensor in self.sensors:
            self.send(sensor, "pause")

        GPIO.cleanup()
        self.logger.debug("GPIO cleaned up")
        self._ready = False

    # -- MSG HANDLING -- #
    def receiveMsg_str(self, message, sender):
        self.logger.debug(str.format("Received message {} from {}", message, sender))

        switcher = {
            "init": self.receiveMsg_init,
            "teardown": self.receiveMsg_teardown,
            "UltrasonicSensorReq": self.receiveMsg_UltrasonicSensorReq,
        }

        func = switcher.get(message, self.receiveMsg_unknown)
        func(message, sender)

    def receiveMsg_init(self, message, sender):
        self.logger.debug("in")
        self._subscriber = sender
        self.init_sensor_module()
        self.send(sender, "sensorModuleRdy")
        self.logger.debug(str.format("sent ready message to {}", sender))

    def receiveMsg_teardown(self, message, sender):
        if not self._ready:
            self.logger.warning(
                str.format("nothing to teardown, sensor module not initialized")
            )

        elif sender != self._subscriber:
            self.logger.warning(
                str.format(
                    "teardown request from unauthorized sender {}, ignored", sender
                )
            )

        else:
            self.teardown_sensor_module()
            self._ready = False

    def receiveMsg_UltrasonicSensorReq(self, message, sender):
        """an actor has requested an ultrasonic sensor.
        creates the sensor and send init msg, indicating the actor who requested it/ will be subscribed to it
        """
        if not self._ready:
            self.logger.warning("sensor module not ready!")
            return
        self.logger.debug(str.format("creating UltrasonicSensor for {}", sender))
        sensor = self.createActor(UltrasonicSensor)
        self.sensors.append(sensor)
        self.send(sensor, {"type": "init", "subscriber": sender})

    def receiveMsg_unknown(self, message, sender):
        self.logger.warning("received unknown message: " + message)


# -- EXAMPLE EVENT FUNCTIONS ---#
# these functions analyze an array of data and
# returns the Event which occured as a message, if it happened


def average_distance_lt20(distance_array):
    sum = 0.0
    for distance in distance_array[-5:]:
        if distance == 0.0:
            return None

        sum += distance

    if sum / 5 < 20:
        return {
            "type": "sensorEventOccured",
            "payload": str.format(
                "sensorEventOccurred: average distance was less than 20: {}", sum / 5
            ),
        }
    return None


def buttonXHovered(distance_array):
    # lets say button is within distances 10 - 15.
    for distance in distance_array[-5:]:
        if distance > 15 or distance < 10:
            return None

    return {
        "type": "sensorEventOccured",
        "payload": str.format("sensorEventOccurred: button at 12.5 cm was hovered"),
    }


# sensor blueprint
class AbstractSensor(ActorTypeDispatcher):
    def __init__(self):
        super().__init__()
        self._poll_period = 100000  # 100 ms
        self._buffer = []
        self._sensor_thread = Thread(target=self._sensor_loop)
        self._terminate_thread = True

    # setup the sensor
    def init_sensor(self):
        logger.error(str.format("%(funcName)s not implemented!"))

    # close the sensor
    def close_sensor(self):
        logger.error(str.format("%(funcName)s not implemented!"))

    # loop run in sensor's polling thread
    def _sensor_loop(self):
        logger.error(str.format("%(funcName)s not implemented!"))

    # def join(self):
    #     self._sensor_thread.join()

    def begin(self):
        self._terminate_thread = False
        logger.info("starting sensor's thread")
        self._sensor_thread.start()

    def receiveMsg(self, message, sender):
        logger.error(str.format("%(funcName)s not implemented!"))


class UltrasonicSensor(AbstractSensor):

    logger = logging.getLogger("UltrasonicSensor")

    def init_sensor(
        self,
        ultrasonic_event_func=buttonXHovered,
        poll_period_us=100000,
        trigPin=16,
        echoPin=18,
        max_depth_cm=200,
        pulse_width_us=10,
    ):
        """
        :param poll_period_us: read period of sensor in microseconds
        :type poll_period_us: float
        :param ultrasonic_event_func: function characterizing the event the sensor will listen for.
                                      this function analyzes a data buffer,
                                      and returns the Event which occured, if any.
        :type ultrasonic_event_func: func(arr), returns Event
        """
        self._poll_period = poll_period_us
        self._event_occured = ultrasonic_event_func
        self._trigPin = trigPin
        self._echoPin = echoPin
        self._max_depth_cm = max_depth_cm
        self._pulse_width = pulse_width_us
        self._time_out = max_depth_cm * 60 * 0.000001

        GPIO.setup(trigPin, GPIO.OUT)  # set trigPin to OUTPUT mode
        GPIO.setup(echoPin, GPIO.IN)  # set echoPin to INPUT mode

    def _sensor_loop(self):
        """sensor loop, every period it:
        - stores a depth reading, and
        - analyzes recent readings to test for an event
        until thread terminate flag is raised.
        """
        global logger

        while not self._terminate_thread:

            # send ultrasonic ping
            t0 = time.time()
            GPIO.output(self._trigPin, GPIO.HIGH)
            time.sleep(self._pulse_width / US_PER_SEC)
            GPIO.output(self._trigPin, GPIO.LOW)

            # calculate distance from reflected ping
            pingTime = pulseIn(self._echoPin, GPIO.HIGH, self._time_out / 0.000001)
            distance = pingTime * 340.0 / 2.0 / 10000.0
            self._buffer.append(distance)
            self.logger.debug(
                str.format(
                    "Ultrasonic depth recorded: {}", self._buffer[len(self._buffer) - 1]
                )
            )

            # check for event, if occurred send msg to subscriber
            event = self._event_occured(self._buffer)
            if event:
                self.send(self.subscriber, event)

            # sleep till next period
            dt_sec = time.time() - t0  # TO-DO: ensure dt_sec < poll_period
            time.sleep(self._poll_period / US_PER_SEC - dt_sec)
        self.logger.info("polling thread terminated")

    def receiveMsg_str(self, message, sender):
        """most messages are strings for now """

        logger.info(str.format("Received message {} from {}", message, sender))
        if "poll" in message:
            self.begin()

        elif "pause" in message:
            self._terminate_thread = True

    def receiveMsg_dict(self, message, sender):
        """message handler for more involved messages"""

        if message["type"] == "init":
            self.init_sensor()
            self.subscriber = message["subscriber"]
            self.send(
                self.subscriber, {"type": "sensorReady", "sensorAddr": self.myAddress}
            )
