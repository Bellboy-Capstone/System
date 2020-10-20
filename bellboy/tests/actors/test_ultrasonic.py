import sys, os
from thespian.actors import ActorSystem

from actors.elevator import buttonHovered
from actors.lead import BellboyLeadActor, GenericActor
from actors.ultrasonic import UltrasonicActor
from utils.messages import (
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


def test_ultrasonicActor_setup(
    ultrasonic_actor: UltrasonicActor, parent_actor: GenericActor
):
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

    parent_actor.send(ultrasonic_actor, setup_req)

    # ensure the sensor is ready to poll.
    status = test_system.ask(ultrasonic_actor, StatusReq)
    assert status == SensorResp.READY

    # ensure it was set to our values.
    summary = test_system.ask(ultrasonic_actor, SummaryReq)
    assert (
        isinstance(summary, SensorRespMsg)
        and summary.trigPin == test_trigPin
        and summary.echoPin == test_echoPin
        and summary.maxDepth_cm == test_maxDepth
    )

    # ensure we get unauthorized if other actor attempts to setup sensor.
    setup_req = SensorReqMsg(reqType=SensorReq.SETUP, trigPin=0, echoPin=0)
    response = test_system.ask(ultrasonic_actor, setup_req)
    assert response == Response.UNAUTHORIZED

    # ensure values stayed the same
    summary = test_system.ask(ultrasonic_actor, SummaryReq)
    assert (
        isinstance(summary, SensorRespMsg)
        and summary.trigPin == test_trigPin
        and summary.echoPin == test_echoPin
    )

    # testing unauthorized clear sensor
    response = test_system.ask(ultrasonic_actor, SensorReq.CLEAR)
    assert response == Response.UNAUTHORIZED
    status = test_system.ask(ultrasonic_actor, StatusReq)
    assert status == SensorResp.READY

    # testing authorized clear sensor
    parent_actor.send(ultrasonic_actor, SensorReq.CLEAR)
    status = test_system.ask(ultrasonic_actor, StatusReq)
    assert status == Response.READY


def test_ultrasonicActor_poll(ultrasonic_actor, parent_actor):
    poll_req = SensorReqMsg(
        reqType=SensorReq.POLL, triggerFunc=buttonHovered, pollPeriod_ms=100.0
    )
    setup_req = SensorReqMsg(reqType=SensorReq.SETUP, trigPin=0, echoPin=0)

    # try polling before setup
    response = test_system.ask(ultrasonic_actor, poll_req)
    assert response == Response.FAIL

    # setup then poll, ensure now the sensor is polling
    parent_actor.send(ultrasonic_actor, setup_req)
    parent_actor.send(ultrasonic_actor, poll_req)
    status = test_system.ask(ultrasonic_actor, StatusReq)
    assert status == SensorResp.POLLING

    # try to clear the sensor as its polling.
    response = test_system.ask(ultrasonic_actor, SensorReq.CLEAR)
    assert response == Response.FAIL
    status = test_system.ask(ultrasonic_actor, StatusReq)
    assert status == SensorResp.POLLING

    # stop polling
    parent_actor.send(ultrasonic_actor, SensorReq.STOP)
    status = test_system.ask(ultrasonic_actor, StatusReq)
    assert status == SensorResp.READY

    parent_actor.send(ultrasonic_actor, SensorReq.CLEAR)
    status = test_system.ask(ultrasonic_actor, StatusReq)
    assert status == Response.READY


def test_ultrasonicActor():

    # create actor, ensure its ready to recieve messages
    lead = test_system.createActor(BellboyLeadActor, "bellboy_lead_test_ultrasonic")
    ultrasonic = lead.createActor(UltrasonicActor, "test_ultrasonic")
    ultrasonic_status = test_system.ask(ultrasonic, StatusReq)
    assert ultrasonic_status == Response.READY

    # put it in test mode. cus we dont want to actually use the rpi pins.
    lead.send(ultrasonic, TestMode())

    # test behaviours
    test_ultrasonicActor_setup(ultrasonic, lead)
    test_ultrasonicActor_poll(ultrasonic, lead)
