# gif to oled

# 1 extract frames

from PIL import Image, ImageSequence


gif_path = "audio_animation_128x32.gif"
gif_name = gif_path.split('.')[0]

gif = Image.open(gif_path)
frames = []
for frame in ImageSequence.Iterator(gif):
    frames.append(frame)


# get the colour info 

# convert to hex format

# save?