"""
General utility functions for the backend.
"""
from typing import Any, Dict, Optional

def format_response(status: str, message: str, data: Optional[Any] = None) -> Dict[str, Any]:
    """
    Formats a standard JSON response dictionary.
    
    Args:
        status (str): "success" or "error".
        message (str): Human-readable message.
        data (Optional[Any]): The payload data. Defaults to None.
        
    Returns:
        Dict[str, Any]: Formatted response dictionary.
    """
    response = {
        "status": status,
        "message": message
    }
    if data is not None:
        response["data"] = data
    return response
