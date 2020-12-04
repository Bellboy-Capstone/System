import json
import os
import pickle
import ssl
from datetime import timedelta
from time import sleep

import requests
import websocket
from actors.generic import GenericActor
from utils.messages import CommsReq, CommsResp, PostableMsg, Response


endpoint = "https://bellboy-services.herokuapp.com"
credential_path = "bellboy-credentials.obj"
url = "websocket-bellboy.herokuapp.com"
HTTP_SUCCESS = 200


class WebCommsActor(GenericActor):
    """
    Class to communicate with all of Bellboy's web services.
    """

    _authenticated = False
    _identifier = None

    _websocket = None
    _retries = 0
    _started = False

    def authenticate(self):
        # Ensure services are up / Wakeup endpoint
        req = requests.get(f"{endpoint}/api/heartbeat/")
        if req.status_code == HTTP_SUCCESS:
            self.log.info("Services are up.")
            self.log.debug(f"Heartbeat endpoint returned {req.json()}")
        else:
            self.log.error("Services are not up.")
            raise Exception("Services are down?")

        # Get credentials
        file_content = None
        with open(credential_path, "rb") as auth_file:
            self.log.info("Found credential file, unpickling...")
            file_content = str(pickle.load(auth_file))
            self._identifier = file_content

        if not file_content:
            # If no creds present, we need to fetch credentials from Services.
            self.log.info("No saved credentials. Registering device with Services...")
            auth_req = requests.get(f"{endpoint}/bellboy/register-device/")
            if req.status_code != HTTP_SUCCESS:
                raise Exception("Could not authenticate!")

            # grab and save our new identifier
            data = auth_req.json()
            self._identifier = str(data.get("identifier"))
            with open(credential_path, "w+") as auth_file:
                self.log.debug("Saving new ID %s", self._identifier)
                pickle.dump(self._identifier, auth_file)

        if not self._identifier:
            raise Exception("Empty ID")

        self._authenticated = True
        self.log.info("Authenticated, ID is %s", self._identifier)

    def _setup_websocket(self):

        # Confirm that Heroku is up.
        req = requests.get(f"https://{url}/")
        if req.status_code != HTTP_SUCCESS:
            raise Exception("Endpoint is not up.")

        self.log.info("Starting WebSocket connection to %s", f"ws://{url}")
        self._websocket = websocket.create_connection(
            f"wss://{url}",
            sslopt={"cert_reqs": ssl.CERT_NONE},
            options={"enable_multithread": False},
        )
        sleep(1)

        # Call out until registered.
        self.log.info("Authenticating with the WebSocket service...")
        response = ""
        while not response.startswith("REGISTERED"):
            response = ""
            self._websocket.send("BELLBOY")
            self.log.info("Getting data from Realtime Services...")
            response = self._websocket.recv()
            self.log.info("Got data from Realtime Services: %s", response)
            sleep(1)

        self.log.info("Realtime Services are ready to go!")
        self._started = True
        self.wakeupAfter(timedelta(seconds=5))

    def post_message_to_backend(self, data):
        """Formats data and sends a dictionary to the status updates endpoint."""

        self.log.debug("POSTing message to backend.")

        # format the data into a dict
        data_to_post = None
        if isinstance(data, str):
            data_to_post = {"message": data}

        elif isinstance(data, PostableMsg):
            data_to_post = data.toDict()

        elif not isinstance(data, dict):
            self.log.warning("Unhandled type of data to POST")
            return

        # Make the POST request:
        response = requests.post(
            f"{endpoint}/bellboy/status-updates/",
            {"bellboy": self._identifier, "body": json.dumps(data_to_post)},
        )

        self.log.debug(
            "Response %s: %s %s", response.status_code, response, response.content
        )

    def _logmsg(self, message: str):
        """Sends a log message to the realtime services."""
        self.log.debug("Sending log message %s", message)

        self._retries = 0
        while self._retries < 10:
            try:
                logmsg = f"BB{self._identifier}: {message}"
                self._websocket.send(logmsg)
                self.log.debug("Successfully sent message to realtime services.")
                return
            except Exception:  # TODO specify exception
                self._retries = self._retries + 1
                self.log.error(
                    "Socket crashed! Reconnecting, attempt %s", self._retries + 1
                )

                # If pipe is broken, rebuild the socket
                self._websocket = None
                self._setup_websocket()

        self.log.error("Socket is closing a lot, gave up!")
        self._websocket = None

    # message handling
    def receiveMsg_PostableMsg(self, message, sender):
        self.log.info("Received message %s from %s", message, self.nameOf(sender))

        if not self._authenticated:
            self.log.error("Please authenticate before attempting to use this actor.")

        self.post_message_to_backend(message)

    def receiveMsg_CommsReq(self, message, sender):
        """responding to simple requests"""
        self.log.info("Received message %s from %s", message, self.nameOf(sender))

        # ignore unauthorized requests
        if sender != self.parent:
            self.log.warning("Received %s req from unauthorized sender!", message.name)
            self.send(sender, Response.UNAUTHORIZED)
            return

        if message == CommsReq.SETUP:
            if self._authenticated:
                self.log.warning("Already authenticated!")
            else:
                self.authenticate()

            if self._websocket:
                self.log.warning("Websocket already created!")
            else:
                self._setup_websocket()

    def receiveMsg_WakeupMessage(self, message, sender):
        if self._websocket:
            self.log.debug("Staying awake, sending heartbeat message.")
            self._logmsg("Heartbeat.")
            self.wakeupAfter(timedelta(seconds=5))
        else:
            self.log.debug("No websocket, putting realtime logs to bed")

    def receiveMsg_RealtimeLog(self, msg, sender):
        if self._websocket is None:
            self.log.error("Setup websocket before attempting to send logs.")
            return

        self.log.debug("Sending string %s to realtime logging service.", msg.text)
        self._logmsg(msg.text)

    # overrides
    def summary(self):
        pass

    def teardown(self):
        self._logmsg("Goodbye!")
        if self._websocket:
            self.log.debug("Closing WebSocket connection to %s", url)
            self._websocket.close()

        self.log.info("Closed WebSocket.")
