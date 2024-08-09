import logging
from colorlog import ColoredFormatter
import os
from typing import Any
from .manager import user_agent
import subprocess

# Получаем текущую ветку Git
git_branch = subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD']).strip().decode('utf-8')


class _ColoredFormatter(ColoredFormatter):
    def format(self, record):
        record.git_branch = git_branch
        return super(_ColoredFormatter, self).format(record)


class _Formatter(logging.Formatter):
    def format(self, record):
        record.git_branch = git_branch
        return super(_Formatter, self).format(record)


class Logger:

    def __init__(self):
        # Добавляем логгер для текущего класса
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self._create_logs_dir()
        # Конфигурируем логгер
        self._setup_logger()

        self.user_agent = user_agent.random()

    def _create_logs_dir(self):
        import os

        # Путь к папке логов
        log_dir = 'logs'

        # Проверяем наличие папки
        if not os.path.exists(log_dir):
            # Если папка отсутствует, создаем ее
            os.makedirs(log_dir)
            self.info(f"logs directory was created")
        else:
            pass

    def _setup_logger(self):
        # Удаляем все существующие обработчики
        for handler in self.logger.handlers:
            self.logger.removeHandler(handler)

        # Добавляем FileHandler
        log_file_path_class = os.path.join('logs', f"{self.__class__.__name__.lower()}.log")
        file_handler = logging.FileHandler(log_file_path_class, encoding="utf-8")
        file_handler.setLevel(logging.INFO)  # Уровень логов для файла
        file_formatter = _Formatter('%(asctime)s - %(git_branch)s - %(pathname)s:%(lineno)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)

        # Добавляем DebugFileHandler
        debug_log_path = os.path.join('logs', 'debug_logger.log')
        debug_file_handler = logging.FileHandler(debug_log_path, encoding='utf-8')
        debug_file_handler.setLevel(logging.DEBUG)
        debug_file_handler.setFormatter(file_formatter)
        self.logger.addHandler(debug_file_handler)

        # Добавляем StdOutHandler
        console_handler = logging.StreamHandler()
        date_format = "%d-%m-%Y %H:%M:%S"
        console_handler.setFormatter(_ColoredFormatter(
            "\033[32m%(asctime)s\033[0m - %(log_color)s%(levelname)s%(reset)s - \033[35m%(git_branch)s\033[0m > %(log_color)s%(message)s%(reset)s",
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

        self.info('logger was started')

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


logger = Logger()
parser_name = git_branch
