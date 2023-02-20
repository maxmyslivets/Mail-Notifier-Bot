import logging
import traceback

import coloredlogs
import inspect

from config import LOG


class Logger:
    def __init__(self, name, file_name=LOG, level=logging.DEBUG, fmt=None):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        if fmt is None:
            fmt = '%(asctime)s - %(name)s - %(levelname)s - %(funcname)s - %(message)s'
        formatter = logging.Formatter(fmt)

        # создаем обработчик для записи в файл
        file_handler = logging.FileHandler(file_name)
        file_handler.setFormatter(formatter)

        # создаем обработчик для вывода в консоль
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        # добавляем обработчики к логгеру
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        coloredlogs.install(level='DEBUG', logger=self.logger, use_chroot=False)

    def debug(self, msg, *args, **kwargs):
        frame = inspect.currentframe().f_back
        self.logger.debug(msg, *args, extra={'funcname': frame.f_code.co_name}, **kwargs)

    def info(self, msg, *args, **kwargs):
        frame = inspect.currentframe().f_back
        self.logger.info(msg, *args, extra={'funcname': frame.f_code.co_name}, **kwargs)

    def warning(self, msg, *args, **kwargs):
        frame = inspect.currentframe().f_back
        self.logger.warning(msg, *args, extra={'funcname': frame.f_code.co_name}, **kwargs)

    def error(self, msg, *args, **kwargs):
        frame = inspect.currentframe().f_back
        self.logger.error(msg + '\n' + traceback.format_exc(), *args, extra={'funcname': frame.f_code.co_name}, **kwargs)

    def critical(self, msg, *args, **kwargs):
        frame = inspect.currentframe().f_back
        self.logger.critical(msg, *args, extra={'funcname': frame.f_code.co_name}, **kwargs)


logger = Logger("MailNotifierBot")
