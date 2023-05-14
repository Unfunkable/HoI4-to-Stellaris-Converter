#!/usr/bin/python
import logging


class Logger(object):
    logging.addLevelName(15, "PROGRESS")

    def log(self, level, message):
        logging.basicConfig(filename='log.txt', filemode='a',
                            format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y:%m:%d %H:%M:%S", level=logging.DEBUG)
        match level:
            case "info":
                logging.info(message)
            case "warning":
                logging.warning(message)
            case "error":
                logging.error(message)
            case "progress":
                logging.log(15, message)
            case _:
                logging.debug(message)
