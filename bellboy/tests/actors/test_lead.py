import time

from actors.lead import BellboyLeadActor
from tests import ActorSystem, logcfg
from utils.messages import Init, Request, Response, TestMode


def test_leadActor():

    with ActorSystem("multiprocQueueBase", logcfg) as actor_system:
        lead = actor_system.createActor(BellboyLeadActor, globalName="test_lead")
        status = actor_system.ask(lead, Init(senderName="test_system"))
        assert status == Response.READY

        actor_system.tell(lead, TestMode())

        # Actor should reply that it is starting when asked.
        response = actor_system.ask(lead, Request.START)
        assert response == Response.STARTED

        # wait for messages to settle
        time.sleep(2)

        # Actor should reply that it is done when stopped.
        response = actor_system.ask(lead, Request.STOP)
        assert response == Response.DONE

        # wait for messages to settle
        time.sleep(2)
