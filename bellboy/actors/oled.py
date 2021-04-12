
from time import sleep
from os import path

from actors.generic import GenericActor
from utils.lcd.Adafruit_LCD1602 import Adafruit_CharLCD
from utils.messages import LcdMsg, LcdReq, LcdResp, Response

from threading import Thread
from board import SCL, SDA
import busio
from PIL import Image, ImageDraw, ImageFont, ImageSequence
import adafruit_ssd1306

CHARS_PER_LINE = 21
PIX_WIDTH = 128
PIX_HEIGHT = 64
GIF_FPS = 60 


basepath = path.dirname(__file__)
gif_name = "audio_animation_128x64.gif"
gif_path = path.abspath(path.join(basepath, "..", "utils", "oled", gif_name))
i2c_addr = 0x3d # 0x3c for 128x32, 0x3d for 128x64

sec_per_frame = 1.0/GIF_FPS
font = ImageFont.load_default()

class OledActor(GenericActor):
    """Class for the LCD Display."""

    def __init__(self):
        super().__init__()

    # --------------------------#
    # STATE MODIFYING METHODS   #
    # --------------------------#

    def setup(self, default_text):
        
        self.default_text = default_text
        # Create the I2C interface.
        i2c = busio.I2C(SCL, SDA)

        # Create the SSD1306 OLED class
        self.oled = adafruit_ssd1306.SSD1306_I2C(PIX_WIDTH, PIX_HEIGHT, i2c, addr=i2c_addr)

        # Clear display.
        self.oled.fill(0)
        self.oled.show()

        self.width = self.oled.width
        self.height = self.oled.height

        # define some constants to allow easy resizing of shapes.
        padding = -2
        self.top = padding
        self.bottom = self.height - padding

        self.canvas = Image.new("1", (self.width, self.height))
        self.painter = ImageDraw.Draw(self.canvas)

        # gather gif from file
        gif = Image.open(gif_path)
        self.gif_frames = []

        for frame in ImageSequence.Iterator(gif):
            # add frames as '1' bit maps.
            self.gif_frames.append(frame.convert('1'))


        self.displayText("System Starting...", 2)
        self.status = LcdResp.SET

    def displayText(self, text, duration):
        """Displays text on screen for duration of time, then returns to
        default message."""

        self.interrupted = True # end gif thread
        if self.TEST_MODE:
            self.log.info("Mock OLED DISPLAY: " + text)
            sleep(self.duration)
            return


        # maybe put ti in a thread so it can be interuuptable?
        # idk if msg handling and thisfucntions happen in parallel
        self.printText(text)
        sleep(duration)
        # while(self.duration > 0 and not interrupted)
        #     sleep(sec_per_frame)
        #     self.duration -= sec_per_frame
        
        self.duration = 0
        self.interrupted = False

        #self.display_gif()
        self.printText(self.default_text)


    def clearScreen(self):
        # Clear display.
        self.oled.fill(0)
        self.oled.show()

    def printText(self, text):
        """
        Prints text to the LCD.
        Text will persist until cleared.
        """
        # clean the canvas
        self.painter.rectangle((0, 0, self.width, self.height), outline=0, fill=0)

        lines = self.chop_string(text)
        lineNum = 0

        for line in lines:
            # paint text in white
            left_corner = (0, self.top + lineNum*8)
            self.painter.text(left_corner, line, font=font, fill=255)
            lineNum += 1

        # display the image
        self.oled.image(self.canvas)
        self.oled.show()


    def chop_string(self, text):
        """
        Divides sentence into 4 pieces, the first fits in 16 charcaters, the
        second is the leftover.

        Already centered if in range of 16 charcaters .
        """
        words = text.split()  # split text by whitespace
        sIx = 0
        endIx = 0 # start and end of substring
        lineCount = 0

        lines = []
        while sIx < len(text) and lineCount < 4:
            endIx = sIx + CHARS_PER_LINE
            if endIx > len(text):
                endIx = len(text)

            lines.append(text[sIx:endIx])
            sIx = endIx
            lineCount += 1

        return lines

    def display_gif(self):
        self.gif_thread = Thread(target=self.gif_thread_loop)
        self.gif_thread.start()

    def gif_thread_loop(self):
        #self.clearScreen()
                # clean the canvas
        self.painter.rectangle((0, 0, self.width, self.height), outline=0, fill=0)

        fIx = 0
        while not self.interrupted:
            self.oled.image(self.gif_frames[fIx])
            self.oled.show()
            sleep(sec_per_frame)
            fIx = (fIx + 1)%len(self.gif_frames)

        
    # --------------------------#
    # MESSAGE HANDLING METHODS  #
    # --------------------------#

    def receiveMsg_LcdReq(self, message, sender):
        self.log.info(
            str.format("Received message {} from {}", message, self.nameOf(sender))
        )
        pass

    def receiveMsg_LcdMsg(self, message: LcdMsg, sender):
        self.log.info(
            str.format("Received message {} from {}", message, self.nameOf(sender))
        )

        # handle cases
        if message.msgType == LcdReq.SETUP:
            self.setup(message.defaultText)
            self.send(sender, self.status)

        if message.msgType == LcdReq.DISPLAY:
            self.displayText(message.displayText, message.displayDuration)


    def teardown(self):
        """
        Actor's teardown sequence, called before shutdown.

        (i.e. close threads, disconnect from services, etc)
        """
        self.interrupted = True
        self.clearScreen()

    def summary(self):
        """
        Returns a summary of the actor.

        The summary can be any detailed msg described in the messages module.
        :rtype: object
        """
        pass

