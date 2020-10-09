import logging
from abc import ABC, abstractmethod

from thespian.actors import ActorAddress, ActorTypeDispatcher

from src.utils.address_book import AddressBook
from src.utils.constants import ActorNames, Requests


class GenericActor(ActorTypeDispatcher, ABC):
    """Provides a Generic Actor to simplify the process of setting up logs and
    parsing input."""

    # Setting up log when loaded in main omits all log setup,
    # So a helper function/class must be created to load and start
    # all the actors, including the main actor.
    log = None
    parent: ActorAddress = None
    actor: ActorNames = None

    # For looping parts
    loop_period_seconds: float = 10
    loop_enabled: bool = False

    # For contacting other actors
    address_book = None

    def __init__(self, *args, **kwargs):
        if not self.actor or self.actor not in ActorNames:
            raise Exception("Please provide an actor:ActorNames value for this actor!")

        # We can init a new log as long as children of this class provide 'name', but
        # it's very hard to get these children to use the original thread's logging params.
        if not self.log:
            self.log = logging.getLogger(self.actor.name)

        # Init the ActorTypeDispatcher
        super(ActorTypeDispatcher, self).__init__(*args, **kwargs)
        self.log.info(f"Initialized actor '{self.actor.name}'.")

    def receiveMsg_str(self, message: str, sender: ActorAddress):
        """Parses incoming messages containing strings."""
        self.log.debug("Received str %s from sender %s", message, sender)

    def receiveMsg_int(self, message: int, sender: ActorAddress):
        """Parses incoming messages containing integers."""
        self.log.debug("Received int %s from sender %s", message, sender)

    def receiveMsg_dict(self, message: dict, sender: ActorAddress):
        """
        Parses incoming messages containing dictionaries.

        Make sure you SUPER this method if you are overriding it.
        """
        self.log.debug("Received dict %s from sender %s", message, sender)

        # If the dictionary has actor-name keys, assume it is an address book.
        if list(message.keys())[0] in ActorNames:
            self.address_book = message

    def receiveMsg_AddressBook(self, message: AddressBook, sender: ActorAddress):
        """
        DO NOT OVERRIDE;

        Parses incoming messages containing dictionaries.
        """
        # Currently this fails, the arriving object is empty. Needs some work.
        self.log.debug("Received address book from sender %s", message, sender)
        self.log.debug("Received Book has keys: %s", message.all().keys())
        self.address_book = message

    def receiveMsg_WakeupMessage(self, message: dict, sender: ActorAddress):
        """
        DO NOT OVERRIDE;

        Continuously runs the code in the looping method.
        """
        if self.loop_enabled:
            self.wakeupAfter(self.loop_period_seconds)
        self.log.debug("Received %s from sender %s", message, sender)
        self.loop()

    def receiveMsg_Requests(self, message: Requests, sender: ActorAddress):
        """
        DO NOT OVERRIDE;

        Parses incoming messages containing Request enumerations.
        """
        self.log.debug("Received enum %s from sender %s", message.name, sender)

        if message is Requests.START:
            # When the start message is sent to an actor, record the sender as the parent.
            self.parent = sender
            self.send(sender, Requests.STARTING)
            self.start(message, sender)
        elif message is Requests.STOP:
            self.send(sender, Requests.STOPPING)
            self.set_loop_enabled(False)
            self.stop(message, sender)
        elif message is Requests.ARE_YOU_ALIVE:
            self.send(sender, Requests.YES)
        elif message in Requests:
            self.log.debug("No known action for this message.")
        else:
            msg = "Unrecognized Request Enum value sent."
            self.log.error(msg)
            raise Exception(msg)

    def set_loop_period_seconds(self, seconds: float):
        """Sets the period between loop wakeups."""
        self.loop_period_seconds = seconds

    def set_loop_enabled(self, enabled: bool):
        """Allows the parent class to enable or disable the associated looping
        code."""
        self.loop_enabled = enabled
        if enabled is True:
            self.wakeupAfter(self.loop_period_seconds)
            self.loop()  # First run of the looping code is immediate

    @abstractmethod
    def start(self, message: Requests, sender: ActorAddress):
        """The START method contains all setup code for the actor."""
        pass

    @abstractmethod
    def stop(self, message: Requests, sender: ActorAddress):
        """The STOP method contains all teardown code for the actor."""
        pass

    @abstractmethod
    def loop(self):
        """The LOOP method contains all looping code for the actor."""
        pass
