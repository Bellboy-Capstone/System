import logging

import RPi.GPIO as GPIO
from thespian.actors import ActorAddress

from bellboy.actors.generic import GenericActor
from bellboy.actors.ultrasonic import UltrasonicActor
from bellboy.utils.messages import *

# simple "buttons", only have a position (depth) value and a radius.. all in cm
BTN1_POS = 15
BTN2_POS = 30
BTN_RAD = 2

class BellboyLeadActor(GenericActor):
    def __init__(self):
        """define Bellboy's private variables."""
        self.ultrasonic_sensor = None

    def start(self):
        """
        Starts bellboy lead actor services. Configures global RPI Board.
        Spawns and sets up child actors (ultrasonic sensor).
        """     

        self.log.info("Starting bellboy services.")

        # configure RPI GPIO board
        GPIO.setmode(GPIO.BOARD)  # use PHYSICAL GPIO Numbering
        self.log.debug("GPIO mode set to BOARD")

        # spawn actors
        self.log.info("Starting all dependent actors...")
        self.ultrasonic_sensor = self.createActor(UltrasonicActor, globalName="ultrasonic")

        # request to setup sensor
        self.send(
            self.ultrasonic_sensor,
            SensorReqMsg(
                SensorReq.SETUP,
                trigPin=16,
                echoPin=18,
                maxDepth_cm=200,
                pulseWidth_us=10,
            ),
        )

    def stop(self, message: Requests, sender: ActorAddress):
        self.log.info("Stopping all child actors...")

    def receiveMsg_SensorResp(self, message, sender):
        self.log.info(str.format("Received message {} from {}", message, sender))

        if message == SensorResp.READY:
            if sender == self.ultrasonic_sensor:
                # sensor is setup and ready to go, lets start polling for a hovered button.
                self.send(
                    sender,
                    SensorReqMsg(
                        SensorReq.POLL,
                        pollPeriod_ms=100,
                        triggerFunc=buttonHovered,
                    ),
                )


    def receiveMsg_SensorEventMsg(self, message, sender):
        self.log.info(str.format("Received message {} from {}", message, sender))
        self.log.info(
            str.format(
                "#{}: {} event from {} - {}",
                self.event_count,
                message.eventType,
                sender,
                message.eventData,
            )
        )


def buttonHovered(depth_array):
    "rough implementation of a buttonHovered method. tells us which button was hovered given array of depth values"

    btn_chosen = "button1"
    for depth in depth_array[-10:]:
        if depth < BTN1_POS - BTN_RAD or depth > BTN1_POS + BTN_RAD:
            # btn1 wasnt chosen
            btn_chosen = "button2"
            break
    
    if btn_chosen == "button1":
        return SensorEventMsg(eventType=SensorEvent.BUTTON_HOVERED, eventData="button1 was hovered")

    for depth in depth_array[-10:]:
        if depth < BTN1_POS - BTN_RAD or depth > BTN1_POS + BTN_RAD:
            # btn2 wasnt chosen
            btn_chosen = None
            break
    
    if btn_chosen == "button2":
        return SensorEventMsg(eventType=SensorEvent.BUTTON_HOVERED, eventData="button2 was hovered")
    
    return None