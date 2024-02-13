import os
import importlib
import asyncio
import inspect
import json
from .bot import Bot
from datamining.module.logcontroller import LogController



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
                            and issubclass(obj, Parser)
                            and obj != Parser
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

class Parser(Controller):
    def __init__(self, delay=0):
        super().__init__()
        self.delay = delay

    def run(self):
        self.info("Good")
        self.debug("Normal")
        self.warning("Kek")
        self.error('Kuka')
        self.critical('AAAA')