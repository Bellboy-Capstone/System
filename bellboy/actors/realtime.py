from time import sleep

import requests
import websocket
from actors.generic import GenericActor
from utils.messages import CommsReq, CommsResp, Request, Response


url = "bellboy-realtime.herokuapp.com"


class RealtimeCommsActor(GenericActor):
    """Class to communicate with the heroku-deployed Services."""

    _identifier = None
    _websocket = None
    _started = False
    _thread = None

    def on_message(self):
        self.log.info("on_message")

    def on_error(self):
        self.log.info("on_error")

    def on_close(self):
        self.log.info("on_close")
        print("on_close")

    def on_open(self):
        self.log.info("on_open")

    def __init__(self):
        """Start WebSocket Client."""
        super().__init__()

    # --------------------------#
    # STATE MODIFYING METHODS   #
    # --------------------------#

    def _setup_websocket(self):
        req = requests.get(f"https://{url}")
        if req.status_code != 200:
            raise Exception("Enpoint is not up.")

        self.log.info("Starting WebSocket connection to %s", f"wss://{url}")
        self._websocket = websocket.create_connection(f"wss://{url}")
        sleep(1)
        self.log.info("Saying hello")
        self._websocket.send("Hello!!!")

    def authenticate(self):
        pass

    # --------------------------#
    # MESSAGE HANDLING METHODS  #
    # --------------------------#

    def receiveMsg_RealtimeCommsReq(self, message, sender):
        """responding to simple sensor requests."""

        self.log.info(
            str.format("Received message {} from {}", message, self.nameOf(sender))
        )

        # ignore unauthorized requests
        if sender != self.parent:
            self.log.warning(
                str.format("Received {} req from unauthorized sender!", message)
            )
            self.send(sender, Response.UNAUTHORIZED)

        elif message == CommsReq.AUTHENTICATE:
            self.authenticate()

    def receiveMsg_Request(self, message, sender):
        if message == Request.START:
            self.log.info("STARTing WebSocket...")
            self._setup_websocket()

    def receiveMsg_SummaryReq(self, message, sender):
        """sends a summary of the actor."""
        self.send(sender, CommsResp.SUCCESS)

    def summary(self):
        self.log.info("Summary of realtime actor requested.")
        pass

    def teardown(self):
        self._websocket.send("Closing.")
        self.log.info("Closing WebSocket connection to %s", url)
        self._websocket.close()
        self.log.info("Closed WebSocket.")
        print("Teardown for realtime comms done.")
