import logging
import os
from abc import ABC, abstractmethod

from thespian.actors import ActorAddress, ActorTypeDispatcher
from utils.messages import DetailedMsg, Init, Response, StatusReq, SummaryReq, TestMode


class GenericActor(ActorTypeDispatcher, ABC):
    """Generic Actor to unify logging and some message handling."""

    def __init__(self, *args, **kwargs):
        """Creates an empty actor, to be fleshed out by further messages."""
        super().__init__()

        # private attributes
        self.parent = None
        self.log = None
        self._address_book = {}
        self.status = Response.NOT_READY
        self.TEST_MODE = False
        self.children = []

    def nameOf(self, address: ActorAddress):
        """
        Returns name of actor if it's entry exists in address book.

        Else returns the toString of the actorAddress.
        """

        return self._address_book.get(str(address), str(address))

    def _nameAddress(self, address: ActorAddress, name: str):
        """Adds entry to my address book."""
        if name is not None:
            # using the str of the address as key bc the address itself is unhashable type
            self._address_book[str(address)] = name

    def createActor(
        self, actorClass, targetActorRequirements=None, globalName=None, sourceHash=None
    ):
        """Wrapper/Overrider for the thespian createActor, so all bellboy
        actors can be spawned with our conventions."""
        actor = super().createActor(
            actorClass, targetActorRequirements, globalName, sourceHash
        )

        # update this actor's address book with new child
        self._nameAddress(actor, globalName)
        self.children.append(actor)

        # all initialization msgs unique to bellboy actors get sent now
        self.send(actor, Init(senderName=self.globalName))

        # if this actor is in test mode, all its children should be as well.
        if self.TEST_MODE:
            self.send(actor, TestMode())

        return actor

    def receiveMsg_Init(self, message, sender):
        """
        Initializes a bellboy actor for bellboy activities.

        i.e. setting up log. etc
        """

        # set parent and add them to our address book
        self.parent = sender
        self._nameAddress(sender, message.senderName)

        if self.globalName is None:
            self.globalName = str(self.myAddress)

        self.log = logging.getLogger(self.globalName)
        self.log.info(
            str.format(
                "{} created by {}, pid={}",
                self.globalName,
                self.nameOf(sender),
                os.getpid(),
            )
        )

        self.status = Response.READY
        self.send(sender, self.status)

    def receiveMsg_TestMode(self, message, sender):
        """Puts the actor in test mode."""
        self.TEST_MODE = True
        self.log.info("Set to TEST mode")

    def receiveMsg_StatusReq(self, message: StatusReq, sender):
        """Sends a status update to sender."""
        self.send(sender, self.status)

    def receiveMsg_SummaryReq(self, message: SummaryReq, sender):
        """Sends a summary of the actor to the sender."""
        self.send(sender, self.summary())

    def receiveMsg_ActorExitRequest(self, msg, sender):
        """This is last msg processed before the Actor is shutdown."""
        self.log.debug("Received ActorExitRequest message!")
        self.teardown()

    @abstractmethod
    def teardown(self):
        """
        Actor's teardown sequence, called before shutdown.

        (i.e. close threads, disconnect from services, etc)
        """
        pass

    @abstractmethod
    def summary(self) -> DetailedMsg:
        """
        Returns a summary of the actor.

        The summary can be an object of any type described in the messages module.

        :rtype: object
        """
        pass
