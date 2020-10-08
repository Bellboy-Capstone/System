import logging
from time import sleep

from thespian.actors import ActorSystem

from src.actors.lead import LeadActor
from src.utils.cli import CLI
from src.utils.constants import Requests


def main():
    # cmd line argument handling
    cli = CLI()
    cli.parse_args()

    # create multiprocessing system, housing all our actors
    system = ActorSystem("multiprocQueueBase")

    # create lead actor
    lead = system.createActor(LeadActor)
    try:
        response = system.ask(lead, Requests.START)
        if response != Requests.STARTING:
            raise Exception("Lead actor did not start correctly.")
        while True:
            sleep(5)
    except KeyboardInterrupt:
        logging.error("The bellboy system was interrupted by the keyboard.")
    finally:
        system.tell(lead, Requests.STOP)
        system.shutdown()


if __name__ == "__main__":
    main()
