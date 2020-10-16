import logging
import os

from time import sleep

from thespian.actors import ActorAddress, ActorSystem
from bellboy.utils.messages import Request, Response
from bellboy.actors.lead import BellboyLeadActor


def main():
    """
    Starts the Bellboy system by  creating an ActorSystem, creating the LeadActor, and asking it to START.
    """

    log = logging.getLogger("Bellboy")
    log.info("Starting the Bellboy system")

    # Initialize the Actor system
    system = ActorSystem(systemBase="multiprocQueueBase")
    bellboy = system.createActor(BellboyLeadActor, globalName="bellboy_lead")

    try:
        # Ask bellboy to start his work
        response = system.ask(bellboy, Request.START)

        # If the lead actor does not reply that he is starting, something is wrong
        if response != Response.SUCCESS:
            raise Exception("Lead actor did not start correctly.")

    except KeyboardInterrupt:
        log.error("The bellboy system was interrupted by the keyboard, exiting...")
    finally:
        system.tell(bellboy, Request.STOP)
        system.shutdown()


if __name__ == "__main__":
    main()
