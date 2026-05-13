import logging
import os
import sys

def get_logger(name: str, log_file: str = "ai_activities.log", level=logging.INFO):
    """
    Sets up and returns a logger with both console and file handlers.
    
    Args:
        name (str): Name of the logger (typically __name__).
        log_file (str): File to output logs to. Defaults to "ai_activities.log".
        level: Logging level.
        
    Returns:
        logging.Logger: Configured logger.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Prevent duplicate logging if get_logger is called multiple times
    if logger.handlers:
        return logger

    # Create formatters
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (put logs in the root directory by default)
    log_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.abspath(os.path.join(log_dir, ".."))
    log_path = os.path.join(root_dir, log_file)
    
    file_handler = logging.FileHandler(log_path, encoding='utf-8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
