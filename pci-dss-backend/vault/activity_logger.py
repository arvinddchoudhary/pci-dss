import json
import os
import time
from datetime import datetime, timezone
from functools import wraps

ACTIVITY_LOG_FILE = os.path.join(os.path.dirname(__file__), 'agent_activity.jsonl')

def log_agent_activity(agent_name: str, action: str, system_id: str = None, details: str = "", duration_ms: float = None):
    """Log every action the agent takes — the agent itself is auditable (Constraint C3)."""
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "agent_name": agent_name,
        "action": action,
        "system_id": system_id,
        "details": details,
        "duration_ms": duration_ms
    }
    
    os.makedirs(os.path.dirname(ACTIVITY_LOG_FILE), exist_ok=True)
    with open(ACTIVITY_LOG_FILE, 'a') as f:
        f.write(json.dumps(record) + '\n')
    
    return record


def track_agent_action(agent_name: str, action: str):
    """Decorator to automatically log agent function calls with timing."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            system_id = None
            
            # Try to extract system_id from args
            for arg in args:
                if hasattr(arg, 'system_id'):
                    system_id = arg.system_id
                    break
            
            log_agent_activity(agent_name, f"START: {action}", system_id, f"Function: {func.__name__}")
            
            try:
                result = func(*args, **kwargs)
                duration = (time.time() - start) * 1000
                
                status = getattr(result, 'status', 'unknown')
                log_agent_activity(
                    agent_name, f"COMPLETE: {action}", system_id,
                    f"Result: {status}", duration
                )
                return result
            except Exception as e:
                duration = (time.time() - start) * 1000
                log_agent_activity(
                    agent_name, f"ERROR: {action}", system_id,
                    f"Exception: {str(e)}", duration
                )
                raise
        return wrapper
    return decorator


def get_activity_log(limit: int = 100) -> list:
    """Retrieve recent agent activity entries."""
    entries = []
    if not os.path.exists(ACTIVITY_LOG_FILE):
        return entries
    
    with open(ACTIVITY_LOG_FILE, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                entries.append(json.loads(line))
    
    return entries[-limit:]