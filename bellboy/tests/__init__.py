import pytest
from thespian.actors import ActorSystem as ThespianActorSystem


@pytest.mark.skip(reason="actorsystem context manager, not a testing class")
class ActorSystem(object):
    def __init__(self, systemBase: str, logcfg: dict):
        self.test_system = ThespianActorSystem(systemBase="multiprocQueueBase", logDefs=logcfg)

    def __enter__(self):
        return self.test_system

    def __exit__(self, type, value, traceback):
        self.test_system.shutdown()


logcfg = {
    "version": 1,
    "formatters": {
        "standard": {
            "format": "%(asctime)s :: %(levelname)s :: %(name)s :: %(funcName)s() :: %(message)s"
        },
    },
    "handlers": {
        "sh": {
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
            "formatter": "standard",
            "level": "INFO"
        },
    },
    "loggers": {"": {"handlers": ["sh"], "level": "INFO"}},
}
