from datetime import datetime
import os
import importlib
import asyncio
import inspect
import json

from sqlalchemy import delete
from .bot import Bot
from database.models.main_models import AllEvents, session

# LogContoller is coming
# from datamining.module.logcontroller import LogController


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
        
    def _clear_events(self, parser):
        delete_query = delete(AllEvents).where(getattr(AllEvents, "parser") == parser)

        session.execute(delete_query)

        # Подтверждаем изменения
        session.commit()
    
    async def load_scripts(self):
        scripts = []
        with open(self.config_path, 'r') as config_file:
            config = json.load(config_file)

        for file_name in os.listdir(self.scripts_folder):
            if file_name.endswith(".py"):
                module_name = file_name[:-3]
                module_path = f'datamining.scripts.{module_name}'

                try:
                    module = importlib.import_module(module_path)
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
        scripts : list = await self.load_scripts()
        tasks = [self.run_script_with_delay(script) for script in scripts]

        await asyncio.gather(*tasks)

    async def run_script_with_delay(self, script):
        self._clear_events(script.__class__.__module__.split('.')[-1])
        await script.run()
        script.info('Программа успешно завершила работу')
        await asyncio.sleep(script.delay)
        

class Parser(Controller):
    def __init__(self, config_filename="config.json"):
        super().__init__(config_filename)
        
        self.delay = 3600 # Задержка по-умолчанию
        
    def register_event( 
                       self, 
                       event_name: str, 
                       link: str, 
                       date: datetime,
                       venue: str = None,
                       avg_price: int = -1):
        
        event_name = event_name.replace('\n', ' ')
        if venue is not None:
            venue = venue.replace('\n', ' ')
        
        parser = self.__class__.__module__.split('.')[-1]
        
        log_time_format = '%Y-%m-%d %H:%M:%S'
        normal_date = datetime.strftime(date, log_time_format)
        
        new_event = AllEvents(
            name=event_name,
            link=link,
            parser=parser,
            date=normal_date,
            venue=venue,
            average_price=avg_price
        )
        session.add(new_event)
        session.commit()