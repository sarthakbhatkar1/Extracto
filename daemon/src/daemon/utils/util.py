import json
import jsonschema
from enum import Enum
from typing import Dict, Any, Optional
from datetime import datetime
from uuid import uuid4

from daemon.common.config.config_store import ConfigStore
from daemon.logger.log_utils import Logger

logger = Logger()


class TaskStatumEnum(str, Enum):
    NOT_STARTED = "Not Started"
    IN_PROGRESS = "In Progress"
    SUCCESS = "Success"
    FAILURE = "Failure"
    PARSING = "Parsing"
    EXTRACTING = "Extracting"
    SUMMARIZING = "Summarising"
    VALIDATING = "Validating"


def validate_json_against_schema(data: str, schema: Dict[str, Any]) -> Dict[str, Any]:
    """Validate LLM JSON output against schema with repair attempts."""
    try:
        parsed = json.loads(data)
        jsonschema.validate(instance=parsed, schema=schema)
        return parsed
    except json.JSONDecodeError:
        return _repair_json(data)
    except jsonschema.ValidationError as e:
        logger.warning(f"Schema validation failed: {e}")
        return _repair_json(data, schema)


def _repair_json(json_str: str, schema: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Repair malformed JSON from LLM."""
    # Simple repair: extract JSON-like content
    start = json_str.find('{')
    end = json_str.rfind('}') + 1
    if start >= 0 and end > start:
        try:
            return json.loads(json_str[start:end])
        except:
            pass
    
    # Fallback: return as dict with warning
    logger.warning("JSON repair failed, returning raw string")
    return {"raw_response": json_str, "error": "invalid_json"}


def get_unique_number():
    return str(uuid4()).lower()


def get_current_datetime():
    UTC_ISO_TIME_FORMAT = "%Y-%m-%dT%H:%M:%S.000Z"
    return datetime.utcnow().strftime(UTC_ISO_TIME_FORMAT)
