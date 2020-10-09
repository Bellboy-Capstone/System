import logging
import sys
from time import sleep

from thespian.actors import ActorAddress, ActorSystem

from src.utils.cli import CLI
from src.utils.constants import Requests


def main():
    """
    Starts the Bellboy system by configuring logging, creating an ActorSystem,
    creating the LeadActor, and asking it to START.

    The lead actor loads all other required actors. The system can be
    halted with a keyboard interrupt (CTRL+C)
    """

    log = logging.getLogger("Bellboy")
    log.info("Starting the Bellboy system")

    # Parse arguments and configure logging.
    cli = CLI()
    cli.setup(sys.argv)

    # Import the lead actor. This must be done here to allow the log configuration to correctly propagate over
    # the multi-threaded Thespian configurations with Queue or UDP bases.
    from src.actors.lead import LeadActor

    # Initialize the Actor system:
    system: ActorSystem = ActorSystem(systemBase="multiprocQueueBase")
    lead: ActorAddress = system.createActor(LeadActor)
    log.info("Created lead actor")
    try:
        # Ask the lead actor to start his work
        response = system.ask(lead, Requests.START)

        # If the lead actor does not reply that he is starting, something is wrong
        if response != Requests.STARTING:
            raise Exception("Lead actor did not start correctly.")

        # Run this while loop for the duration of the program.
        while True:
            sleep(10)
            log.debug("Sending Heartbeat request to lead actor.")
            system.tell(lead, Requests.ARE_YOU_ALIVE)

    except KeyboardInterrupt:
        log.error("The bellboy system was interrupted by the keyboard, exiting...")
    finally:
        system.tell(lead, Requests.STOP)
        system.shutdown()
        return 0


if __name__ == "__main__":
    main()
