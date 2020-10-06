# Sensor classes
# Sensors include Camera, Ultrasonicm Mic....
import logging
import time
from abc import ABC, abstractmethod
from threading import Thread

import Rpi.GPIO as GPIO
from picamera import PiCamera

from bellboy.UltrasonicRanging import pulseIn

logger = logging.getLogger("__name__")


class AbstractSensor(ABC):

    # constructor.
    # creates private variables for:
    #   the sensor's data buffer,
    #   the polling period, and
    #   the sensor's polling thread
    # @param poll_period_us time inbetween sensor reads, in microseconds
    def __init__(self, poll_period_us):

        self._poll_period = poll_period_us
        self._buffer = []
        super().__init__()
        self._sensor_thread = Thread(target=self.read_sensor)

    # setup the sensor
    @abstractmethod
    def init_sensor(self):
        pass

    # close the sensor
    @abstractmethod
    def close_sensor(self):
        pass

    # string rep of sensors current status
    @abstractmethod
    def brief_status(self):
        pass

    @abstractmethod
    # read sensor once.
    # to be called continuously in sensor's thread
    def read_sensor(self):
        # wait for self._poll_period
        pass

    def run_sensor_thread(self):
        self._sensor_thread.start()


class TestSensor(AbstractSensor):
    def __init__(self):
        super().__init__(300)


class RPICamSensor(AbstractSensor):
    def __init__(self, poll_period_us):
        super().__init__(poll_period_us)
        self.picam: PiCamera = PiCamera()

    def init_sensor(self):
        pass

    def close_sensor(self):
        pass

    def brief_status(self):
        pass

    def read_sensor(self):
        pass


class UltrasonicSensor(AbstractSensor):
    def __init__(self, poll_period_us):
        super().__init__(poll_period_us)

    # setup the sensor
    def init_sensor(self, trigPin=16, echoPin=18, max_depth_cm=200, pulse_width_us=10):
        self._trigPin = trigPin
        self._echoPin = echoPin
        self._max_depth_cm = max_depth_cm
        self._pulse_width = pulse_width_us
        self._time_out = max_depth_cm * 60 * 0.000001

    # close the sensor
    @abstractmethod
    def close_sensor(self):
        pass

    # string rep of sensors current status
    @abstractmethod
    def brief_status(self):
        pass

    @abstractmethod
    # read sensor once.
    # to be called continuously in sensor's thread
    def read_sensor(self):
        # send high pulse
        GPIO.output(self._trigPin, GPIO.HIGH)
        time.sleep(self._pulse_width / 1000000.0)  # us --> sec
        GPIO.output(self._trigPin, GPIO.LOW)  # make trigPin output LOW level
        pingTime = pulseIn(
            self._echoPin, GPIO.HIGH, self._time_out
        )  # read plus time of echoPin
        self._buffer.append(pingTime)
        logger.debug(
            str.format(
                "Ultrasonic depth recorded: {}", self._buffer[len(self._buffer) - 1]
            )
        )

    def pulseIn(self, pin, level, timeOut):  # obtain pulse time of a pin under timeOut
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


class MicrophoneSensor(AbstractSensor):
    def __init__(self, poll_period_us):
        super().__init__(poll_period_us)
