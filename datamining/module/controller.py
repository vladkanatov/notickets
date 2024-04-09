from datetime import datetime
import importlib
import inspect

from .logger import logger
from .manager import user_agent
from datamining.module.logger import parser_name
from datamining.module.manager.session import AsyncSession, AsyncProxySession


class Controller:

    def __init__(self):
        super().__init__()

        self.script = 'parser'
        self.user_agent = user_agent.random()

    def __str__(self) -> str:
        """Этот класс используется для запуска
        скриптов для парсинга информации с различных
        web-ресурсов"""

    # Старая версия. Это скоро пропадёт
    # @staticmethod
    # def _clear_events():
    #     delete_query = delete(AllEvents).where(getattr(AllEvents, "parser") == parser_name)
    #
    #     session.execute(delete_query)
    #
    #     # Подтверждаем изменения
    #     session.commit()

    @staticmethod
    async def _clear_events(session: AsyncSession):

        payload = {
            'parser': parser_name
        }
        r = await session.post('http://188.120.244.63:8000/clear_events/', json=payload)
        logger.debug(f'request for clear: {r.status_code}')

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
            await self._clear_events(script.session) # Берем сессию, созданную в классе Parser
            try:
                await script.main()  # Запускаем async def main в parser.py
            except AttributeError as e:
                logger.error(f'parser down with error: {e}')
                return

            logger.info(f'the script {parser_name} has successfully completed its work')
            if script.session is not None:
                await script.session.close()


class Parser(Controller):
    def __init__(self):
        super().__init__()

        # self.session: AsyncSession = AsyncSession()
        self.session: AsyncProxySession = AsyncProxySession()
        self.name = ''

    async def register_event(
            self,
            event_name: str,
            link: str,
            date: datetime,
            venue: str = None):

        event_name = event_name.replace('\n', ' ')
        if venue is not None:
            venue = venue.replace('\n', ' ')

        parser = parser_name

        log_time_format = '%Y-%m-%d %H:%M:%S'
        normal_date = datetime.strftime(date, log_time_format)

        new_event = {
            "name": event_name,
            "link": link,
            "parser": parser,
            "date": normal_date,
            "venue": venue
        }

        r = await self.session.post('http://188.120.244.63:8000/put_event/', json=new_event)
        if r.status_code != 200:
            logger.error(f"the request to the allocator ended with the code: {r.status_code}")
