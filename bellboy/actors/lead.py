from actors.elevator import buttonHovered
from actors.generic import GenericActor
from actors.ultrasonic import UltrasonicActor
from actors.microphone import MicrophoneActor

from thespian.actors import ActorAddress
from utils.messages import (
    Request,
    Response,
    SensorMsg,
    SensorReq,
    SensorResp,
    MicReq,
    MicMsg,
    MicResp,
)


class BellboyLeadActor(GenericActor):
    def __init__(self):
        """define Bellboy's private variables."""
        super().__init__()
        self.ultrasonic_sensor = None
        self.event_count = 0

    def startBellboyLead(self):
        """
        Starts bellboy lead actor services.

        Spawns and sets up child actors
        """
        self.log.info("Starting bellboy services.")

        # spawn actors
        self.log.info("Starting all dependent actors...")
        self.ultrasonic_sensor = self.createActor(
            UltrasonicActor, globalName="ultrasonic"
        )
        self.microphone = self.createActor(MicrophoneActor, globalName="microphone")

        # setup actors
        # ultrasonic
        self.send(
            self.ultrasonic_sensor,
            SensorMsg(SensorReq.SETUP, trigPin=23, echoPin=24, maxDepth_cm=200),
        )

        self.send(self.microphone, MicMsg(MicReq.SETUP))

        self.status = Response.STARTED

    def stopBellboyLead(self):
        self.log.info("Stopping all child actors...")
        self.status = Response.DONE
        self.send(self.ultrasonic_sensor, SensorReq.STOP)
        self.send(self.ultrasonic_sensor, SensorReq.CLEAR)

    # --------------------------#
    # MESSAGE HANDLING METHODS  #
    # --------------------------#
    def receiveMsg_Request(self, message: Request, sender: ActorAddress):
        """handles messages of type Request enum."""
        self.log.debug(
            "Received enum %s from sender %s", message.name, self.nameOf(sender)
        )

        if message is Request.START:
            self.startBellboyLead()

        elif message is Request.STOP:
            self.stopBellboyLead()

        self.send(sender, self.status)

    # handling sensor msgs
    def receiveMsg_SensorResp(self, message, sender):
        self.log.info(
            str.format("Received message {} from {}", message, self.nameOf(sender))
        )

        if message == SensorResp.SET:
            # sensor is setup and ready to go, lets start polling for a hovered button.
            self.send(
                sender,
                SensorMsg(
                    SensorReq.POLL,
                    pollPeriod_ms=100,
                    triggerFunc=buttonHovered,
                ),
            )

    def receiveMsg_SensorEventMsg(self, message, sender):
        self.event_count += 1
        self.log.info(
            str.format("Received message {} from {}", message, self.nameOf(sender))
        )
        self.log.info(
            str.format(
                "#{}: {} event from {} - {}",
                self.event_count,
                message.eventType,
                sender,
                message.eventData,
            )
        )

        if self.event_count == 3:
            self.log.debug("received 3 events, turning off sensor.")
            self.send(self.ultrasonic_sensor, SensorReq.STOP)

    # handling mic msgs
    def receiveMsg_MicResp(self, message, sender):
        self.log.info(
            str.format("Received message {} from {}", message, self.nameOf(sender))
        )

        if message == MicResp.SET:
            self.send(sender, MicReq.START_LISTENING)

    def receiveMsg_MicEventMsg(self, message, sender):
        self.log.info(
            str.format("Received message {} from {}", message, self.nameOf(sender))
        )
        self.log.info(
            str.format(
                "{} event from {} - {}",
                message.eventType,
                self.nameOf(sender),
                message.phraseHeard,
            )
        )

    def summary(self):
        """Returns a summary of the actor."""
        return self.status
        # TODO flesh this out...

    def teardown(self):
        pass
