from datamining.module.controller import Parser
from datamining.module.logger import logger
from bs4 import BeautifulSoup
from datetime import datetime


class ParserName(Parser):
    def __init__(self):
        super().__init__()

    @staticmethod
    def str_to_datetime(date_str, time_str, month):
        # Распаковываем значения из строки даты
        day, day_of_week = date_str.split(',')
        day = int(day.strip())
        day_of_week = day_of_week.strip()

        # Распаковываем значения из строки времени
        hour, minute = map(int, time_str.split(':'))

        # Создаем объект datetime
        dt = datetime(year=2024, month=month, day=day, hour=hour, minute=minute)
        
        return dt

    async def main(self):

        r = await self.session.get('https://mxat.ru/timetable/')
        logger.info(f'request end with code: {r.status_code}')
        
        soup = BeautifulSoup(r.text, 'lxml')

        events = soup.find_all('div', class_='event')

        date_str = ''

        for event in events:
            if 'first' in event.get('class', []):
                date_str = event.find('div', class_='dt').text

            title = event.find('a').text.replace(', (состав)', '').replace('\xa0', '').replace('\xa011', '')
            link = 'https://mxat.ru' + event.find('a')['href']
            time = event.find('span', class_='tm').text

            date = self.str_to_datetime(date_str, time, 4)

            await self.register_event(title, link, date, venue='МХТ им. Чехова')

            logger.debug((title, link, date, 'МХТ им. Чехова'))
            
        
