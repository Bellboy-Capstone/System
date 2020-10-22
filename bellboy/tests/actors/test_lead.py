from thespian.actors import ActorSystem

from actors.lead import BellboyLeadActor
from utils.messages import Request, Response, TestMode, Init


class TestLeadActor:
    def test_receiveMsg_Requests(self, actor_system: ActorSystem):
        lead = actor_system.createActor(BellboyLeadActor, globalName="test_lead")
        status = actor_system.ask(lead, Init())
        actor_system.tell(lead, TestMode())

        # Actor should reply that it is starting when asked.
        response = actor_system.ask(lead, Request.START)
        assert response == Response.STARTED

        # Actor should reply that it is done when stopped.
        response = actor_system.ask(lead, Request.STOP)
        assert response == Response.DONE