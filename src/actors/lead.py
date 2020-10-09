import logging

from thespian.actors import ActorAddress

from src.actors.generic import GenericActor
from src.utils.constants import ActorNames, Requests


class LeadActor(GenericActor):
    actor = ActorNames.LEAD
    log = logging.getLogger(ActorNames.LEAD.name)

    def start(self, message: Requests, sender: ActorAddress):
        self.set_loop_period_seconds(3)
        self.set_loop_enabled(True)

    def stop(self, message: Requests, sender: ActorAddress):
        self.log.info("Stopping all child actors...")

    def loop(self):
        pass
