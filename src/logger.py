# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


import os
import logging

from constants import WORKINGDIR


__all__ = [
    'TraceLogger'
]


class Logger(object):
    def __init__(self, logger_type: str):
        self.__set_logger_type(logger_type)

        handler = logging.FileHandler(os.path.join(WORKINGDIR, '{0}_log.log'.format(logger_type)))
        handler.setLevel(logging.DEBUG)
        self.__set_handler(handler)

        logger = logging.getLogger('{0}-local'.format(logger_type))
        logger.setLevel(logging.DEBUG)
        logger.addHandler(handler)
        self.__set_logger(logger)

    def __get_logger_type(self):
        return self.__logger_type

    def __set_logger_type(self, logger_type):
        self.__logger_type = logger_type

    def __get_handler(self):
        return self.__handler

    def __set_handler(self, handler):
        self.__handler = handler

    def __get_logger(self):
        return self.__logger

    def __set_logger(self, logger):
        self.__logger = logger

    def debug(self, message: str) -> None:
        logger = self.__get_logger()
        logger.debug(message)

    def info(self, message: str) -> None:
        logger = self.__get_logger()
        logger.info(message)

    def warning(self, message: str) -> None:
        logger = self.__get_logger()
        logger.warning(message)

    def error(self, message: str) -> None:
        logger = self.__get_logger()
        logger.error(message)

    def critical(self, message: str) -> None:
        logger = self.__get_logger()
        logger.critical(message)


TraceLogger = Logger('Trace')
