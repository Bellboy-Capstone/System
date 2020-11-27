from actors.comms import CommsActor
from actors.elevator import buttonHovered
from actors.generic import GenericActor
from actors.realtime import RealtimeCommsActor
from actors.ultrasonic import UltrasonicActor
from thespian.actors import ActorAddress
from utils.messages import (
    CommsReq,
    CommsResp,
    Request,
    Response,
    SensorMsg,
    SensorReq,
    SensorResp,
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
        self.comms_actor = self.createActor(CommsActor, globalName="comms")
        self.realtime_actor = self.createActor(
            RealtimeCommsActor, globalName="realtime"
        )

        # request to setup sensor
        """
        self.send(
            self.ultrasonic_sensor,
            SensorMsg(SensorReq.SETUP, trigPin=23, echoPin=24, maxDepth_cm=200),
        )
        """
        # request to setup communications
        self.send(self.comms_actor, CommsReq.AUTHENTICATE)
        self.send(self.realtime_actor, Request.START)

        self.status = Response.STARTED
        self.send(self.realtime_actor, "Let's GOOOOOO!")
        self.send(self.realtime_actor, "Let's GOOOOOO!")
        self.send(self.realtime_actor, "Let's GOOOOOO!")
        self.send(self.realtime_actor, "Let's GOOOOOO!")

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

    def receiveMsg_SensorResp(self, message, sender):
        self.log.info(
            str.format("Received message {} from {}", message, self.nameOf(sender))
        )

        # if bellboy is complete, we can ignore any response msgs.

        if message == SensorResp.SET:
            if sender == self.ultrasonic_sensor:
                # sensor is setup and ready to go, lets start polling for a hovered button.
                self.send(
                    sender,
                    SensorMsg(
                        SensorReq.POLL, pollPeriod_ms=100, triggerFunc=buttonHovered
                    ),
                )

    def receiveMsg_CommsResp(self, message, sender):
        self.log.info(
            str.format("Received message {} from {}", message, self.nameOf(sender))
        )

        if message == CommsResp.SUCCESS:
            self.log.info("Hooray! Comms work.")

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

    def summary(self):
        """Returns a summary of the actor."""
        return self.status
        # TODO flesh this out...

    def teardown(self):
        pass
