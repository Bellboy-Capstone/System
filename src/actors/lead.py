import logging

from thespian.actors import ActorAddress

from src.actors.generic import GenericActor
from src.utils.constants import Requests


class LeadActor(GenericActor):
    name = "Lead Actor"
    log = logging.getLogger("Lead Actor")

    def start(self, message: Requests, sender: ActorAddress):
        self.log.info("Starting all child actors...")

    def stop(self, message: Requests, sender: ActorAddress):
        self.log.info("Stopping all child actors...")
