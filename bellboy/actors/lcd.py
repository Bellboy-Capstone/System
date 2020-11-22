from time import sleep

from utils.lcd.Adafruit_LCD1602 import Adafruit_CharLCD
from utils.lcd.PCF8574 import PCF8574_GPIO

from actors.generic import GenericActor
from utils.messages import Response, LcdMsg, LcdReq, LcdResp


PCF8574_address = 0x27  # I2C address of the PCF8574 chip.
PCF8574A_address = 0x3F  # I2C address of the PCF8574A chip.


class LcdActor(GenericActor):
    """
    Class for the LCD Display.
    """

    def __init__(self):
        super().__init__()
        self.lcd = None
        self.default_text = "Default Text"

    # --------------------------#
    # STATE MODIFYING METHODS   #
    # --------------------------#

    def setup(self):
        """setup LCD."""
        # Create PCF8574 GPIO adapter.
        try:
            mcp = PCF8574_GPIO(PCF8574_address)
        except:
            try:
                mcp = PCF8574_GPIO(PCF8574A_address)
            except:
                self.log.warning("MCP creation failed!")
                return

        self.lcd = Adafruit_CharLCD(pin_rs=0, pin_e=2, pins_db=[4, 5, 6, 7], GPIO=mcp)
        self.displayText("LCD is ready...", 1)
        self.status = LcdResp.SET

    def displayText(self, text, duration):
        """Displays text on screen"""
        self.lcd.message(text)
        sleep(duration)
        self.lcd.message(self.default_text)

    def clear(self):
        self.lcd.clear()

        self.log.debug("cleared LCD")
        self.status = Response.READY

    # --------------------------#
    # MESSAGE HANDLING METHODS  #
    # --------------------------#


    def receiveMsg_LcdReq(self, message, sender):
        self.log.info(str.format("Received message {} from {}", message, self.nameOf(sender)))

        # authorize
        if sender != self.parent:
            self.log.warning(str.format("Received {} req from unauthorized sender!", message))
            self.send(sender, Response.UNAUTHORIZED)
            return

        # handle cases
        if message == LcdReq.CLEAR:
            self.clear()

    def receiveMsg_LcdMsg(self, message: LcdMsg, sender):
        self.log.info(str.format("Received message {} from {}", message, self.nameOf(sender)))

        # authorize
        if sender != self.parent:
            self.log.warning(str.format("Received {} req from unauthorized sender!", message.type))
            self.send(sender, Response.UNAUTHORIZED)
            return

        # handle cases
        if message.msgType == LcdReq.SETUP:
            self.setup()
            self.send(sender, self.status)

        if message.msgType == LcdReq.DISPLAY:
            self.displayText(message.displayText, message.displayDuration)
