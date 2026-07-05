import json
import sys
from datetime import datetime


LOG_LEVELS = {"DEBUG": 10, "INFO": 20, "WARN": 30, "ERROR": 40}
_level = LOG_LEVELS.get("INFO", 20)


def set_level(level_name: str):
    global _level
    _level = LOG_LEVELS.get(level_name.upper(), 20)


def _log(level: str, agent: str | None, message: str, **extra):
    if LOG_LEVELS.get(level, 0) < _level:
        return
    record = {
        "timestamp": datetime.now().isoformat(),
        "level": level,
        "agent": agent,
        "message": message,
    }
    if extra:
        record.update(extra)
    print(json.dumps(record, ensure_ascii=False), file=sys.stdout, flush=True)


def debug(agent: str | None, message: str, **extra):
    _log("DEBUG", agent, message, **extra)


def info(agent: str | None, message: str, **extra):
    _log("INFO", agent, message, **extra)


def warn(agent: str | None, message: str, **extra):
    _log("WARN", agent, message, **extra)


def error(agent: str | None, message: str, **extra):
    _log("ERROR", agent, message, **extra)
