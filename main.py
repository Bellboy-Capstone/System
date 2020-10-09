import logging
import sys
from time import sleep

from thespian.actors import ActorSystem, ActorAddress

from src.actors.lead import LeadActor
from src.utils.cli import CLI
from src.utils.constants import Requests


def main() -> int:
    """
    Starts the Bellboy system.

    :return: exit code
    """
    log = logging.getLogger("Bellboy")
    log.info("Starting the Bellboy system")

    # Parse arguments and configure logging.
    cli = CLI()
    cli.setup(sys.argv)

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
        else:
            log.info(f"Lead actor replied with '{response.name}'")

        # Run this while loop for the duration of the program.
        while True:
            sleep(10)
            log.debug("Sending Heartbeat request to lead actor.")
            system.tell(lead, Requests.ARE_YOU_ALIVE)

    except KeyboardInterrupt:
        log.error("The bellboy system was interrupted by the keyboard.")
    finally:
        system.tell(lead, Requests.STOP)
        system.shutdown()
        return 0


if __name__ == "__main__":
    main()
