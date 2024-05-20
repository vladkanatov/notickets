from datamining.module.controller import Parser
from datamining.module.logger import logger
from bs4 import BeautifulSoup

import json
from datetime import datetime


class Template(Parser):

    def __init__(self):
        super().__init__()

    async def main(self):

        r = await self.session.get('https://bkz.ru/')
        
        logger.debug(r.text)
        
        soup = BeautifulSoup(r.text, 'lxml')
        
        blocks = soup.find_all('div', class_='section1__month')
        
        for block in block:
            hrefs = block.find_all('a')


        logger.debug(r.text)
