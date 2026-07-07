from enum import Enum, auto

class ExecutionPhase(Enum):
    VALIDATING = auto()
    PREPARING_WORKSPACE = auto()
    INSTALLING_DEPENDENCIES = auto()
    EXECUTING = auto()
    COLLECTING_RESULTS = auto()
    PERSISTING_RESULTS = auto()
    COMPLETED = auto()
    FAILED = auto()
