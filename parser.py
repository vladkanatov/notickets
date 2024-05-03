from datamining.module.controller import Parser
from datamining.module.logger import logger
from bs4 import BeautifulSoup

import json
from datetime import datetime

class Template(Parser):

    def __init__(self):
        super().__init__()
    
    @staticmethod
    def str_to_datetime(time_str: str) -> datetime:
        try:
            # Получаем текущую дату
            current_date = datetime.now()
            
            # Получаем текущий год
            year = current_date.year
            
            # Пытаемся разобрать строку времени в формате HH:MM
            dt = datetime.strptime(f"{year} {time_str}", "%Y %H:%M")
            return dt
        except ValueError:
            return None

    async def main(self):
        
        r = await self.session.get('https://hamovniki.theater/')
        # logger.debug(r.text)
        logger.debug(r.status_code)
        
        soup = BeautifulSoup(r.text, 'lxml')
        
        events = soup.find_all('div', class_='row show_border')  

        for event in events:
            title = event.find('a', class_='tkt22')
            if title:
                title_text = title.text.strip()  # Убираем лишние пробелы
            else:
                title_text = "Заголовок не найден"
        
            link = 'https://hamovniki.theater' + event.find('a')['href']
            time = event.find('div', class_ ="showtime").find('span')
            
            dt = self.str_to_datetime(time.text)
            
            logger.debug(title.text)
            logger.debug(link)
            logger.debug(dt)