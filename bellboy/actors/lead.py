import RPi.GPIO as GPIO
from actors.elevator import buttonHovered
from actors.generic import GenericActor
from actors.ultrasonic import UltrasonicActor
from thespian.actors import ActorAddress
from utils.messages import *


class BellboyLeadActor(GenericActor):
    def __init__(self):
        """define Bellboy's private variables."""
        super().__init__()
        self.ultrasonic_sensor = None
        self.event_count = 0

    def startBellboyLead(self):
        """
        Starts bellboy lead actor services. Configures global RPI Board.
        Spawns and sets up child actors (ultrasonic sensor).
        """
        self.log.info("Starting bellboy services.")

        # configure RPI GPIO board
        GPIO.setmode(GPIO.BOARD)  # use PHYSICAL GPIO Numbering
        self.log.debug("GPIO mode set to BOARD")
        self.log.info(
            str.format("mode: {}", GPIO.getmode())
        )  # use PHYSICAL GPIO Numbering

        # spawn actors
        self.log.info("Starting all dependent actors...")
        self.ultrasonic_sensor = self.createActor(
            UltrasonicActor, globalName="ultrasonic"
        )

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
        self.status = Response.STARTED

    def stopBellboyLead(self):
        self.log.info("Stopping all child actors...")
        self.send(self.ultrasonic_sensor, SensorReq.STOP)
        self.status = Response.DONE

    # --------------------------#
    # MESSAGE HANDLING METHODS  #
    # --------------------------#
    def receiveMsg_Request(self, message: Request, sender: ActorAddress):
        """
        handles messages of type Request enum.
        """
        self.log.debug("Received enum %s from sender %s", message.name, sender)

        if message is Request.START:
            self.startBellboyLead()

        elif message is Request.STOP:
            self.stopBellboyLead()

        elif message is Request.STATUS:
            self.log.debug(str.format("Status check - {}", Response.ALIVE.name))

        else:
            msg = "Unhandled Request Enum value sent."
            self.log.error(msg)
            raise Exception(msg)

        self.send(sender, self.status)

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
        self.event_count += 1
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

        if self.event_count == 10:
            self.log.debug("received 10 events, turning off sensor.")
            self.send(self.ultrasonic_sensor, SensorReq.STOP)

    def receiveMsg_SummaryReq(self, message, sender):
        """sends a summary of the actor."""
        # TODO flesh this out...
        self.send(sender, self.status)
