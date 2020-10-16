import logging
from typing import Dict

from thespian.actors import ActorAddress

from src.utils.constants import ActorNames


class AddressBook:
    """Stores the addresses of all active actors to make message passing
    easier."""

    log: logging.Logger = logging.getLogger("AddressBook")
    addresses: Dict[ActorNames, ActorAddress] = {}

    def add(self, name: ActorNames, address: ActorAddress):
        """Adds an actor and its address to the address book."""
        self.log.debug(f"Added new actor {name.name} to address book.")
        self.addresses[name] = address

    def get(self, name: ActorNames) -> ActorAddress:
        """Finds the address of a given actor who was added to the address
        book."""
        if name in self.addresses.keys():
            return self.addresses[name]
        else:
            raise Exception("The requested actor was never added to the address book!")

    def all(self) -> Dict[ActorNames, ActorAddress]:
        """
        Returns all addresses for performing bulk operations.

        Be careful not to remove actors.
        """
        return self.addresses
