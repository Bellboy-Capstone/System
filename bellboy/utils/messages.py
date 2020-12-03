from enum import Enum


""" Global messages, non-actor specifc """


# init
class Init:
    def __init__(self, senderName=None):
        self.senderName = senderName


# for checking status
class StatusReq:
    pass


# for getting a summary
class SummaryReq:
    pass


# to run actors in testmode
class TestMode:
    pass


# generic parent class for detailed messages


class DetailedMsg:
    pass


# general requests
class Request(Enum):
    START, STOP, CLEAR = range(3)


# general responses
# responses are usually a direct and simple reply to a request.
# they also are used to indicate an actors status.
class Response(Enum):
    (
        READY,
        NOT_READY,
        SUCCESS,
        FAIL,
        DONE,
        ALIVE,
        UNAUTHORIZED,
        STARTED,
        SUMMARY,
    ) = range(9)


""" Sensor related messages. """


# sensor requests
class SensorReq(Enum):
    SETUP, POLL, STOP, CLEAR = range(4)


# sensor responses
class SensorResp(Enum):
    SET, POLLING = range(2)


# for req/resp with more info
class SensorMsg(DetailedMsg):
    def __init__(
        self,
        type,
        trigPin=0,
        echoPin=0,
        maxDepth_cm=0.0,
        triggerFunc=None,
        pollPeriod_ms=0.0,
    ):
        self.type = type
        self.trigPin = trigPin
        self.echoPin = echoPin
        self.maxDepth_cm = maxDepth_cm
        self.sensorEventFunc = triggerFunc
        self.pollPeriod_ms = pollPeriod_ms

    def __str__(self):
        return self.type.name


# sensor events
class SensorEvent(Enum):
    BUTTON_HOVERED = 1


# for event with more info
class SensorEventMsg(DetailedMsg):
    def __init__(self, eventType, eventData):
        self.eventType = eventType
        self.eventData = eventData

    def __str__(self):
        return self.eventType.name


"""Cam messages"""


class CamReq(Enum):
    SETUP, GET_CAM_LIST, START_STREAM, STOP_STREAM = range(4)


class CamResp(Enum):
    SET, STREAMING, CAM_LIST = range(3)


class CamMsg:
    def __init__(self, msgType, cameraNumber=None):
        self.msgType = msgType
        self.cameraNumber = cameraNumber

    def __str__(self):
        return self.msgType.name


class CamEvent(Enum):
    FLOOR_CHOSEN, FACE_DETECED = range(2)

class CameraType(Enum):
    RPI_CAM, USB_CAM = range(2)


class CamEventMsg:
    def __init__(self, eventType: CamEvent, face = None, faceId = 0):
        self.eventType = eventType
        self.face = face
        self.faceId = faceId

    def __str__(self):
        return self.eventType.name


"""Lcd messages"""


class LcdReq(Enum):
    SETUP, DISPLAY, CLEAR = range(3)


class LcdResp(Enum):
    SET, DISPLAYING = range(2)


class LcdMsg(DetailedMsg):
    def __init__(
        self,
        msgType,
        defaultText=None,
        displayText=None,
        displayDuration=0.0,
        overFlow=None,
    ):
        self.msgType = msgType
        self.defaultText = defaultText
        self.displayText = displayText
        self.displayDuration = displayDuration

    def __str__(self):
        return self.msgType.name
