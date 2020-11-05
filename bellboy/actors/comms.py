from actors.generic import GenericActor
from utils.messages import CommsReq, CommsResp, Response


class CommsActor(GenericActor):
    """Class to communicate with the heroku-deployed Services."""

    _authenticated = False
    _identifier = None

    # --------------------------#
    # STATE MODIFYING METHODS   #
    # --------------------------#

    def authenticate(self):
        if self._authenticated is False and self._identifier is None:
            self.log.info("Authenticating with Services.")
        else:
            self.log.info("Already authenticated.")

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
