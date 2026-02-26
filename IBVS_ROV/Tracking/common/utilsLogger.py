import logging
import sys
from logging import NOTSET, DEBUG, INFO, WARNING, ERROR, CRITICAL
import datetime
from datetime import datetime
import os

LOG_LEVEL_CONSOLE = WARNING
LOG_LEVEL_FILE = WARNING
LOG_LEVEL_GLOBAL = WARNING
LOG_FOLDER = "log"
LOG_FILE_BASE = ""

logging.getLogger("root").setLevel(NOTSET)

def loggerCreate(name, globalLogLevel = LOG_LEVEL_GLOBAL, 
                 fileBase = LOG_FILE_BASE, 
                 fileLevel = LOG_LEVEL_FILE, 
                 fileFolder = LOG_FOLDER,
                 consoleLevel = LOG_LEVEL_CONSOLE):
    
    # Getting filename
    now = datetime.now()
    f = now.strftime("%Y-%m-%d_%H-%M-%S")
    loggingFile = os.path.join(fileFolder, f"logfile_{f}_{fileBase}.log")
    
    # Global logger
    logger = logging.getLogger(name)
    logger.setLevel(globalLogLevel)

    logger.handlers = []
    
    # Console handler
    formatter = logging.Formatter("%(asctime)s.%(msecs)03d - %(levelname)8s - %(processName)s - %(threadName)s - %(name)s - %(funcName)s - %(message)s",
        # style="{",
        datefmt="%Y-%m-%d %H:%M:%S")
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(consoleLevel)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler
    os.makedirs(LOG_FOLDER, exist_ok=True)
    file_handler = logging.FileHandler(loggingFile)
    file_handler.setLevel(fileLevel)  # Always debug level for file
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    
    
    return logger
    
def loggerGet(name):
    return logging.getLogger(name)
