import logging

from thespian.actors import ActorAddress

from src.actors.generic import GenericActor
from src.utils.constants import ActorNames, Requests


class LiquidCrystalActor(GenericActor):
    actor = ActorNames.LIQUID_CRYSTAL
    log = logging.getLogger(ActorNames.LIQUID_CRYSTAL.name)

    def start(self, message: Requests, sender: ActorAddress):
        self.log.debug("Starting the Liquid Crystal display...")

    def stop(self, message: Requests, sender: ActorAddress):
        self.log.debug("Stopping the Liquid Crystal system...")

    def receiveMsg_str(self, message: str, sender: ActorAddress):
        """Parses incoming messages containing integers."""
        self.log.info("Printing to LCD =>  '%s' ", message)

    def loop(self):
        pass
