import logging
from time import sleep

from thespian.actors import ActorSystem

from actors.lead import BellboyLeadActor
from utils.cli import configure_bellboy
from utils.messages import Init, Request, Response


def main():
    """Starts the Bellboy system by  creating an ActorSystem, creating the
    LeadActor, and asking it to START."""

    configure_bellboy()

    log = logging.getLogger("Bellboy")
    log.info("Starting the Bellboy system")

    # Initialize the Actor system
    system = ActorSystem(systemBase="multiprocQueueBase")
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
        system.tell(bellboy, Request.STOP)
        system.shutdown()
        return 0


if __name__ == "__main__":
    main()
