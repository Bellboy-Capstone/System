import logging
from abc import ABC, abstractmethod

from thespian.actors import ActorAddress, ActorTypeDispatcher

from src.utils.constants import Requests


class BellboyActor(ActorTypeDispatcher, ABC):
    """The lead actor orchestrates all other Bellboy services."""

    # Setting up log when loaded in main omits all log setup,
    # So a helper function/class must be created to load and start
    # all the actors, including the main actor.
    log = logging.getLogger(__name__)
    parent = None

    def receiveMsg_str(self, message, sender):
        """Parses incoming messages containing strings."""
        self.log.debug("Received str %s from sender %s", message, sender)

    def receiveMsg_int(self, message, sender):
        """Parses incoming messages containing integers."""
        self.log.debug("Received int %s from sender %s", message, sender)

    def receiveMsg_dict(self, message, sender):
        """Parses incoming messages containing dictionaries."""
        self.log.debug("Received dict %s from sender %s", message, sender)

    def receiveMsg_Requests(self, message, sender: ActorAddress):
        """Parses incoming messages containing Request enumerations."""
        self.log.debug(
            "Received enum %s from sender %s", message, sender.actorAddressString
        )

        if message is Requests.START:
            self.parent = sender
            self.start()
            self.send(sender, Requests.STARTING)
        elif message is Requests.STOP:
            self.stop()
            self.send(sender, Requests.STOPPING)
        elif message is Requests.ARE_YOU_ALIVE:
            self.log.info("Yep, I am alive.")
        else:
            msg = "Unrecognized Request Enum value sent."
            self.log.error(msg)
            raise Exception(msg)

    @abstractmethod
    def start(self):
        self.log.info("Performing START action.")
        pass

    @abstractmethod
    def stop(self):
        self.log.debug("Performing STOP action.")
        pass
