from datamining.module.controller import Parser
from datamining.module.logger import logger
from bs4 import BeautifulSoup


class Kek(Parser):
    def __init__(self):
        super().__init__()

    async def main(self):
        response = await self.session.get('https://mossoveta.ru/timetable/')

        soup = BeautifulSoup(response.text, 'lxml')

        divs = soup.find_all('div', class_='title')

        for div in divs:
            logger.debug(div.text)

