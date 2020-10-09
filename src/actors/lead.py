import logging

from thespian.actors import ActorAddress

from src.actors.generic import GenericActor
from src.utils.constants import ActorNames, Requests


class LeadActor(GenericActor):
    actor = ActorNames.LEAD
    log = logging.getLogger(ActorNames.LEAD.name)

    def start(self, message: Requests, sender: ActorAddress):
        self.log.debug("Address Book has keys: %s", self.address_book.all().keys())
        # self.send(self.address_book.get(ActorNames.LIQUID_CRYSTAL), Requests.START)
        # self.send(self.address_book.get(ActorNames.ULTRASONIC), Requests.START)

    def stop(self, message: Requests, sender: ActorAddress):
        self.log.info("Stopping all child actors...")
        self.send(self.address_book.get(ActorNames.LIQUID_CRYSTAL), Requests.STOP)
        self.send(self.address_book.get(ActorNames.ULTRASONIC), Requests.STOP)

    def loop(self):
        pass
