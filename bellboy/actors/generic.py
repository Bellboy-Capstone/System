from abc import ABC, abstractmethod

from actors import log
from thespian.actors import ActorAddress, ActorTypeDispatcher
from utils.messages import Init, Request, Response


class GenericActor(ActorTypeDispatcher, ABC):
    """Generic Actor to unify logging and some message handling."""

    def __init__(self, *args, **kwargs):
        "creates an empty actor, to be fleshed out by further messages."
        super().__init__()

        # private attributes
        self.parent = None
        self.name = None
        self.log = None
    def receiveMsg_WakeupMessage(self, message: dict, sender: ActorAddress):
        """
        On wakeup request
        """
        self.send(sender, Response.AWAKE)
        
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
