import logging

from thespian.actors import ActorTypeDispatcher

from src.utils.constants import Requests


class LeadActor(ActorTypeDispatcher):

    log = logging.getLogger("LeadActor")

    def receiveMsg_str(self, message, sender):
        """Parses incoming messages containing strings."""
        self.log.debug("Received str %s from sender %s", message, sender)

    def receiveMsg_int(self, message, sender):
        """Parses incoming messages containing integers."""
        self.log.debug("Received int %s from sender %s", message, sender)

    def receiveMsg_dict(self, message, sender):
        """Parses incoming messages containing dictionaries."""
        self.log.debug("Received dict %s from sender %s", message, sender)

    def receiveMsg_Requests(self, message, sender):
        """Parses incoming messages containing Request enumerations."""
        self.log.debug("Received enum %s from sender %s", message, sender)

        if message is Requests.START:
            self.log.debug("Performing START action.")
            self.send(sender, Requests.STARTING)
        elif message is Requests.STOP:
            self.log.debug("Performing STOP action.")
            self.send(sender, Requests.STOPPING)
        else:
            raise Exception("Unrecognized Request Enum value sent.")
