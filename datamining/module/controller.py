from datetime import datetime
import importlib
import inspect

from sqlalchemy import delete
from .logger import logger
from database.models.main_models import AllEvents, session
from .manager import user_agent
from datamining.module.logger import parser_name
from datamining.module.manager.session import AsyncSession


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
    def _clear_events():
        delete_query = delete(AllEvents).where(getattr(AllEvents, "parser") == parser_name)

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
            self._clear_events()
            try:
                await script.main()  # Запускаем async def main в parser.py
            except AttributeError as e:
                logger.error(e)
                return

            logger.info(f'the script {parser_name} has successfully completed its work')
            if script.session is not None:
                await script.session.close()


class Parser(Controller):
    def __init__(self):
        super().__init__()

        self.session = AsyncSession()
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

        parser = parser_name

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
