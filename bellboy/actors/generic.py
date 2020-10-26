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
        self.status = Response.NOT_READY
        self.TEST_MODE = False

    def createActor(
        self, actorClass, targetActorRequirements=None, globalName=None, sourceHash=None
    ):
        """
        Wrapper/Overrider for the thespian createActor, so all bellboy actors can be spawned with our conventions.
        """
        actor = super().createActor(
            actorClass, targetActorRequirements, globalName, sourceHash
        )

        # all initialization msgs unique to bellboy actors get sent now
        self.send(actor, Init())

        # if this actor is in test mode, all its children should be as well.
        if self.TEST_MODE:
            self.send(actor, TestMode())
        return actor

    def receiveMsg_Init(self, message, sender):
        """
        Initializes a bellboy actor for bellboy activities. i.e. setting up log. etc
        """
        self.parent = sender

        if self.globalName is None:
            log.warning("unnamed actor created!")
            self.log = log.getChild("UNNAMED")
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


# pls read if ur gonna write an actor that extends this class:
#
# 1. If d actor isnt created by a bellboy actor, u must send the Init msg to it explicitly in order to use bellboy logs.
#     (This should only matter for the lead actor and during testing,
#     cus all actors are sposed to be created thru bellboy lead anyways.)
#     Reason is bc the actors are running in independent processes, they dont share globals, i.e. the logger.
#     Everything is communicated thru messaging.
#
# 2. Organization tip:
#       Divide the class into:
#           a) state modifying methods (private) and
#           b) message handling methods (public).
#       Send any response messages in the message handling methods only.
#       It will be nice and make testing much easier!
