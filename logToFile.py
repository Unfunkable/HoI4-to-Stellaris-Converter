#!/usr/bin/python

from distutils.log import debug
import sys
import logging


class Logger(object):
    logging.addLevelName(15, "PROGRESS")
    def log(self, level, message):
        logging.basicConfig(filename='log.txt', filemode='a', format = "%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y:%m:%d %H:%M:%S", level=logging.DEBUG)
        if level == "info":
            logging.info(message)
        elif level == "warning":
            logging.warning(message)
        elif level == "error":
            logging.error(message)
        elif level == "progress":
            logging.log(15, message)
        else:
            logging.debug(message)

#     def __init__(self):
#         self.terminal = sys.stdout
#         self.log = open("log.txt", "a")

#     def write(self, message):
#         self.log = open("log.txt", "a")
#         self.terminal.write(message)
#         self.log.write(message)
#         self.log.close()

#     def flush(self):
#         pass


# sys.stdout = Logger()
# sys.stderr = sys.stdout