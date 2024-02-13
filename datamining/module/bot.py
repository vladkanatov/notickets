import logging
from colorlog import ColoredFormatter
import os
from typing import Any
from .manager import user_agent

class Bot:
    def __init__(self):
        # Добавляем логгер для текущего класса
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.DEBUG)
        # Конфигурируем логгер
        self._setup_logger()
        
        self.user_agent = user_agent.random()
    
    def _setup_logger(self):
        # Удаляем все существующие обработчики
        for handler in self.logger.handlers:
            self.logger.removeHandler(handler)

        # Добавляем FileHandler
        log_file_path_class = os.path.join('logs', f"{self.__class__.__name__.lower()}.log")
        file_handler = logging.FileHandler(log_file_path_class, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)  # Уровень логов для файла
        file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        date_format = "%d-%m-%Y %H:%M:%S"
        console_handler.setFormatter(ColoredFormatter(
            "\033[32m%(asctime)s\033[0m - %(log_color)s%(levelname)s%(reset)s - \033[35m%(name)s\033[0m > %(message)s",
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'bold_red',
            },
            reset=True,
            style='%',
            datefmt=date_format
        ))
        self.logger.addHandler(console_handler)
        
        self.info('Logger was started')
        
    def info(self, message: Any, *args):
        self.logger.info(message, *args)
        
    def debug(self, message: Any, *args):
        self.logger.debug(message, *args)
        
    def error(self, message: Any, *args):
        self.logger.error(message, *args)
        
    def critical(self, message: Any, *args):
        self.logger.critical(message, *args)
        
    def warning(self, message: Any, *args):
        self.logger.warning(message, *args)