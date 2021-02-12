import time
from threading import Thread

import gpiozero
from gpiozero import Servo
from gpiozero import AngularServo
from gpiozero.pins.mock import MockFactory
from actors.generic import GenericActor
from collections import deque
from utils.messages import Response, ServoReq, ServoResp, ServoMsg


OFFSE_DUTY = 0.5        #define pulse offset of servo
SERVO_MIN_DUTY = 2.5+OFFSE_DUTY     #define pulse duty cycle for minimum angle of servo
SERVO_MAX_DUTY = 12.5+OFFSE_DUTY    #define pulse duty cycle for maximum angle of servo
servoPin = 12

lass UltrasonicActor(GenericActor):
    """
    Class for the servo.
    """

    def __init__(self):
        super().__init__()

        # define private attributes
        # the following are set on setup request
        self._servoPin = 0
        self._servoOffset = 0
        self._servoMin = 0
        self._servoMax = 0
        self._servo = None


    # --------------------------#
    # STATE MODIFYING METHODS   #
    # --------------------------#

    def _setup_servo(self, servoPin, servoOffset, servoMin, servoMax):
        """setup servo paramaters"""
        self._servoPin = servoPin
        self._servoOffset = servoOffset
        self._servoMin = servoMin
        self._servoMax = servoMax

        if self.TEST_MODE:
            gpiozero.Device.pin_factory = MockFactory()
            # TODO should this be "globally" set in the test suites...
            # but then will it even be recognized in other domains...

        self._servo = ServoMotor(
            pin=self._servoPin, offset=self._servoOffset, min=self._servoMin, max=self._servoMax
        )

        self.status = ServoResp.SET



    def _clear(self):
        self._servoPin = 0
        self._servoOffset = 0
        self._servoMin = 0
        self._servoMax = 0

        self._servo.close()


        self._buffer.clear()
        self.log.debug("cleared servo")
        self.status = Response.READY

    # --------------------------#
    # MESSAGE HANDLING METHODS  #
    # --------------------------#

    def receiveMsg_ServoReq(self, message, sender):
        """
        responding to simple servo requests
        """

        self.log.info(str.format("Received message {} from {}", message, sender))

        # authorize
        if sender != self.parent:
            self.log.warning(
                str.format("Received {} req from unauthorized sender!", message)
            )
            self.send(sender, Response.UNAUTHORIZED)
            return

        if message == ServoReq.STOP:
            self.clear()

    def receiveMsg_ServoMsg(self, message: ServoMsg, sender):
        self.log.info(str.format("Received message {} from {}", message, sender))

        if sender != self.parent:
            self.log.warning(
                str.format("Received {} req from unauthorized sender!", message.type)
            )
            self.send(sender, Response.UNAUTHORIZED)
            return

        if message.type == ServoReq.SETUP:
            self._setup_servo(
                servoPin = message.servoPin,
                servoOffset = message.servoOffset,
                servoMin = message.servoMin,
                servoMax = message.servoMax
            )

    def teardown(self):
        """
        Actor's teardown sequence, called before shutdown.

        (i.e. close threads, disconnect from services, etc)
        """
        self.clear()

    def summary(self):
        """
        Returns a summary of the actor.

        The summary can be any detailed msg described in the messages module.
        :rtype: object
        """
        return ServoMsg(
            type = Response.SUMMARY,
            servoPin = self._servoPin
            servoOffset = self._servoOffset
            servoMin = self._servoMin
            servoMax = self._servoMax

        )
