import time
from threading import Thread

import gpiozero
from gpiozero import LiquidCrystal
from gpiozero.pins.mock import MockFactory
from actors.generic import GenericActor
from collections import deque
#from utils.messages import
from bellboy.actors.generic import GenericActor

# from bellboy.utils.messages import

self._sdaPin = 2
self._sclPin = 3

class LiquidCrystalActor(GenericActor):
    """
    Class for the LCD Display.

    Contains a polling thread which can be run or stopped on message
    request.
    """
    def __init__(self):
        super().__init__()

        # define private attributes
        # the following are set on setup request

        self._LCD = None

    # --------------------------#
    # STATE MODIFYING METHODS   #
    # --------------------------#

    def _setup_LCD(self,_sdaPin, sclPin):
        """setup LCD paramaters."""
        self._sdaPin=_sdaPin
        self._sclPin= sclPin
        
        if self.TEST_MODE:
            gpiozero.Device.pin_factory = MockFactory()
            # TODO should this be "globally" set in the test suites...
            # but then will it even be recognized in other domains...

        self._LCD = LiquidCrystal(
            sdaPin=self._sdaPin, 
            sclPin=self._sclPin

        )

        self.status = LCDResp.SET


    def _clear(self):
        self._sdaPin = 0
        self._sclPin = 0


        self._LCD.close()

        self._buffer.clear()
        self.log.debug("cleared LCD")
        self.status = Response.READY

    # --------------------------#
    # MESSAGE HANDLING METHODS  #
    # --------------------------#

    def receiveMsg_LCDReq(self, message, sender):
        """responding to simple LCD requests."""

        self.log.info(
            str.format("Received message {} from {}", message, self.nameOf(sender))
        )

        # ignore unauthorized requests
        if sender != self.parent:
            self.log.warning(
                str.format("Received {} req from unauthorized sender!", message)
            )
            self.send(sender, Response.UNAUTHORIZED)
            return



        elif message == LCDReq.CLEAR:
            self._clear()

    def receiveMsg_LCDMsg(self, message: LCDMsg, sender):
        self.log.info(
            str.format("Received message {} from {}", message, self.nameOf(sender))
        )

        if sender != self.parent:
            self.log.warning(
                str.format("Received {} req from unauthorized sender!", message.type)
            )
            self.send(sender, Response.UNAUTHORIZED)
            return

        if message.type == LCDReq.SETUP:
            self._setup_LCD(
            _sdaPin=self._sdaPin, 
                sclPin=self._sclPin
            )

    def receiveMsg_SummaryReq(self, message, sender):
        """sends a summary of the actor."""
        self.send(
            sender,
            LCDMsg(
                type=Response.SUMMARY,
                sdaPin=self._sdaPin, 
                sclPin=self._sclPin
            ),
        )


    pass
