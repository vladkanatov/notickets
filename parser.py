from datamining.module.controller import Parser
from datamining.module.logger import logger
from bs4 import BeautifulSoup

from datetime import datetime

class Template(Parser):

    def __init__(self):
        super().__init__()
        
    @staticmethod
    def convert_to_datetime(date_str: str, time_str: str) -> str:
        try:
            # Словарь для преобразования названий месяцев на русском в числовой формат
            month_names = {
                "января": "01",
                "февраля": "02",
                "марта": "03",
                "апреля": "04",
                "мая": "05",
                "июня": "06",
                "июля": "07",
                "августа": "08",
                "сентября": "09",
                "октября": "10",
                "ноября": "11",
                "декабря": "12"
            }

            # Разбиваем строку с датой на день и месяц
            day, month_name = date_str.split()
            
            # Преобразуем месяц в числовой формат
            month = month_names[month_name]
            
            # Получаем текущий год
            current_year = datetime.now().year
            
            # Собираем дату в формате ГГГГ-ММ-ДД
            date_formatted = f"{current_year}-{month}-{day.zfill(2)}"
            
            # Собираем полную дату и время
            datetime_formatted = f"{date_formatted} {time_str}"
            
            cleaned_string = datetime_formatted.split('\t')[0]

# Преобразуем строку в объект datetime
            datetime_obj = datetime.strptime(cleaned_string, '%Y-%m-%d %H:%M')
            
            return datetime_obj
        except ValueError as e:
            print(f"Ошибка преобразования даты и времени: {e}")
            return None

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