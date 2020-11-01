from abc import ABC, abstractmethod

from actors import log
from thespian.actors import ActorAddress, ActorTypeDispatcher
from utils.messages import Init, Response, StatusReq, SummaryReq, TestMode


class GenericActor(ActorTypeDispatcher, ABC):
    """Generic Actor to unify logging and some message handling."""

    def __init__(self, *args, **kwargs):
        "Creates an empty actor, to be fleshed out by further messages."
        super().__init__()

        # private attributes
        self.parent = None
        self.log = None
        self._address_book = {}
        self.status = Response.NOT_READY
        self.TEST_MODE = False

    def nameOf(self, address: ActorAddress):
        """
        Returns name of actor if it's entry exists in address book.
        Else returns the toString of the actorAddress.
        """

        return self._address_book.get(str(address), str(address))

    def _nameAddress(self, address: ActorAddress, name: str):
        """
        Adds entry to my address book.
        """
        if name is not None:
            # using the str of the address as key bc the address itself is unhashable type
            self._address_book[str(address)] = name

    def createActor(
        self, actorClass, targetActorRequirements=None, globalName=None, sourceHash=None
    ):
        """
        Wrapper/Overrider for the thespian createActor, so all bellboy actors can be spawned with our conventions.
        """
        actor = super().createActor(
            actorClass, targetActorRequirements, globalName, sourceHash
        )

        # update this actor's address book with new child
        self._nameAddress(actor, globalName)

        # all initialization msgs unique to bellboy actors get sent now
        self.send(actor, Init(senderName=self.globalName))

        # if this actor is in test mode, all its children should be as well.
        if self.TEST_MODE:
            self.send(actor, TestMode())

        return actor

    def receiveMsg_Init(self, message, sender):
        """
        Initializes a bellboy actor for bellboy activities. i.e. setting up log. etc
        """

        # set parent and add them to our address book
        self.parent = sender
        self._nameAddress(sender, message.senderName)

        if self.globalName is None:
            log.warning("unnamed actor created!")
            self.log = log.getChild(str(self.myAddress))
        else:
            self.log = log.getChild(self.globalName)
            self.log.info(str.format("{} created by {}", self.globalName, sender))

        self.status = Response.READY
        self.send(sender, self.status)

    def receiveMsg_TestMode(self, message, sender):
        """
        Puts the actor in test mode.
        """
        self.TEST_MODE = True
        self.log.info("Set to TEST mode")

    def receiveMsg_StatusReq(self, message: StatusReq, sender):
        """
        Sends a status update to sender.
        """
        self.send(sender, self.status)

    def receiveMsg_WakeupMessage(self, message: dict, sender: ActorAddress):
        """
        On wakeup request
        """
        self.send(sender, Response.AWAKE)

    @abstractmethod
    def receiveMsg_SummaryReq(self, message: SummaryReq, sender):
        """sends a summary of the actor to the sender. to be defined in child classes."""
        pass


# NOTE:
# If d actor isnt created by a bellboy actor, u must send an Init msg to it explicitly in order to use bellboy logs.
# This should only matter for the lead actor and during testing,
# cus all actors are sposed to be created thru bellboy lead anyways.
# Reason is bc the actors are running in independent processes, they dont share globals, i.e. the logger.
# Everything is communicated thru messaging.
# tldr the init msg holds the addressbook and log configs together