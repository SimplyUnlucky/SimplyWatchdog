import logging
import logging.handlers
import sys
from pathlib import Path
import colorlog
from .config import config

def setup_logger(name: str = "SystemWatch"):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG if config.get("app.debug") else logging.INFO)
    
    if logger.handlers:
        return logger

    # Console Handler with Colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_formatter = colorlog.ColoredFormatter(
        "%(log_color)s%(asctime)s - [%(name)s] - %(levelname)s - %(message)s",
        datefmt="%H:%M:%S",
        log_colors={
            'DEBUG':    'cyan',
            'INFO':     'green',
            'WARNING':  'yellow',
            'ERROR':    'red',
            'CRITICAL': 'red,bg_white',
        }
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File Handler
    log_file = config.get("logging.file_path", "logs/app.log")
    Path(log_file).parent.mkdir(parents=True, exist_ok=True)
    
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=config.get("logging.max_size_mb", 10) * 1024 * 1024,
        backupCount=5
    )
    file_formatter = logging.Formatter(
        "%(asctime)s - [%(name)s] - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    return logger

logger = setup_logger()
