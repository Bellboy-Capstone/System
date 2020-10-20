from abc import ABC, abstractmethod

from actors import log
from thespian.actors import ActorAddress, ActorTypeDispatcher
from utils.messages import Init, Response, StatusReq, SummaryReq


class GenericActor(ActorTypeDispatcher, ABC):
    """Generic Actor to unify logging and some message handling. Other than the lead actor (created by thesystem), all bellboy actors should be created from another bellboy actor."""

    def __init__(self, *args, **kwargs):
        "creates an empty actor, to be fleshed out by further messages."
        super().__init__()

        # private attributes
        self.parent = None
        self.name = None
        self.log = None
        self.status = Response.NOT_READY
        self.TEST_MODE = False

    # overidden to createbellboy actors that use our logging convention.
    def createActor(self, actorClass,
                    targetActorRequirements=None,
                    globalName=None,
                    sourceHash=None):
        actor = super().createActor(actorClass,
                                    targetActorRequirements,
                                    globalName,
                                    sourceHash)
        self.send(actor, Init())
        return actor

    def receiveMsg_Init(self, message, sender):
        self.log = log.getChild(self.globalName)
        self.parent = sender
        self.log.info(str.format("{} created by {}", self.globalName, sender))
        self.status = Response.READY
        self.send(sender, self.status)

    def receiveMsg_TestMode(self, message, sender):
        self.TEST_MODE = True
        self.log.info("Set to TEST mode")

    def receiveMsg_StatusReq(self, message, sender):
        self.send(sender, self.status)

    def receiveMsg_WakeupMessage(self, message: dict, sender: ActorAddress):
        """
        On wakeup request
        """
        self.send(sender, Response.AWAKE)

    @abstractmethod
    def receiveMsg_SummaryReq(self, message, sender): 
        """sends a summary of thec actor."""
        pass
