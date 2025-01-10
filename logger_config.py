import logging
import os
from datetime import datetime


def setup_logger(name, log_dir='logs/', level=logging.DEBUG):
    """Setup a logger for a specific module or class."""
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    if not os.path.isdir(log_dir):
        os.mkdir(log_dir)
    current_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    log_file = f"{log_dir}FilterDesign_{current_time}.log"

    # Create handlers
    file_handler = logging.FileHandler(log_file)
    console_handler = logging.StreamHandler()

    # Set handler levels
    file_handler.setLevel(level)
    console_handler.setLevel(logging.INFO)

    # Create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add handlers to the logger
    if not logger.hasHandlers():  # Prevent adding handlers multiple times
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger
