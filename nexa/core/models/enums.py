from enum import Enum, auto

class Status(Enum):
    PENDING = auto()
    RUNNING = auto()
    SUCCESS = auto()
    FAILED = auto()
    PARTIAL = auto()
    ROLLED_BACK = auto()

class Operation(Enum):
    GENERATE = "GENERATE"
    MODIFY = "MODIFY"
    DELETE = "DELETE"
    MOVE = "MOVE"
    RENAME = "RENAME"
    OPTIMIZE = "OPTIMIZE"
    REPAIR = "REPAIR"
    DOCUMENT = "DOCUMENT"
    TRANSLATE = "TRANSLATE"
    EXPLAIN = "EXPLAIN"

class RiskLevel(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class EventPriority(Enum):
    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"

class SearchStrategy(Enum):
    EXACT = "EXACT"
    NORMALIZED = "NORMALIZED"
    FUZZY = "FUZZY"
    AST = "AST"

class PatchStrategy(Enum):
    MODIFY = "MODIFY"
    CREATE = "CREATE"
    DELETE = "DELETE"
    RENAME = "RENAME"
