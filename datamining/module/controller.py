from datetime import datetime, timedelta
import gzip
import logging
import os
import importlib
import asyncio
import inspect
import json
import re
import threading
from typing import Any
from colorlog import ColoredFormatter
            
class Bot:
    def __init__(self):
        # Добавляем логгер для текущего класса
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.DEBUG)
        # Конфигурируем логгер
        self._setup_logger()
        self.schedule_compressor
        
    
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
        
        log_info = {
            "msg": message,
            "timestamp": int(datetime.now().timestamp()),
            "level": "INFO",
            "name": self.logger.name
        }
        
    def debug(self, message: Any, *args):
        self.logger.debug(message, *args)
        
    def error(self, message: Any, *args):
        self.logger.error(message, *args)
        
    def critical(self, message: Any, *args):
        self.logger.critical(message, *args)
        
    def warning(self, message: Any, *args):
        self.logger.warning(message, *args)


class Controller(Bot):
    def __init__(self, config_filename="config.json"):
        super().__init__()

        self.scripts_folder = os.path.abspath("/home/lon8/python/projects/notickets/datamining/scripts")
        self.root_directory = os.path.abspath(os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'), '..'))
        self.config_filename = config_filename
        self.config_path = os.path.join(self.root_directory, config_filename)
        
        self.log_controller = LogController(log_folder="logs")
        asyncio.create_task(self.log_controller.schedule_compression())
        
        self.loop = asyncio.get_event_loop()
        self.loop.run_until_complete(self.run_scripts())

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
                    self.error(f"Failed to load {module_name}: {e}")

        return scripts

    async def run_scripts(self):
        scripts = await self.load_scripts()
        tasks = [self.run_script_with_delay(script) for script in scripts]

        await asyncio.gather(*tasks)

    async def run_script_with_delay(self, script):
        await asyncio.sleep(script.delay)
        await script.kernel()

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

class LogController(Bot):
    def __init__(self, log_folder):
        self.log_folder = log_folder
        self.compress_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        self.schedule_compression()

    def parse_log_line(self, log_line):
        log_pattern = re.compile(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) - (\S+) - (\S+) - (.+)')
        match = log_pattern.match(log_line)
        if match:
            timestamp_str, name, level, msg = match.groups()
            timestamp = int(datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S,%f").timestamp())
            return {
                "time": timestamp_str,
                "timestamp": timestamp,
                "name": name,
                "level": level,
                "msg": msg
            }
        else:
            return None

    async def serialize_and_compress_logs(self):
        log_files = [f for f in os.listdir(self.log_folder) if f.endswith(".log")]
        now = datetime.now()

        for log_file in log_files:
            log_path = os.path.join(self.log_folder, log_file)
            compressed_path = os.path.join(self.log_folder, f"{now.strftime('%Y-%m-%d')}_compressed.gz")

            with open(log_path, 'r') as log_file:
                logs = [self.parse_log_line(line) for line in log_file.readlines() if line.strip()]

            async with gzip.open(compressed_path, 'wb') as compressed_file:
                for log in logs:
                    log_json = json.dumps(log) + '\n'
                    compressed_file.write(log_json.encode('utf-8'))

            os.remove(log_path)
            self.info(f"Logs compressed and renamed: {compressed_path}")

    def schedule_compression(self):
        threading.Timer(self.time_until_midnight(), self.schedule_compression).start()
        self.serialize_and_compress_logs()

    def time_until_midnight(self):
        midnight = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        return (midnight - datetime.now()).total_seconds()

    
# Пример использования
if __name__ == "__main__":
    config_path = os.path.abspath("config.json")
    
    # controller = Controller(scripts_folder, config_filename=config_path)
    # asyncio.run(controller.run_scripts())

    x = EventParser()
    x.run()