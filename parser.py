from datetime import datetime
from typing import Optional
from bs4 import BeautifulSoup

from datamining.module.controller import Parser
from datamining.module.logger import logger


class Bileter(Parser):
    def __init__(self):
        super().__init__()
        # Имя парсера
        self.name = 'bileter_ru'

        self.delay = 1800
        self.driver_source = None
        self.headers = {
            'authority': 'www.bileter.ru',
            'accept': 'text/html, */*; q=0.01',
            'accept-language': 'ru,en;q=0.9',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'referer': 'https://www.bileter.ru/afisha',
            'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "YaBrowser";v="23"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Linux"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': self.user_agent,
            'x-pjax': 'true',
            'x-pjax-container': '#js_id_afisha_performances_grid',
            'x-requested-with': 'XMLHttpRequest',
        }
        self.urls = [
            # Москва
            'https://msk.bileter.ru/afisha?building[]=1930_moscow.html',

            # СПБ
            # 'https://www.bileter.ru/afisha?building[]=aleksandrinskiy_teatr.html', # Александрийский театр
            # 'https://www.bileter.ru/afisha?building[]=bolshoy_dramaticheskiy_teatr_imgatovstonogova.html', # БДТ Товстогонова
            'https://www.bileter.ru/afisha?building[]=dom_ofitserov.html',  # Дом офицеров
            'https://www.bileter.ru/afisha?building[]=bolshoy_kontsertnyiy_zal_oktyabrskiy.html'  # БКЗ "Октябрьский"
        ]

    @staticmethod
    def reformat_venue(venue: str) -> Optional[str]:
        return {
            'Александрийский театр': 'Александрийский театр!'
        }.get(venue, None)

    @staticmethod
    def month_string_to_number(month):
        return {
            'Января': 1, 'Февраля': 2, 'Марта': 3, 'Апреля': 4,
            'Мая': 5, 'Июня': 6, 'Июля': 7, 'Августа': 8,
            'Сентября': 9, 'Октября': 10, 'Ноября': 11, 'Декабря': 12
        }[month]

    def str_to_datetime(self, date: str) -> datetime:
        date_parts = date.split()
        # Извлекаем день, месяц и время
        day = date_parts[0]
        if "Открытая дата" in date:  # Если точной даты не существуеты
            return None
        day = int(day)
        month_string = date_parts[1].replace(',', '')
        month_number = self.month_string_to_number(month_string)
        time = date_parts[-1]
        year = date_parts[-2].replace(',', '')
        if month_string == year:  # Если не указан год
            year = datetime.now().year
        # Собираем все в datetime объект
        final_date = datetime(year=int(year), month=month_number, day=day, hour=int(time.split(':')[0]),
                              minute=int(time.split(':')[1]))
        return final_date

    def get_date(self, event: BeautifulSoup):
        date = event.find('div', class_='date').text
        datetime_date = self.str_to_datetime(date)
        return datetime_date

    @staticmethod
    def get_link(event: BeautifulSoup) -> str:
        price_block = event.find('div', class_='price')
        link = "https://www.bileter.ru" + price_block.find('a')['href']
        return link

    def get_date_from_list(self, event: BeautifulSoup) -> datetime:
        date_and_price = event.find('a')
        date = date_and_price.contents[0]
        datetime_date = self.str_to_datetime(date)
        return datetime_date

    @staticmethod
    def get_link_from_list(event: BeautifulSoup) -> str:
        return "https://www.bileter.ru" + event.find('a')['href']

    async def put_db(self, events: list[tuple]) -> None:
        for event in events:
            logger.debug(event)
            await self.register_event(
                event_name=event[0],
                link=event[1],
                date=event[2],
                venue=event[3],
                image_link=event[4]
            )

    async def main(self):

        r = await self.session.get('https://bkz.ru/afisha/')
        logger.debug(r.status_code)
        # logger.debug(r.text)
        
        soup = BeautifulSoup(r.text, 'lxml')
     
        events = soup.find_all('div', class_='section1__month')
        
        for event in events:
            containers = event.find_all('a')
            
            for container in containers:
                title = container.find('img', class_='playbill-el-img-mobile')['alt']
                image_link = container.find('img', class_='playbill-el-img-mobile')['data-src']
                link = 'https://bkz.ru/afisha' + container['href']
                time = container.find('div', class_='playbill-el-text-date')
                
                if time:
                    full_text = time.text.strip()

                    # Разделяем строку на дату и время
                    if ' в ' in full_text:
                        date_part, time_part = full_text.split(' в ')
                        date_str = date_part.strip()
                        time_str = time_part.strip()

                        dt = self.convert_to_datetime(date_str, time_str)
                        
                        # logger.debug(title)
                        # logger.debug(link)
                        # logger.debug(dt)
                        await self.register_event(title, link, dt, 'Большой концертный зал "Октябрьский"')