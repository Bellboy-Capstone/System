"""class for the elevator and button related stuff. in actors for now.. could move"""

from collections import deque

from actors import log
from utils.messages import SensorEvent, SensorEventMsg


# simple "buttons", only have a position (depth) value and a radius.. all in cm
BTN1_POS = 15
BTN2_POS = 30
BTN_RAD = 2

DATA_TO_COUNT = 10  # 10 * 100 ms = 2 sec of data


def buttonHovered(depth_deque):
    """
    rough implementation of a buttonHovered method. processes data deque.
    tells us which button was hovered.
    """
    
    # free up bloated deque
    while len(depth_deque) > depth_deque.maxlen - DATA_TO_COUNT:
        depth_deque.pop()
   
    # only check data in quantums
    if len(depth_deque) % DATA_TO_COUNT != 0:
        log.debug("not enough data to process: %d", len(depth_deque))
        return None

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
        log.debug(str.format("data: {}", depth_deque))
        return SensorEventMsg(
            eventType=SensorEvent.BUTTON_HOVERED, eventData="button1 was hovered"
        )

    count = 0
    while count < DATA_TO_COUNT:
        depth = depth_deque[count]
        count += 1
        if depth < BTN1_POS - BTN_RAD or depth > BTN1_POS + BTN_RAD:
            # btn2 wasnt chosen
            btn_chosen = None
            break

    if btn_chosen == "button2":
        log.debug(str.format("data: {}", depth_deque))
        return SensorEventMsg(
            eventType=SensorEvent.BUTTON_HOVERED, eventData="button2 was hovered"
        )

    return None
