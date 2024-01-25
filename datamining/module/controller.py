import os
import importlib
import asyncio
import inspect
import json
from datamining.module.bot import Bot

class EventParser:
    def __init__(self, delay=0):
        self.delay = delay

    async def parse(self):
        # Реализация асинхронного парсинга для базового класса
        pass

class Controller(Bot):
    def __init__(self, log_file_path, logger_name, scripts_folder, config_filename="config.json"):
        super().__init__(log_file_path=log_file_path, logger_name=logger_name)
        self.scripts_folder = scripts_folder
        self.root_directory = os.path.abspath(os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'), '..'))
        self.config_filename = config_filename
        self.config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), config_filename)

    def __str__(self) -> str:
        """Этот класс используется для запуска
        скриптов для парсинга информации с различных
        web-ресурсов"""
    
    async def load_scripts(self):
        self.info('Запуск загрузки скрипта')
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
    config_path = os.path.abspath("путь/к/config.json")
    
    controller = Controller(scripts_folder, config_filename=config_path)
    asyncio.run(controller.run_scripts())
