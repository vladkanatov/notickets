from datetime import datetime
import importlib
import inspect

from sqlalchemy import delete
from .logger import logger
from database.models.main_models import AllEvents, session
from .manager import user_agent


class Controller:

    def __init__(self):
        super().__init__()

        self.script = 'parser'
        self.user_agent = user_agent.random()

    def __str__(self) -> str:
        """Этот класс используется для запуска
        скриптов для парсинга информации с различных
        web-ресурсов"""

    @staticmethod
    def _clear_events(parser):
        delete_query = delete(AllEvents).where(getattr(AllEvents, "parser") == parser)

        session.execute(delete_query)

        # Подтверждаем изменения
        session.commit()

    async def load_script(self):
        try:
            parser_module = importlib.import_module(self.script)
            for name in dir(parser_module):
                obj = getattr(parser_module, name)
                if (
                        inspect.isclass(obj)
                        and issubclass(obj, Parser)
                        and obj != Parser
                ):
                    return obj()
        except Exception as e:
            logger.error(f"failed to load parser: {e}")

    async def run(self):
        script = await self.load_script()
        if script:
            parser = script.name
            self._clear_events(parser)
            await script.main()
            logger.info(f'the script{parser} has successfully completed its work')


class Parser(Controller):
    def __init__(self):
        super().__init__()

        self.name = ''

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

        parser = self.name
        if parser == '':
            logger.error('the parser name is not set')

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
