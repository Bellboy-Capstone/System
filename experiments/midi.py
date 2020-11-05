from time import sleep

import pygame.midi


# On pi: apt-get install for audio drivers:
# python3-pygame timidity fluid-soundfont-gm

# Timidity server must be running for notes to play:
# timidity -iA

C = 74
MAX = 127
brief = 0.05


def play(note=[C], volume=MAX, length=brief):
    for n in note:
        midi_out.note_on(n, volume)

    sleep(length)

    for n in note:
        midi_out.note_off(n, volume)


pygame.midi.init()
port = pygame.midi.get_default_output_id()
port = 2

print(f"There are {pygame.midi.get_count()} MIDI devices.")

print(f"Playing on port {port}")
print(pygame.midi.get_device_info(port))
midi_out = pygame.midi.Output(port)

print("Playing a note...")


def play_instrument(num, note=74, time=1):
    print(f"Note from instrument {num}")
    midi_out.set_instrument(num)
    midi_out.note_on(note, 127)
    midi_out.note_on(note + 3, 127)
    sleep(time)
    midi_out.note_off(note, 127)
    midi_out.note_off(note + 3, 127)
    sleep(time / 3)


def play_sequence(instrument=52):
    play_instrument(instrument)
    play_instrument(instrument, note=76, time=0.5)
    play_instrument(instrument, note=73, time=3)
    sleep(1)


for chosen in [16, 52, 38, 104, 112]:
    play_sequence(instrument=chosen)

print("Playing audio...")
for instrument in range(100, 128):
    print(f"Using instrument {instrument}")
    midi_out.set_instrument(instrument)
    for note in range(74, 84):
        play(note=[note], length=0.1)
    sleep(1)

print("Done.")

pygame.midi.quit()
