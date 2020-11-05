from thespian.actors import ActorSystem

from bellboy.actors.elevator import buttonHovered
from bellboy.actors.ultrasonic import UltrasonicActor
from utils.messages import (
    Init,
    Response,
    SensorMsg,
    SensorReq,
    SensorResp,
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
    setup_req = SensorMsg(
        type=SensorReq.SETUP,
        trigPin=test_trigPin,
        echoPin=test_echoPin,
        maxDepth_cm=test_maxDepth,
    )

    # ensure the sensor is ready to poll.
    status = test_system.ask(ultrasonic_actor, setup_req)
    assert status == SensorResp.SET

    # ensure it was set to our values.
    summary = test_system.ask(ultrasonic_actor, SummaryReq())
    assert (
        isinstance(summary, SensorMsg)
        and summary.trigPin == test_trigPin
        and summary.echoPin == test_echoPin
        and summary.maxDepth_cm == test_maxDepth
    )

    # test clear sensor
    test_system.tell(ultrasonic_actor, SensorReq.CLEAR)
    status = test_system.ask(ultrasonic_actor, StatusReq())
    assert status == Response.READY


def check_ultrasonicActor_poll(ultrasonic_actor):
    poll_req = SensorMsg(
        type=SensorReq.POLL, triggerFunc=buttonHovered, pollPeriod_ms=100.0
    )
    setup_req = SensorMsg(
        type=SensorReq.SETUP, trigPin=10, echoPin=11, maxDepth_cm=100.0
    )

    # try polling before setup
    response = test_system.ask(ultrasonic_actor, poll_req)
    assert response == Response.FAIL

    # setup then poll, ensure now the sensor is polling
    status = test_system.ask(ultrasonic_actor, setup_req)
    assert status == SensorResp.SET

    status = test_system.ask(ultrasonic_actor, poll_req)
    assert status == SensorResp.POLLING

    # try to clear the sensor as its polling.
    response = test_system.ask(ultrasonic_actor, SensorReq.CLEAR)
    assert response == Response.FAIL

    status = test_system.ask(ultrasonic_actor, StatusReq())
    assert status == SensorResp.POLLING

    # stop polling
    status = test_system.tell(ultrasonic_actor, SensorReq.STOP)
    status = test_system.ask(ultrasonic_actor, StatusReq())
    assert status == SensorResp.SET

    status = test_system.tell(ultrasonic_actor, SensorReq.CLEAR)
    status = test_system.ask(ultrasonic_actor, StatusReq())
    assert status == Response.READY


# main test
def test_ultrasonicActor():

    # create actor, ensure its ready to recieve messages
    ultrasonic_actor = test_system.createActor(
        UltrasonicActor, globalName="test_ultrasonic"
    )
    ultrasonic_status = test_system.ask(
        ultrasonic_actor, Init(senderName="test_system")
    )
    assert ultrasonic_status == Response.READY
    test_system.tell(ultrasonic_actor, TestMode())

    # test behaviours
    check_ultrasonicActor_setup(ultrasonic_actor)
    check_ultrasonicActor_poll(ultrasonic_actor)
