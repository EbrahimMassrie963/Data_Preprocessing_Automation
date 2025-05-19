import logging
import os

def get_logger(name: str = "GeminiAgent") -> logging.Logger:
    if not os.path.exists("logs"):
        os.makedirs("logs")

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)  # default level

    if not logger.hasHandlers():
        file_handler = logging.FileHandler("logs/agent.log")
        formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
