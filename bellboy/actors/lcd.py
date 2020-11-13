import time
from threading import Thread

import gpiozero
from gpiozero import LiquidCrystal
from gpiozero.pins.mock import MockFactory
from actors.generic import GenericActor
from collections import deque
from utils.messages import Response, LCDMsg, LCDReq, LCDResp
from bellboy.actors.generic import GenericActor


# from bellboy.utils.messages import


class LiquidCrystalActor(GenericActor):
    pass
