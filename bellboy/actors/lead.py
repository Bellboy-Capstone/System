from thespian.actors import ActorAddress

from actors.elevator import buttonHovered
from actors.generic import GenericActor
from actors.ultrasonic import UltrasonicActor
from utils.messages import Request, Response, SensorMsg, SensorReq, SensorResp


class BellboyLeadActor(GenericActor):
    def __init__(self):
        """define Bellboy's private variables."""
        super().__init__()
        self.ultrasonic_sensor = None
        self.event_count = 0

    def startBellboyLead(self):
        """
        Starts bellboy lead actor services.

        Configures global RPI Board. Spawns and sets up child actors
        (ultrasonic sensor).
        """
        self.log.info("Starting bellboy services.")

        # spawn actors
        self.log.info("Starting all dependent actors...")
        self.ultrasonic_sensor = self.createActor(
            UltrasonicActor, globalName="ultrasonic"
        )

        # request to setup sensor
        self.send(
            self.ultrasonic_sensor,
            SensorMsg(
                SensorReq.SETUP,
                trigPin=23,
                echoPin=24,
                maxDepth_cm=200,
            ),
        )
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

        elif message is Request.STATUS:
            self.log.debug(str.format("Status check - {}", Response.ALIVE.name))

        else:
            msg = "Unhandled Request Enum value sent."
            self.log.error(msg)
            raise Exception(msg)

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

    def summary(self):
        """Returns a summary of the actor."""
        return self.status
        # TODO flesh this out...
