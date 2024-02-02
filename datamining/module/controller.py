import logging
import os
import importlib
import asyncio
import inspect
import json

class EventParser:
    def __init__(self, delay=0):
        self.delay = delay

    async def parse(self):
        # Реализация асинхронного парсинга для базового класса
        pass

class Bot:
    def __init__(self):
        # Добавляем логгер для текущего класса
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.DEBUG)
        # Конфигурируем логгер
        self._setup_logger()
        
    
    def _setup_logger(self):
        # Добавляем FileHandler
        
        log_file_path_class = os.path.join('logs', f"{self.__class__.__name__.lower()}.log")
        file_handler = logging.FileHandler(log_file_path_class, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)  # Уровень логов для файла
        file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)
        
        # Добавляем StreamHandler (консоль)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)  # Уровень логов для консоли

        # Форматтеры для консольных логов для разных уровней
        info_formatter = logging.Formatter('\033[92m%(asctime)s\033[0m - \033[95m%(name)s\033[0m - \033[92mINFO\033[0m: %(message)s')
        debug_formatter = logging.Formatter('\033[92m%(asctime)s\033[0m - \033[95m%(name)s\033[0m - \033[96mDEBUG\033[0m: %(message)s')
        warning_formatter = logging.Formatter('\033[92m%(asctime)s\033[0m - \033[95m%(name)s\033[0m - \033[93mWARNING\033[0m: %(message)s')
        error_formatter = logging.Formatter('\033[92m%(asctime)s\033[0m - \033[95m%(name)s\033[0m - \033[91mERROR\033[0m: %(message)s')
        critical_formatter = logging.Formatter('\033[92m%(asctime)s\033[0m - \033[95m%(name)s\033[0m - \033[30;41mCRITICAL\033[0m: %(message)s')

        # Устанавливаем соответствующие форматтеры для каждого уровня
        console_handler.setFormatter(info_formatter)  # для info
        self.logger.addHandler(console_handler)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)  # Уровень логов для консоли
        console_handler.setFormatter(debug_formatter)  # для debug
        self.logger.addHandler(console_handler)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)  # Уровень логов для консоли
        console_handler.setFormatter(warning_formatter)  # для warning
        self.logger.addHandler(console_handler)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.ERROR)  # Уровень логов для консоли
        console_handler.setFormatter(error_formatter)  # для error
        self.logger.addHandler(console_handler)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.CRITICAL)  # Уровень логов для консоли
        console_handler.setFormatter(critical_formatter)  # для critical
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
    def __init__(self, scripts_folder, config_filename="config.json"):
        super().__init__()

        self.scripts_folder = scripts_folder
        self.root_directory = os.path.abspath(os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'), '..'))
        self.config_filename = config_filename
        self.config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), config_filename)

    def __str__(self) -> str:
        """Этот класс используется для запуска
        скриптов для парсинга информации с различных
        web-ресурсов"""
    
    async def load_scripts(self):
        self.info("Good")
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

# Пример использования
if __name__ == "__main__":
    scripts_folder = os.path.abspath("путь/к/папке/со/скриптами")
    config_path = os.path.abspath("config.json")
    
    controller = Controller(scripts_folder, config_filename=config_path)
    asyncio.run(controller.run_scripts())
