import asyncio
import time

import websocket
from actors.generic import GenericActor
from utils.messages import CommsReq, CommsResp, Request, Response


socket_url = "wss://bellboy-realtime.herokuapp.com"


class RealtimeCommsActor(GenericActor):
    """Class to communicate with the heroku-deployed Services."""

    _identifier = None
    _websocket = None

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
        self.log.info("Starting WebSocket connection to %s", socket_url)
        self._websocket = websocket.WebSocketApp(
            socket_url,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
        )
        self._websocket.on_open = self.on_open
        self._websocket.daemon = True
        self._websocket.run_forever()

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
        self.log.info("Closing WebSocket connection to %s", socket_url)
        self._websocket.close()
        self.log.info("Closed WebSocket.")
        print("Teardown for realtime comms done.")
