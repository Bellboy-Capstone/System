from abc import ABC, abstractmethod

from thespian.actors import ActorAddress, ActorTypeDispatcher

from utils.messages import Request, Response, Init

from actors import log

class GenericActor(ActorTypeDispatcher, ABC):
    """Generic Actor to unify logging and some message handling."""

    def __init__(self, *args, **kwargs):
        "creates an empty actor, to be fleshed out by further messages."
        super().__init__()

        # private attributes
        self.parent = None
        self.name = None
        self.log = None

    def receiveMsg_Init(self, message, sender):
        self.log = log.getChild(self.globalName)
        self.parent = sender
        self.log.info(str.format("{} created by {}", self.globalName, sender))

    def receiveMsg_str(self, message: str, sender: ActorAddress):
        self.log.debug("Received str %s from sender %s", message, sender)

    def receiveMsg_int(self, message: int, sender: ActorAddress):
        self.log.debug("Received int %s from sender %s", message, sender)

    def receiveMsg_dict(self, message: dict, sender: ActorAddress):
        self.log.debug("Received dict %s from sender %s", message, sender)

    def receiveMsg_WakeupMessage(self, message: dict, sender: ActorAddress):
        """
        On wakeup request
        """
        self.send(sender, Response.AWAKE)

    def receiveMsg_Request(self, message: Request, sender: ActorAddress):
        """
        handles messages of type Request enum.
        """
        self.log.debug("Received enum %s from sender %s", message.name, sender)

        if message is Request.START:
            self.start()

        elif message is Request.STOP:
            self.stop()

        else:
            msg = "Unhandled Request Enum value sent."
            self.log.error(msg)
            raise Exception(msg)

    @abstractmethod
    def start(self):
        """The START method contains all setup code for the actor."""
        pass

    @abstractmethod
    def stop(self):
        """The STOP method contains all teardown code for the actor."""
        pass

    
    # to createbellboy actors that use our logging convention.

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

