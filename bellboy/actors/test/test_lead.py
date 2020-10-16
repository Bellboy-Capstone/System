from thespian.actors import ActorSystem

from src.actors.lead import LeadActor
from src.utils.constants import Requests


class TestLeadActor:
    def test_receiveMsg_Requests(self, actor_system: ActorSystem):
        lead = actor_system.createActor(LeadActor)

        # Actor should reply that it is starting when asked.
        response = actor_system.ask(lead, Requests.START)
        assert response == Requests.STARTING
