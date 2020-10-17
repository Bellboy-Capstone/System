import logging
import os
from time import sleep

from thespian.actors import ActorAddress, ActorSystem

from actors.lead import BellboyLeadActor
from utils.cli import configure_bellboy
from utils.messages import Request, Response


def main():
    """
    Starts the Bellboy system by  creating an ActorSystem, creating the LeadActor, and asking it to START.
    """

    configure_bellboy()

    log = logging.getLogger("Bellboy")
    log.info("Starting the Bellboy system")

    # Initialize the Actor system
    system = ActorSystem(systemBase="multiprocQueueBase")
    bellboy = system.createActor(BellboyLeadActor, globalName="bellboy_lead")

    try:
        # Ask bellboy to start his work
        system.ask(bellboy, Request.START)

    except KeyboardInterrupt:
        log.error("The bellboy system was interrupted by the keyboard, exiting...")
    finally:
        system.tell(bellboy, Request.STOP)


if __name__ == "__main__":
    main()
