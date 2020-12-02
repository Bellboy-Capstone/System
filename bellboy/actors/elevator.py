"""
class for the elevator and button related stuff.

in actors for now.. could move
"""

import logging

from collections import deque
from utils.messages import SensorEvent, SensorEventMsg


log = logging.getLogger("elevator")
# simple "buttons", only have a position (depth) value and a radius.. all in cm
BTN1_POS = 8.5
BTN2_POS = 16
BTN_RAD = 3

DATA_TO_COUNT = 10  # 10 * 100 ms = 1 sec of data


def buttonHovered(depth_deque: deque):
    """
    rough implementation of a buttonHovered method.

    processes data deque. tells us which button was hovered.
    """

    log.debug(str.format("data: {}", format_deque(depth_deque)))

    # for now only test in quantums
    if len(depth_deque) % DATA_TO_COUNT != 0:
        return

    btn_chosen = "button1"
    count = 0
    while count < DATA_TO_COUNT:
        depth = depth_deque[count]
        count += 1
        if depth < BTN1_POS - BTN_RAD or depth > BTN1_POS + BTN_RAD:
            # btn1 wasnt chosen
            btn_chosen = "button2"
            break

    if btn_chosen == "button1":
        log.debug(str.format("data: {}", format_deque(depth_deque)))
        return SensorEventMsg(
            eventType=SensorEvent.BUTTON_HOVERED, eventData="button1 was hovered"
        )

    count = 0
    while count < DATA_TO_COUNT:
        depth = depth_deque[count]
        count += 1
        if depth < BTN2_POS - BTN_RAD or depth > BTN2_POS + BTN_RAD:
            # btn2 wasnt chosen
            btn_chosen = None
            break

    if btn_chosen == "button2":
        log.debug(str.format("data: {}", format_deque(depth_deque)))
        return SensorEventMsg(
            eventType=SensorEvent.BUTTON_HOVERED, eventData="button2 was hovered"
        )

    return None


def format_deque(d):
    # format to two decimal places.
    return ["%.2f" % elem for elem in d]
