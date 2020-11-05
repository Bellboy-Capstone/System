import pytest
from thespian.actors import ActorSystem


@pytest.fixture
def actor_system() -> ActorSystem:
    """Returns an empty, non-threaded actor system."""
    return ActorSystem()
