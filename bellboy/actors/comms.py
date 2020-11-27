import os
import pickle

import requests
from actors.generic import GenericActor
from utils.messages import CommsReq, CommsResp, Response


endpoint = "https://bellboy-services.herokuapp.com"
credential_path = "bellboy-credentials.obj"


class CommsActor(GenericActor):
    """Class to communicate with the heroku-deployed Services."""

    _authenticated = False
    _identifier = None

    # --------------------------#
    # STATE MODIFYING METHODS   #
    # --------------------------#

    def authenticate(self):
        req = requests.get(f"{endpoint}/api/heartbeat/")
        if req.status_code == 200:
            self.log.info("Services are up.")
            self.log.debug(f"Heartbeat endpoint returned {req.json()}")
        else:
            self.log.error("Services are not up.")
            raise Exception("Services are down?")

        if self._authenticated is False or self._identifier is None:
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
                self._authenticated = True
            else:
                # If no file is present, we need to fetch credentials from Services.
                self.log.info(
                    "No saved credentials. Registering device with Services..."
                )
                auth_req = requests.get(f"{endpoint}/bellboy/register-device/")
                data = auth_req.json()
                self.log.debug("Authorization result: %s", data)
                if req.status_code == 200:
                    self.log.debug("New ID is %s", data.get("identifier"))
                else:
                    raise Exception("Could not authenticate!")

                # Save that identifier for use now:
                self._identifier = str(data.get("identifier"))
                self._authenticated = True

                # Now we've got a new identifier, so let's pickle it for storage:
                new_auth_file = open(credential_path, "wb")
                pickle.dump(self._identifier, new_auth_file)
                new_auth_file.close()

        self.log.info("Authenticated, ID is %s", self._identifier)

    # --------------------------#
    # MESSAGE HANDLING METHODS  #
    # --------------------------#

    def receiveMsg_CommsReq(self, message, sender):
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

    def receiveMsg_SummaryReq(self, message, sender):
        """sends a summary of the actor."""
        self.send(sender, CommsResp.SUCCESS)

    def summary(self):
        pass

    def teardown(self):
        pass
