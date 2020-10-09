import logging
import sys
from time import sleep

from thespian.actors import ActorAddress, ActorSystem

from src.utils.address_book import AddressBook
from src.utils.cli import CLI
from src.utils.constants import ActorNames, Requests


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

    # Import actors here to instantiate logging system correctly.
    from src.actors.lcd import LiquidCrystalActor
    from src.actors.lead import LeadActor
    from src.actors.ultrasonic import UltrasonicActor

    # Initialize the Actor system:
    system: ActorSystem = ActorSystem(systemBase="multiprocQueueBase")
    address_book = AddressBook()

    lead: ActorAddress = system.createActor(LeadActor)
    address_book.add(ActorNames.LEAD, lead)

    # All the other actors can be added with one-liners:
    address_book.add(ActorNames.LIQUID_CRYSTAL, system.createActor(LiquidCrystalActor))
    address_book.add(ActorNames.ULTRASONIC, system.createActor(UltrasonicActor))

    # Send the complete address book to each thread:
    # Currently the AddressBook arrives EMPTY! So we just send the stored dictionary instead.
    all_addresses = address_book.all()
    for actor in address_book.all().values():
        system.tell(actor, all_addresses)  # Tell each actor everyone's address!

    # Now we can get all the actors to start.
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
