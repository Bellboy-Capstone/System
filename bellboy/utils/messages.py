from enum import Enum

""" Global messages, non-actor specifc """


# init
class Init():
    def __init__(self, testMode=False):
        self.testing = testMode

# for checking status
class StatusReq:
    pass

# for getting a summary
class SummaryReq:
    pass

# to run actors in testmode
class TestMode:
    pass

# general requests
class Request(Enum):
    START, STOP, STATUS, CLEAR = range(4)


# general responses
# responses are a direct and simple reply to a request.
class Response(Enum):
    READY, NOT_READY, SUCCESS, FAIL, DONE, ALIVE, UNAUTHORIZED = range(7)


""" Sensor related messages. """


# sensor requests
class SensorReq(Enum):
    SETUP, CLOSE, POLL, STOP = range(4)

# for requests with more info
class SensorReqMsg:
    def __init__(
        self,
        reqType: SensorReq,
        trigPin=0,
        echoPin=0,
        maxDepth_cm=0.0,
        pulseWidth_us=0.0,
        triggerFunc=None,
        pollPeriod_ms=0.0,
    ):
        self.type = reqType
        self.trigPin = trigPin
        self.echoPin = echoPin
        self.maxDepth_cm = maxDepth_cm
        self.pulseWidth_us = pulseWidth_us
        self.sensorEventFunc = triggerFunc
        self.pollPeriod_ms = pollPeriod_ms
    
    def __str__(self):
        return self.type.name

# sensor responses
class SensorResp(Enum):
    READY, POLLING, UNSET, SUMMARY = range(4)

# for responses with more info
class SensorRespMsg:
    def __init__(
        self,
        reqType: SensorResp,
        trigPin=0,
        echoPin=0,
        maxDepth_cm=0.0,
        pulseWidth_us=0.0,
        triggerFunc=None,
        pollPeriod_ms=0.0,
    ):
        self.type = reqType
        self.trigPin = trigPin
        self.echoPin = echoPin
        self.maxDepth_cm = maxDepth_cm
        self.pulseWidth_us = pulseWidth_us
        self.sensorEventFunc = triggerFunc
        self.pollPeriod_ms = pollPeriod_ms
    
    def __str__(self):
        return self.type.name


# sensor events
class SensorEvent(Enum):
    BUTTON_HOVERED = 1


# for event with more info
class SensorEventMsg:
    def __init__(self, eventType, eventData):
        self.eventType = eventType
        self.eventData = eventData

    def __str__(self):
        return self.eventType.name
