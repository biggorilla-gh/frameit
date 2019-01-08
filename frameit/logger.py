import logging
import datetime
import os, sys
#
# LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
# DATE_FORMAT = "%Y-%m-%dT%H:%M:%S%z"

def create_logger(name, debug=True):
    new_logger = logging.Logger(name)

    ch = logging.StreamHandler()

    if debug:
        ch.setLevel(logging.DEBUG)
    else:
        ch.setLevel(logging.INFO)

    new_logger.addHandler(ch)

    logname = 'frameit/api/logs/logs.txt'
    logging.basicConfig(filename=logname,
                        filemode='a',
                        format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.NOTSET)

    return new_logger


logger = create_logger('newLog', debug=True)