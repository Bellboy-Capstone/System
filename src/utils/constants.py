from enum import Enum, auto


class ChoicesEnum(Enum):
    """Augments a regular enum with methods to return lists of enum
    choices/names."""

    @classmethod
    def get_names(cls):
        names = []
        for choice in cls:
            names.append(choice.name)

        return names

    @classmethod
    def get_choices(cls):
        choices = []
        for choice in cls:
            choices.append(choice)

        return choices


class Requests(ChoicesEnum):
    START = auto()
    STARTING = auto()
    STOP = auto()
    STOPPING = auto()
    ARE_YOU_ALIVE = auto()


class RunLevels(ChoicesEnum):
    LOCAL = auto()
    LOCAL_STANDALONE = auto()
    PRODUCTION = auto()


class LogLevels(ChoicesEnum):
    DEBUG = auto()
    INFO = auto()
    WARNING = auto()
    ERROR = auto()
