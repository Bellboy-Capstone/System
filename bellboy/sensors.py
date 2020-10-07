import logging
import time
from threading import Thread

import RPi.GPIO as GPIO
from thespian.actors import Actor, ActorSystem, ActorTypeDispatcher

logger = logging.getLogger(__name__)

# conversion factors
US_PER_SEC = 1000000


class SensorModule(Actor):
    """SensorModule actor handles sensors which connect to RPI.
    This class is an interface to the sensors for whoever created it.
    Each sensor is a thespian Actor.
    """

    def __init__(self):
        self._subscriber = None  # subscriber  = Actor who this sensor module belongs to
        self._ready = False

    def init_sensor_module(self):
        GPIO.setmode(GPIO.BOARD)  # use PHYSICAL GPIO Numbering
        logger.debug("GPIO mode set to BOARD")
        self._ready = True

    def teardown_sensor_module(self):
        # TO-DO: nicely kill the sensor threads.
        GPIO.cleanup()  # use PHYSICAL GPIO Numbering
        logger.debug("GPIO cleaned up")
        self._ready = False

    # -- MSG HANDLING --#
    def receiveMsg(self, message, sender):
        logger.debug(str.format("Received message {} from {}", message, sender))

        switcher = {
            "init": receiveMsg_init,
            "teardown": receiveMsg_teardown,
            "UltrasonicSensorReq": receiveMsg_UltrasonicSensorReq,
        }

        func = switcher.get(message, receiveMsg_unknown)

    def receiveMsg_init(self, message, sender):
        self._subscriber = sender
        self.init_sensor_module()
        self.send(sender, "sensorModuleRdy")

    def receiveMsg_teardown(self, message, sender):
        if not self._ready:
            logger.warning(
                str.format("nothing to teardown, sensor module not initialized")
            )

        elif sender != self._subscriber:
            logger.warning(
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
        sensor = self.createActor(UltrasonicSensor)
        self.send(sensor, "init-" + sender)

    def receiveMsg_unknown(self, message, sender):
        logger.warning("received unknown message: " + message)


# sensor blueprint
class AbstractSensor(Actor):
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
        logger.debug("starting sensor's thread")
        self._sensor_thread.start()

    def receiveMsg(self, message, sender):
        logger.error(str.format("%(funcName)s not implemented!"))


class UltrasonicSensor(AbstractSensor):
    def init_sensor(
        self,
        ultrasonic_event_func=average_distance_lt20,
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

    def close_sensor(self):
        GPIO.cleanup()  # release GPIO resource

    def _sensor_loop(self):
        """sensor loop, every period it:
        - stores a depth reading,
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
            pingTime = self.pulseIn(self._echoPin, GPIO.HIGH, self._time_out)
            distance = pingTime * 340.0 / 2.0 / 10000.0
            self._buffer.append(distance)
            logger.debug(
                str.format(
                    "Ultrasonic depth recorded: {}", self._buffer[len(self._buffer) - 1]
                )
            )

            # check for event, if occurred send msg to subscriber
            event = self._event_occured(self._buffer)
            if event:
                self.send(subscriber, event)

            # sleep till next period
            dt_sec = time.time() - t0  # TO-DO: ensure dt_sec < poll_period
            time.sleep(self._poll_period / US_PER_SEC - dt_sec)
        logger.info("polling thread terminated")

    def pulseIn(self, pin, level, timeOut):  # obtain pulse time of a pin under timeOut
        """ultrasonic ranging code copy pasted

        :param pin: [description]
        :type pin: [type]
        :param level: [description]
        :type level: [type]
        :param timeOut: [description]
        :type timeOut: [type]
        :return: [description]
        :rtype: [type]
        """
        t0 = time.time()
        while GPIO.input(pin) != level:
            if (time.time() - t0) > self._time_out:
                return 0

        t0 = time.time()
        while GPIO.input(pin) == level:
            if (time.time() - t0) > self._time_out:
                return 0

        pulseTime = (time.time() - t0) * 1000000
        return pulseTime

    def receiveMsg(self, message, sender):
        """message handler. all msgs are strings for now, so only this method is needed"""

        # init message comes in form "init-subscriber"
        if "init" in message:
            self.init_sensor()
            self.subscriber = message.split("-")[1]
            self.send(self.subscriber, "sensorReady-" + self.Addr)

        elif "poll" in message:
            self.begin()

        elif "pause" in message:
            self._terminate_thread = True


# -- EXAMPLE EVENT FUNCTIONS ---#
# these functions analyze an array of data and
# returns the Event which occured, None if none if it didnt happen


def average_distance_lt20(distance_array):
    sum = 0.0
    for distance in distance_array[-5:]:
        if distance == 0.0:
            return None

        sum += distance

    if sum / 5 < 20:
        return str.format(
            "sensorEventOccurred: average distance was less than 20: {}", sum / 5
        )

    return None


def buttonXHovered(distance_array):
    # lets say button is within distances 10 - 15.
    sum = 0
    for distance in distance_array[-5:]:
        if distance > 15 or distance < 10:
            return None

    return "sensorEventOccurred: buttonX was hovered"
