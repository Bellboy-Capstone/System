# from actors.comms import CommsActor
from actors.comms import WebCommsActor
from actors.elevator import buttonHovered
from actors.facecam import FacecamActor
from actors.generic import GenericActor
from actors.lcd import LcdActor
from actors.ultrasonic import UltrasonicActor
from thespian.actors import ActorAddress, ActorExitRequest
from utils.messages import (
    CamReq,
    BellboyMsg,
    CommsReq,
    LcdMsg,
    LcdReq,
    PostableMsg,
    RealtimeLog,
    Request,
    Response,
    SensorMsg,
    SensorReq,
)


class BellboyLeadActor(GenericActor):
    def __init__(self):
        """define Bellboy's private variables."""
        super().__init__()
        self.event_count = 0

    def start(self):
        """
        Starts bellboy lead actor services.

        Spawns and sets up child actors
        """
        self.log.info("Starting bellboy services.")
        self.spawnActors()
        self.status = Response.STARTED

        # bellboy is ready, start running things n whatnot
        # self.post_to_backend(BellboyMsg(event="power", state="on"))
        # self.log_realtime("Ready to serve clients.")
        # self.display("Hello this is a message, which floor would you like to go to?")
        # self.poll_sensor()
        self.stream_camera()

    def spawnActors(self):
        """Create and set-up all child actors."""
        # creates and sets up actors actors
        self.log.info("Spawning all dependent actors...")

        # # comms
        # self.comms_actor = self.createActor(WebCommsActor, globalName="comms")
        # self.send(self.comms_actor, CommsReq.SETUP)

        # # sensor
        # self.ultrasonic = self.createActor(UltrasonicActor, globalName="ultrasonic")
        # sensor_setup_msg = SensorMsg(
        #     SensorReq.SETUP, trigPin=23, echoPin=24, maxDepth_cm=200
        # )
        # self.send(self.ultrasonic, sensor_setup_msg)

        # # display
        # self.lcd = self.createActor(LcdActor, globalName="lcd")
        # lcd_setup_msg = LcdMsg(LcdReq.SETUP, defaultText="Welcome to Bellboy")
        # self.send(self.lcd, lcd_setup_msg)

        # camera
        self.facecam = self.createActor(FacecamActor, globalName="facecam")
        self.send(self.facecam, CamReq.SETUP)

    # utility methods
    def display(self, text, duration=3):
        """ Send msg to our display to show text for duration of time."""
        message = LcdMsg(
            LcdReq.DISPLAY,
            displayText=text,
            displayDuration=duration,
        )
        self.send(self.lcd, message)

    def post_to_backend(self, data: PostableMsg):
        self.send(self.comms_actor, data)

    def log_realtime(self, text):
        self.send(self.comms_actor, RealtimeLog(text))

    def poll_sensor(self):
        self.send(
            self.ultrasonic,
            SensorMsg(SensorReq.POLL, pollPeriod_ms=100, triggerFunc=buttonHovered),
        )
    
    def stream_camera(self):
        self.send(self.facecam, CamReq.START_STREAM)

    # --------------------------#
    # MESSAGE HANDLING METHODS  #
    # --------------------------#

    def receiveMsg_Request(self, message: Request, sender: ActorAddress):
        """handles messages of type Request enum."""
        self.log.debug(
            "Received enum %s from sender %s", message.name, self.nameOf(sender)
        )

        if message is Request.START:
            self.start()

        elif message is Request.STOP:
            self.teardown()

        self.send(sender, self.status)

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

        # Display, log realtime and post to backend
        self.display(sensor_message_str)
        self.log_realtime(sensor_message_str)
        self.post_to_backend(message)

    def summary(self):
        """Returns a summary of the actor."""
        return self.status
        # TODO flesh this out...

    def teardown(self):
        self.log.info("Stopping all child actors...")
        while self.children:
            self.send(self.children.pop(), ActorExitRequest())

        self.status = Response.DONE
