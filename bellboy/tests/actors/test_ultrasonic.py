from actors.elevator import buttonHovered
from actors.ultrasonic import UltrasonicActor
from thespian.actors import ActorSystem
from utils.messages import (
    Init,
    Response,
    SensorReq,
    SensorReqMsg,
    SensorResp,
    SensorRespMsg,
    StatusReq,
    SummaryReq,
    TestMode,
)


test_system = ActorSystem(systemBase="multiprocQueueBase")


def check_ultrasonicActor_setup(ultrasonic_actor):
    # ensure the ultrasonic sensor only accepts setup reqs from its parent
    test_trigPin = 10
    test_echoPin = 11
    test_maxDepth = 50.0
    setup_req = SensorReqMsg(
        reqType=SensorReq.SETUP,
        trigPin=test_trigPin,
        echoPin=test_echoPin,
        maxDepth_cm=test_maxDepth,
        pulseWidth_us=10.0,
    )

    # ensure the sensor is ready to poll.
    status = test_system.ask(ultrasonic_actor, setup_req)
    assert status == SensorResp.READY

    # ensure it was set to our values.
    summary = test_system.ask(ultrasonic_actor, SummaryReq())
    assert (
        isinstance(summary, SensorRespMsg)
        and summary.trigPin == test_trigPin
        and summary.echoPin == test_echoPin
        and summary.maxDepth_cm == test_maxDepth
    )

    # testing authorized clear sensor
    status = test_system.ask(ultrasonic_actor, SensorReq.CLEAR)
    assert status == Response.READY


def check_ultrasonicActor_poll(ultrasonic_actor):
    poll_req = SensorReqMsg(
        reqType=SensorReq.POLL, triggerFunc=buttonHovered, pollPeriod_ms=100.0
    )
    setup_req = SensorReqMsg(reqType=SensorReq.SETUP, trigPin=0, echoPin=0)

    # try polling before setup
    response = test_system.ask(ultrasonic_actor, poll_req)
    assert response == Response.FAIL

    # setup then poll, ensure now the sensor is polling
    status = test_system.ask(ultrasonic_actor, setup_req)
    assert status == SensorResp.READY

    status = test_system.ask(ultrasonic_actor, poll_req)
    assert status == SensorResp.POLLING

    # try to clear the sensor as its polling.
    response = test_system.ask(ultrasonic_actor, SensorReq.CLEAR)
    assert response == Response.FAIL

    status = test_system.ask(ultrasonic_actor, StatusReq())
    assert status == SensorResp.POLLING

    # stop polling
    status = test_system.ask(ultrasonic_actor, SensorReq.STOP)
    assert status == SensorResp.READY

    status = test_system.ask(ultrasonic_actor, SensorReq.CLEAR)
    assert status == Response.READY


# main test
def test_ultrasonicActor():

    # create actor, ensure its ready to recieve messages
    ultrasonic_actor = test_system.createActor(
        UltrasonicActor, globalName="test_ultrasonic"
    )
    ultrasonic_status = test_system.ask(ultrasonic_actor, Init())
    assert ultrasonic_status == Response.READY
    test_system.tell(ultrasonic_actor, TestMode())

    # test behaviours
    check_ultrasonicActor_setup(ultrasonic_actor)
    check_ultrasonicActor_poll(ultrasonic_actor)
