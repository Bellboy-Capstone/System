import logging
log = logging.getLogger("actors")

from thespian.actors import ActorAddress

# identifying actors
addressBook = {}
def nameOf(address: ActorAddress):
    return addressBook.get(str(address), "ADDRESS_NOT_FOUND")
