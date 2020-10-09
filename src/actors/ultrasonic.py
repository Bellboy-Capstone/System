import logging

from thespian.actors import ActorAddress

from src.actors.generic import GenericActor
from src.utils.constants import ActorNames, Requests


class UltrasonicActor(GenericActor):
    actor = ActorNames.ULTRASONIC
    log = logging.getLogger(ActorNames.ULTRASONIC.name)

    def start(self, message: Requests, sender: ActorAddress):
        self.log.debug("Starting the UltraSonic detection loop...")
        self.set_loop_period_seconds(1)
        self.set_loop_enabled(True)

    def stop(self, message: Requests, sender: ActorAddress):
        self.log.debug("Stopping the UltraSonic detection loop...")

    def loop(self):
        self.log.debug("UltraSonic sensor read!")
