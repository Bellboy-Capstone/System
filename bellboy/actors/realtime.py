import os
import pickle
import ssl
from datetime import timedelta
from time import sleep

import requests
import websocket
from actors.generic import GenericActor
from utils.messages import CommsReq, Request, Response


url = "websocket-bellboy.herokuapp.com"
credential_path = "bellboy-credentials.obj"


class RealtimeCommsActor(GenericActor):
    """Class to communicate with the heroku-deployed Services."""

    _identifier = None
    _websocket = None
    _retries = 0
    _started = False
    _thread = None
    _identifier = None

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

        # Confirm that Heroku is up.
        req = requests.get(f"https://{url}/")
        if req.status_code != 200:
            raise Exception("Enpoint is not up.")
        else:
            self.log.info("WebSocket endpoint at %s is up.", f"https://{url}")

        #
        self.log.info("Starting WebSocket connection to %s", f"ws://{url}")
        self._websocket = websocket.create_connection(
            f"wss://{url}",
            sslopt={"cert_reqs": ssl.CERT_NONE},
            options={"enable_multithread": False},
        )
        sleep(1)
        self.log.info("Authenticating with the WebSocket service...")

        # Call out until registered.
        response = ""
        while not response.startswith("REGISTERED"):
            response = ""
            self._websocket.send("BELLBOY")
            self.log.info("Getting data from Realtime Services...")
            response = self._websocket.recv()
            self.log.info("Got data from Realtime Services: %s", response)
            sleep(1)

        # Announce successful setup:
        self.log.info("Realtime Services are ready to go!")

        # Get the ID saved by comms actor if the file is present
        if self._identifier is None:
            # Unpickle the auth file if it is present:
            if (
                os.path.exists(credential_path)
                and os.path.isfile(credential_path)
                and os.path.getsize(credential_path) > 0
            ):
                self.log.info("Found credential file, unpickling...")
                auth_file = open(credential_path, "rb")
                self._identifier = str(pickle.load(auth_file))
                auth_file.close()

        if not self._started:
            self._started = True
            self.wakeupAfter(timedelta(seconds=5))

    def _logmsg(self, message):
        """Sends a log message to the realtime services."""
        self.log.debug("Sending log message %s", message)
        try:
            if self._identifier:
                logmsg = f"BB{self._identifier}: {message}"
                self._websocket.send(logmsg)
            else:
                self._websocket.send(message)

            self.log.debug("Successfully sent message to realtime services.")
            self._retries = 0

        # If the pipe is broken, we need to reconnect.
        except Exception:
            self.log.error("Socket crashed! Reconnecting, attempt %s", self._retries)
            self._websocket = None
            self._setup_websocket()
            self._logmsg(message)
            self._retires = self._retries + 1
            if self._retires > 10:
                self.log.error("Socket is closing a lot, restarting actor.")
                self._websocket = None
                raise Exception("Kill me, I've fallen and I can't get up.")

    # --------------------------#
    # MESSAGE HANDLING METHODS  #
    # --------------------------#

    def receiveMsg_WakeupMessage(self, message, sender):
        self.log.debug("Staying awake, sending heartbeat message.")
        self._logmsg("Heartbeat.")
        self.wakeupAfter(timedelta(seconds=5))

    def receiveMsg_str(self, message, sender):
        """Sends a string as a message to NodeJS Services."""
        if self._websocket is None:
            self.log.error("Please authenticate before attempting to use this actor.")
        else:
            self.log.debug("Sending string %s to realtime logging service.", message)
            self._logmsg(message)

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

    def summary(self):
        pass

    def teardown(self):
        self._logmsg("Goodbye!")
        self.log.debug("Closing WebSocket connection to %s", url)
        self._websocket.close()
        self.log.info("Closed WebSocket.")
