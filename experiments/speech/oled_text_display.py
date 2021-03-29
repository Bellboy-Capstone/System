# SPDX-FileCopyrightText: 2017 Tony DiCola for Adafruit Industries
# SPDX-FileCopyrightText: 2017 James DeVito for Adafruit Industries
# SPDX-License-Identifier: MIT

# This example is for use on (Linux) computers that are using CPython with
# Adafruit Blinka to support CircuitPython libraries. CircuitPython does
# not support PIL/pillow (python imaging library)!

import time
import subprocess

from board import SCL, SDA
import busio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306


PIX_WIDTH = 128
PIX_HEIGHT = 32
GIF_FPS = 60 

sec_per_frame = 1.0/GIF_FPS


# Create the I2C interface.
i2c = busio.I2C(SCL, SDA)

# Create the SSD1306 OLED class
disp = adafruit_ssd1306.SSD1306_I2C(PIX_WIDTH, PIX_HEIGHT, i2c)

# Clear display.
disp.fill(0)
disp.show()

# Create blank image for drawing. '1' for bitmap
width = disp.width
height = disp.height
image = Image.new("1", (width, height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0, 0, width, height), outline=0, fill=0)

# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = -2
top = padding
bottom = height - padding

# Left corner
x = 0
# Load default font.
font = ImageFont.load_default()

# Alternatively load a TTF font.  Make sure the .ttf font file is in the
# same directory as the python script!
# Some other nice fonts to try: http://www.dafont.com/bitmap.php
# font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 9)

lineCount = 0
text =["","","",""]
first = True
while first:
    text[lineCount] = input("What do u wanna display?\n")
    lineCount = (lineCount + 1)%4

    # clear canvas
    draw.rectangle((0, 0, width, height), outline=0, fill=0)
    
    # Write text
    tIx = 0
    for line in text: 
        draw.text((x, top + tIx*8), line, font=font, fill=255)
        tIx += 1

    # Display image.
    disp.image(image)
    disp.show()
    time.sleep(0.1)
    first = False
