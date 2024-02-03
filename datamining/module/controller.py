import logging
import os
import importlib
import asyncio
import inspect
import json
from colorlog import ColoredFormatter

class AsyncStreamHandler(logging.Handler):
    async def emit(self, record):
        # Вместо использования self.handle(record), мы используем asyncio.to_thread
        await asyncio.to_thread(super().emit, record)


class Bot:
    def __init__(self):
        # Добавляем логгер для текущего класса
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.DEBUG)
        # Конфигурируем логгер
        self._setup_logger()
        
    
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
        
    def info(self, message: str, *args):
        self.logger.info(message, *args)
        
    def debug(self, message: str, *args):
        self.logger.debug(message, *args)
        
    def error(self, message: str, *args):
        self.logger.error(message, *args)
        
    def critical(self, message: str, *args):
        self.logger.critical(message, *args)
        
    def warning(self, message: str, *args):
        self.logger.warning(message, *args)


class Controller(Bot):
    def __init__(self, config_filename="config.json"):
        super().__init__()

        self.scripts_folder = os.path.abspath("/home/lon8/python/projects/notickets/datamining/scripts")
        self.root_directory = os.path.abspath(os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'), '..'))
        self.config_filename = config_filename
        self.config_path = os.path.join(self.root_directory, config_filename)

    def __str__(self) -> str:
        """Этот класс используется для запуска
        скриптов для парсинга информации с различных
        web-ресурсов"""
    
    async def load_scripts(self):
        scripts = []
        with open(self.config_path, 'r') as config_file:
            config = json.load(config_file)

        for file_name in os.listdir(self.scripts_folder):
            if file_name.endswith(".py"):
                module_name = file_name[:-3]
                module_path = os.path.join(self.scripts_folder, file_name)

                try:
                    module = importlib.import_module(module_name)
                    for name in dir(module):
                        obj = getattr(module, name)
                        if (
                            inspect.isclass(obj)
                            and issubclass(obj, EventParser)
                            and obj != EventParser
                            and config.get(module_name, False)
                        ):
                            scripts.append(obj())
                except Exception as e:
                    print(f"Failed to load {module_name}: {e}")

        return scripts

    async def run_scripts(self):
        scripts = await self.load_scripts()
        tasks = []

        for script in scripts:
            tasks.append(self.run_script_with_delay(script))

        await asyncio.gather(*tasks)

    async def run_script_with_delay(self, script):
        await asyncio.sleep(script.delay)
        await script.parse()

class EventParser(Controller):
    def __init__(self, delay=0):
        super().__init__()
        self.delay = delay

    def run(self):
        self.info("Good")
        self.debug("Normal")
        self.warning("Kek")
        self.error('Kuka')
        self.critical('AAAA')
        
    
# Пример использования
if __name__ == "__main__":
    config_path = os.path.abspath("config.json")
    
    # controller = Controller(scripts_folder, config_filename=config_path)
    # asyncio.run(controller.run_scripts())

    x = EventParser()
    x.run()