import logging
from time import sleep

from actors.lead import BellboyLeadActor
from thespian.actors import ActorSystem
from utils.cli import get_bellboy_configs
from utils.messages import Init, Request, Response


def main():
    """Starts the Bellboy system by  creating an ActorSystem, creating the
    LeadActor, and asking it to START."""

    logcfgs = get_bellboy_configs()

    # for logging in main
    log = logging.getLogger("Main")
    log.info("Starting the Bellboy system")

    # Initialize the Actor system
    system = ActorSystem(systemBase="multiprocQueueBase", logDefs=logcfgs)
    bellboy = system.createActor(BellboyLeadActor, globalName="bellboy_lead")
    status = system.ask(bellboy, Init())

    if status != Response.READY:
        log.error("ruh roh")

    try:
        # tell bellboy to start his work
        system.tell(bellboy, Request.START)

        # Run this while loop for the duration of the program.
        while True:
            sleep(10)
            log.debug("Sending Heartbeat request to lead actor.")
            system.tell(bellboy, Request.STATUS)

    except KeyboardInterrupt:
        log.error("The bellboy system was interrupted by the keyboard, exiting...")
    finally:
        system.shutdown()


if __name__ == "__main__":
    main()
