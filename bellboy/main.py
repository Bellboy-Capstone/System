import logging

from actors.lead import BellboyLeadActor
from thespian.actors import ActorSystem
from utils.cli import get_bellboy_configs
from utils.messages import Init, Request, StatusReq, ServoReq


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
    system.tell(bellboy, Init())
    try:
        # tell bellboy to start his work
        system.tell(bellboy, Request.START)

        # Run this while loop for the duration of the program.
        while True:
            choice = input("Enter 'q' to end Bellboy, 's' to send heartbeat, and 'p' to push button.\n")
            if choice == "p":
                system.ask(bellboy, ServoReq.PUSHBUTTON)
            if choice == "q":
                break
            if choice == "s":
                log.debug("Sending status request to lead actor.")
                system.ask(bellboy, StatusReq())


    except KeyboardInterrupt:
        log.error("The bellboy system was interrupted by the keyboard, exiting...")
    finally:
        log.info("Shutting down system...")
        system.shutdown()


if __name__ == "__main__":
    main()
