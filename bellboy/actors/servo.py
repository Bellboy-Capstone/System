import time
from threading import Thread

import gpiozero
from gpiozero import Servo
from gpiozero import AngularServo
from gpiozero.pins.mock import MockFactory
from actors.generic import GenericActor
from collections import deque
from utils.messages import Response, ServoReq, ServoResp, ServoMsg

servoGPIO = 18

OFFSE_DUTY = 0.45  # define pulse offset of servo
SERVO_MAX_DUTY = (
    2.0 + OFFSE_DUTY
) / 1000  # define pulse duty cycle for maximum angle of servo
SERVO_MIN_DUTY = (
    1.0 - OFFSE_DUTY
) / 1000  # define pulse duty cycle for minimum angle of servo


class ServoActor(GenericActor):
    """
    Class for the servo.
    """

    def __init__(self):
        super().__init__()

        # define private attributes
        # the following are set on setup request
        self._servo = None

    # --------------------------#
    # STATE MODIFYING METHODS   #
    # --------------------------#

    def _setup_servo(self):
        """setup servo paramaters"""

        if self.TEST_MODE:
            gpiozero.Device.pin_factory = MockFactory()
            # TODO should this be "globally" set in the test suites...
            # but then will it even be recognized in other domains...

        self._servo = Servo(
            servoGPIO, min_pulse_width=SERVO_MIN_DUTY, max_pulse_width=SERVO_MAX_DUTY
        )

        self.status = ServoResp.SET
        self.log.info("servo setup")

    def _push_button(self):
        """when servo needs to push button"""

        self.status = ServoResp.PUSHINGBUTTON
        self._servo.min()  # or max depending how we set it up
        time.sleep(2.5)
        self._servo.mid()

        self.status = ServoResp.SET
        self.log.info("button pushed")

    def _clear(self):
        self._servo.close()

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

        if message == ServoReq.PUSHBUTTON:
            self._push_button()

        if message == ServoReq.SETUP:
            self._setup_servo()

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
        return ServoMsg(type=Response.SUMMARY)
