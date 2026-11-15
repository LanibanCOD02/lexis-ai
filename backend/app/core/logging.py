"""
Structured logging configuration module.
Configures logging for the entire application.
"""
import logging
import sys

def setup_logging(log_level: str = "INFO") -> None:
    """
    Initializes basic logging configuration.
    
    Args:
        log_level (str): The logging level to set (e.g., "DEBUG", "INFO", "WARNING").
    """
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Ensure uvicorn logs follow the same level
    logging.getLogger("uvicorn.access").setLevel(numeric_level)
    logging.getLogger("uvicorn.error").setLevel(numeric_level)
