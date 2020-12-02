from actors.comms import CommsActor
from actors.elevator import buttonHovered
from actors.generic import GenericActor
from actors.lcd import LcdActor
from actors.realtime import RealtimeCommsActor
from actors.ultrasonic import UltrasonicActor
from thespian.actors import ActorAddress
from utils.messages import (
    CommsReq,
    LcdMsg,
    LcdReq,
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
        self.lcd = None
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
        self.lcd = self.createActor(LcdActor, globalName="lcd")

        # requests to setup actors
        self.send(self.comms_actor, CommsReq.AUTHENTICATE)
        self.send(self.realtime_actor, Request.START)

        # setup actors, handle their responses
        sensor_setup_msg = SensorMsg(
            SensorReq.SETUP, trigPin=23, echoPin=24, maxDepth_cm=200
        )
        lcd_setup_msg = LcdMsg(LcdReq.SETUP, defaultText="Welcome to Bellboy")

        self.send(self.ultrasonic_sensor, sensor_setup_msg)
        self.send(self.lcd, lcd_setup_msg)

        self.status = Response.STARTED
        self.send(self.realtime_actor, "Ready to serve clients.")
        self.send(self.comms_actor, {"event": "power", "state": "on"})

        message = LcdMsg(
            LcdReq.DISPLAY,
            displayText="Hello this is a message, which floor would you like to go to?  ",
            displayDuration=3,
        )
        self.send(self.lcd, message)

    def stopBellboyLead(self):
        self.log.info("Stopping all child actors...")
        self.send(self.realtime_actor, "Stopping.")
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

    def receiveMsg_SensorEventMsg(self, message, sender):
        self.log.info(
            str.format(
                "#{}: {} event from {} - {}",
                self.event_count,
                message.eventType,
                sender,
                message.eventData,
            )
        )

        # Form a message based on the SensorEventMsg
        sensor_message_str = f"Requested Floor #{str(message.eventData)[6]}"

        # Show the message on the LCD
        lcd_message = LcdMsg(
            LcdReq.DISPLAY,
            displayText=sensor_message_str,
            displayDuration=3,
        )
        self.send(self.lcd, lcd_message)

        # Send the message to Realtime WebLogs
        self.send(self.realtime_actor, sensor_message_str)

        self.send(
            self.comms_actor,
            {
                "event": "detection",
                "method": "hand",
                "floor": str(message.eventData)[6],
            },
        )

    def summary(self):
        """Returns a summary of the actor."""
        return self.status
        # TODO flesh this out...

    def teardown(self):
        pass
