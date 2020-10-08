import argparse
import logging
import os

from src.utils.cli import CLI


def main():
    # cmd line argument handling
    cli = CLI()
    cli.parse_args()

    # create multiprocessing system, housing all our actors
    system = ActorSystem("multiprocQueueBase")

    # create lead actor
    bellboy = system.createActor(BellBoy)
    try:
        system.tell(bellboy, "start")
        system.listen(timeout=1 * 60)  # automatically ends after a minute
    except KeyboardInterrupt:

        pass
    finally:
        system.tell(bellboy, "end")
        system.shutdown()


if __name__ == "__main__":
    main()
