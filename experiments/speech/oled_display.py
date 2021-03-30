# code to display a gif to OLED
import time
import adafruit_ssd1306
import busio
from board import SCL, SDA
from PIL import Image, ImageDraw, ImageFont, ImageSequence

PIX_WIDTH = 128
PIX_HEIGHT = 32
GIF_FPS = 60 

sec_per_frame = 1.0/GIF_FPS


# gather gif from file
gif_path = "audio_animation_128x32.gif"
gif_name = gif_path.split('.')[0]
gif = Image.open(gif_path)
frames = []

for frame in ImageSequence.Iterator(gif):
    # add frames as '1' bit maps.
    frames.append(frame.convert('1'))


# Create the I2C interface.
i2c = busio.I2C(SCL, SDA)

# Create the SSD1306 OLED class
disp = adafruit_ssd1306.SSD1306_I2C(PIX_WIDTH, PIX_HEIGHT, i2c)

# Clear display.
disp.fill(0)
disp.show()

fIx = 0
while True:
    disp.image(frames[fIx])
    disp.show()
    time.sleep(sec_per_frame)
    fIx = (fIx + 1)%len(frames)
