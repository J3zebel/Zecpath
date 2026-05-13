import os
import logging
from utils.logger import get_logger

def test_logger_creation():
    logger = get_logger("test_logger", log_file="test.log", level=logging.DEBUG)
    
    # Check logger level
    assert logger.level == logging.DEBUG
    
    # Check that it has two handlers (console and file)
    assert len(logger.handlers) == 2
    
    # Write a test message
    logger.info("This is a test message.")
    
    # Check if file was created
    log_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.abspath(os.path.join(log_dir, ".."))
    log_path = os.path.join(root_dir, "test.log")
    
    assert os.path.exists(log_path)
    
    # Read file and verify content
    with open(log_path, 'r', encoding='utf-8') as f:
        content = f.read()
        assert "This is a test message." in content

    # Cleanup
    # Close handlers to release file locks (important on Windows)
    for handler in list(logger.handlers):
        handler.close()
        logger.removeHandler(handler)
        
    if os.path.exists(log_path):
        os.remove(log_path)
