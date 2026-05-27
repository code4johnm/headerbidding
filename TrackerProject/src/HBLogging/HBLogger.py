from __future__ import annotations

import logging
import os
import time
from pprint import pprint as pp


class HBLogger:
    def __init__(self, src, logsPath, print_output=True):
        self.src = src
        self.print_output = print_output
        self.logsPath = logsPath

    def log(self, msg: str, level: str = "INFO") -> None:
        getLevel: dict[str, int] = {
            "CRITICAL": logging.CRITICAL,
            "ERROR": logging.ERROR,
            "WARNING": logging.WARNING,
            "INFO": logging.INFO,
            "DEBUG": logging.DEBUG,
            "NOTSET": logging.NOTSET,
        }

        fmt = f"{time.asctime()} - {self.src}: {msg}"
        if not os.path.exists(self.logsPath):
            os.mkdir(self.logsPath)
        srcLogFolder = os.path.join(self.logsPath, self.src)
        if not os.path.exists(srcLogFolder):
            os.mkdir(srcLogFolder)
        timeStamp = str(int(time.time()))
        logLevel = getLevel[level]
        srcLogPath = os.path.join(srcLogFolder, f"{timeStamp}.log")
        logging.basicConfig(filename=srcLogPath, level=logLevel, format=fmt)
        logger = logging.getLogger(self.src)
        logger.log(logLevel, msg)
        if self.print_output:
            print(fmt)



# a = HBLogger('test')
# a.log('msg')