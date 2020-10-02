# Sensor classes
# Sensors include Camera, Ultrasonicm Mic....
from threading import Thread
import time
import Rpi.GPIO as GPIO
import abc
import picamera
 
class AbstractSensor(abc.ABC):

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
        self._sensor_thread = Thread(target=read_sensor)
    
    # setup the sensor
    @abc.abstractmethod
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
    
    def pause_sensor_thread(self):


    
class TestSensor(AbstractSensor):
    def __init__(self):
        super().__init__(300)
    

class RPICamSensor(AbstractSensor):
    def __init__(self, poll_period_us):
        super().__init__(poll_period_us)

    def init_sensor:
    picam = picamera.PiCamera()



class UltrasonicSensor(AbstractSensor):
     def __init__(self, poll_period_us):
        super().__init__(poll_period_us)

class MicrophoneSensor(AbstractSensor):
     def __init__(self, poll_period_us):
        super().__init__(poll_period_us)