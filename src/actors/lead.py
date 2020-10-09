import logging

from thespian.actors import ActorTypeDispatcher

from src.utils.constants import Requests


class LeadActor(ActorTypeDispatcher):
    """The lead actor orchestrates all other Bellboy services."""

    # Setting up log when loaded in main omits all log setup,
    # So a helper function/class must be created to load and start
    # all the actors, including the main actor.
    log = logging.getLogger("LeadActor")

    def receiveMsg_str(self, message, sender):
        """Parses incoming messages containing strings."""
        self.log.info("Received str %s from sender %s", message, sender)

    def receiveMsg_int(self, message, sender):
        """Parses incoming messages containing integers."""
        self.log.info("Received int %s from sender %s", message, sender)

    def receiveMsg_dict(self, message, sender):
        """Parses incoming messages containing dictionaries."""
        self.log.info("Received dict %s from sender %s", message, sender)

    def receiveMsg_Requests(self, message, sender):
        """Parses incoming messages containing Request enumerations."""
        self.log.info("Received enum %s from sender %s", message, sender)

        if message is Requests.START:
            self.log.info("Performing START action.")
            self.send(sender, Requests.STARTING)
        elif message is Requests.STOP:
            self.log.debug("Performing STOP action.")
            self.send(sender, Requests.STOPPING)
        elif message is Requests.ARE_YOU_ALIVE:
            self.log.info("Yep, I am alive. Status of child actors:")
        else:
            raise Exception("Unrecognized Request Enum value sent.")
