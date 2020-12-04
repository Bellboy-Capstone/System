import logging

from actors.lead import BellboyLeadActor
from thespian.actors import ActorSystem
from utils.cli import get_bellboy_configs
from utils.messages import Init, Request, StatusReq


def main():
    """Starts the Bellboy system by  creating an ActorSystem, creating the
    LeadActor, and asking it to START."""

    configs = get_bellboy_configs()

    # Initialize the Actor system
    system = ActorSystem(systemBase="multiprocQueueBase", logDefs=configs["logcfg"])

    # for logging here in main
    log = logging.getLogger("Main")
    log.info("Starting the Bellboy system")

    # lead actor
    bellboy = system.createActor(BellboyLeadActor, globalName="bellboy_lead")
    status = system.ask(bellboy, Init())
    try:
        # tell bellboy to start his work
        system.tell(bellboy, Request.START)

        # Run this while loop for the duration of the program.
        while (
            input("Enter 'q' to end Bellboy, any other key to send heartbeat.\n") != "q"
        ):
            log.debug("Sending status request to lead actor.")
            system.ask(bellboy, StatusReq())

    except KeyboardInterrupt:
        log.error("The bellboy system was interrupted by the keyboard, exiting...")
    finally:
        log.info("Shutting down system...")
        system.shutdown()


if __name__ == "__main__":
    main()
