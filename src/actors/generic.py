import logging
from abc import ABC, abstractmethod

from thespian.actors import ActorAddress, ActorTypeDispatcher

from src.utils.constants import Requests


class GenericActor(ActorTypeDispatcher, ABC):
    """Provides a Generic Actor to simplify the process of setting up logs and
    parsing input."""

    # Setting up log when loaded in main omits all log setup,
    # So a helper function/class must be created to load and start
    # all the actors, including the main actor.
    log = None
    parent = None
    name = None

    def __init__(self, *args, **kwargs):
        if not self.name:
            raise Exception("Please provide a 'name' class variable for this actor!")

        # We can init a new log as long as children of this class provide 'name', but
        # it's very hard to get these children to use the original thread's logging params.
        if not self.log:
            self.log = logging.getLogger(self.name)

        # Init the ActorTypeDispatcher
        super(ActorTypeDispatcher, self).__init__(*args, **kwargs)
        self.log.info(f"Initialized actor '{self.name}'.")

    def receiveMsg_str(self, message: str, sender: ActorAddress):
        """Parses incoming messages containing strings."""
        self.log.debug("Received str %s from sender %s", message, sender)

    def receiveMsg_int(self, message: int, sender: ActorAddress):
        """Parses incoming messages containing integers."""
        self.log.debug("Received int %s from sender %s", message, sender)

    def receiveMsg_dict(self, message: dict, sender: ActorAddress):
        """Parses incoming messages containing dictionaries."""
        self.log.debug("Received dict %s from sender %s", message, sender)

    def receiveMsg_Requests(self, message: Requests, sender: ActorAddress):
        """Parses incoming messages containing Request enumerations."""
        self.log.debug("Received enum %s from sender %s", message.name, sender)

        if message is Requests.START:
            # When the start message is sent to an actor, record the sender as the parent.
            self.parent = sender
            self.send(sender, Requests.STARTING)
            self.start(message, sender)
        elif message is Requests.STOP:
            self.send(sender, Requests.STOPPING)
            self.stop(message, sender)
        elif message is Requests.ARE_YOU_ALIVE:
            self.send(sender, Requests.YES)
        else:
            msg = "Unrecognized Request Enum value sent."
            self.log.error(msg)
            raise Exception(msg)

    @abstractmethod
    def start(self, message: Requests, sender: ActorAddress):
        self.log.info("Performing START action.")

    @abstractmethod
    def stop(self, message: Requests, sender: ActorAddress):
        self.log.debug("Performing STOP action.")
