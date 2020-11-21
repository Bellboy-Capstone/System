from time import sleep, strftime
from threading import Thread

from utils.LCD_code.Adafruit_LCD1602 import Adafruit_CharLCD
from utils.LCD_code.PCF8574 import PCF8574_GPIO
from actors.generic import GenericActor
from utils.messages import Response, LCDMsg, LCDReq, LCDResp, LCDEvent, LCDEventMsg,
from bellboy.actors.generic import GenericActor


# from bellboy.utils.messages import


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

        self.lcd = None
        self.defualtString = 'Bellboy LCD'

    # --------------------------#
    # STATE MODIFYING METHODS   #
    # --------------------------#

    def _setup_LCD(self):
        """setup LCD paramaters."""
        PCF8574_address = 0x27  # I2C address of the PCF8574 chip.
        PCF8574A_address = 0x3F  # I2C address of the PCF8574A chip.

        # Create PCF8574 GPIO adapter.
        try:
            mcp = PCF8574_GPIO(PCF8574_address)
        except:
            try:
                mcp = PCF8574_GPIO(PCF8574A_address)
            except:
                print('I2C Address Error !')
                exit(1)

        self.lcd = Adafruit_CharLCD(pin_rs=0, pin_e=2, pins_db=[4, 5, 6, 7], GPIO=mcp)

        self.status = LCDResp.SET

    def displayText(self, text, duration):
        """running lcd thread. Displays text on screen"""
        self.lcd.message(text)
        sleep(duration)
        self.lcd.message(default)

    def _clear(self):
        self.lcd.clear()

        self.log.debug("cleared LCD")
        self.status = Response.READY

    # --------------------------#
    # MESSAGE HANDLING METHODS  #
    # --------------------------#
    # updateDisplay(text: str, duration: int)

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

        if message == LCDReq.SETUP:
            self._clear()

        if message == LCDReq.DISPLAY

    def receiveMsg_LCDMsg(self, message: LCDMsg, sender):
        if sender != self.parent:
            self.log.warning(
                str.format("Received {} req from unauthorized sender!", message.type)
            )
            self.send(sender, Response.UNAUTHORIZED)
            return

        if message.msgType == LCDReq.SETUP:
            self._setup_LCD()

        if message.msgType == LCDReq.DISPLAY:
            self.displayText(message.displayText, message.displayDuration)
