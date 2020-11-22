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
        self.default_text = None

    # --------------------------#
    # STATE MODIFYING METHODS   #
    # --------------------------#

    def setup(self, default_text):
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

        self.default_text = default_text

        self.lcd = Adafruit_CharLCD(pin_rs=0, pin_e=2, pins_db=[4, 5, 6, 7], GPIO=mcp)
        mcp.output(3, 1)     # turn on LCD backlight
        self.lcd.begin(16, 2)     # set number of LCD lines and columns
        self.lcd.autoscroll()
        self.displayText("System Starting...", 5)
        self.status = LcdResp.SET

    def displayText(self, text, duration):
        """Displays text on screen for duration of time"""

        self.printText(text)
        sleep(duration)
        self.clear()
        self.printText(self.default_text)

    def clear(self):
        self.lcd.clear()

        self.log.debug("cleared LCD")
        self.status = Response.READY

    def printText(self, text):
        lines = chop_string(text)
        if lines[0] and len(lines[0]) <= 16:
            self.printLine(lines[0], 0)

        if lines[1] and len(lines[1]) <= 16:
            self.printLine(lines[1], 1)

        elif lines[1] and len(lines[1]) > 16:
            # here we would scroll line 1
            self.printLine(lines[1][:15], 1)


    def printLine(self, text, lineNum):
        """
        Prints one text to the top or bottom line of the lcd.
        """        
        if (len(text) > 16):
            self.log.warning("<"+text+ "> TOO LONG FOR LCD!")
            return

        if lineNum != 0 and lineNum != 1 :
            self.log.warning("line number must be 0 or 1")
            return

        self.lcd.setCursor(0, lineNum)
        self.lcd.message("                ")
        self.lcd.setCursor(0, lineNum)
        self.lcd.message(text)

    def chop_string(self, text):
        """"
        Divides sentence into 2 pieces, the first fits in 16 charcaters, the second is the leftover. 
        Already centered if in range of 16 charcaters .
        """
        words = text.split() # split text by whitespace
        builder = None
        finalStrings = []
        firstLine = None

        for word in words:
            if builder is None:
                builder = word
                continue

            if firstLine is None and len(builder) + len(word) + 1 > 16:
                firstLine = builder.center(16, " ")
                builder = word
                continue

            builder += " " + word

        if len(builder) < 16:
            builder = builder.center(16, " ")
        
        return [firstLine, builder]
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
            self.setup(message.defaultText)
            self.send(sender, self.status)

        if message.msgType == LcdReq.DISPLAY:
            self.displayText(message.displayText, message.displayDuration, message.overFlow)

    def teardown(self):
        """
        Actor's teardown sequence, called before shutdown. (i.e. close threads, disconnect from services, etc)
        """
        self.clear()

    def summary(self):
        """
        Returns a summary of the actor. The summary can be any detailed msg described in the messages module.
        :rtype: object
        """
        pass
