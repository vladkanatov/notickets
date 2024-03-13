from bs4 import BeautifulSoup
from datamining.module.controller import Parser
from datamining.module.logger import logger


class Ticketland(Parser):
    
    def __init__(self):
        super().__init__()

        self.url = 'https://www.ticketland.ru/teatry/'
        self.our_places_data = {
            'https://sochi.ticketland.ru/teatry/': [
                # 'zimniy-teatr-sochi',
            ],
            'https://spb.ticketland.ru/teatry/': [
                #  'aleksandrinskiy-teatr',
                #  'bdt-imtovstonogova',
                 #'kamennoostrovskiy-teatr',
                #  'mikhaylovskiy-teatr',
            ],
            'https://www.ticketland.ru/teatry/': [
                #'teatr-lenkom',
                # 'mkht-im-chekhova',
                #'mkhat-im-m-gorkogo',
                # 'malyy-teatr',
                # 'teatr-imeni-evgeniya-vakhtangova',
                # 'simonovskaya-scena-teatra-imeni-evgeniya-vakhtangova',
                #'teatr-satiry',
                #'teatr-operetty',
                # 'masterskaya-p-fomenko',
                #'gosudarstvennyy-teatr-naciy',
                # 'teatr-ugolok-dedushki-durova',
                #'moskovskiy-teatr-sovremennik',
                #'teatr-rossiyskoy-armii',
                #'teatr-im-vl-mayakovskogo',
                #'teatr-im-nvgogolya',
                #'teatr-im-ermolovoy',
                # 'ramt'
            ],
            'https://www.ticketland.ru/cirki/': [
                #'bolshoy-moskovskiy-cirk',
            ],
            'https://www.ticketland.ru/drugoe/': [
                #'mts-live-kholl-moskva',
            ],
            'https://www.ticketland.ru/koncertnye-zaly/': [
                # 'gosudarstvennyy-kremlevskiy-dvorec',
            ],
            'https://www.ticketland.ru/vystavochnye-centry/': [
              #  'vdnh',
            ],
            
            'https://www.ticketland.ru/kluby/': [
                "klub-1930"
            ]
        }

    async def get_events(self, link, places_url, venue):
        events = []
        number_page = 0
        achtung = False
        while not achtung:
            if 'bdt-imtovstonogova' in link:
                add_link = link + f'LoadBuildingCrossPopularJS/?page={number_page}&dateStart=0&dateEnd=0&dateRangeCode=default'
            else:
                add_link = link + f'LoadBuildingPopularJS/?page={number_page}&dateStart=0&dateEnd=0&dateRangeCode=default'
            headers = {
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,'
                          'image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'ru,en;q=0.9',
                'cache-control': 'max-age=0',
                'connection': 'keep-alive',
                'host': 'www.ticketland.ru',
                'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108", "Yandex";v="23"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'none',
                'sec-fetch-user': '?1',
                'upgrade-insecure-requests': '1',
                'user-agent': self.user_agent
            }
            if 'spb' in link:
                headers['host'] = 'spb.ticketland.ru'
            elif 'sochi' in places_url:
                headers['host'] = 'sochi.ticketland.ru'

            r = await self.session.get(add_link, headers=headers)
            soup = BeautifulSoup(r.text, "lxml")
            cards = soup.find_all('div', class_='col')
            achtung = 'На выбранную дату нет мероприятий' in r.text
            for card in cards:
                href = card.find('a', class_='card__image-link').get('href')
                link_ = link.split('w')[0] + places_url.split('/')[2] + href
                for event in await self.get_cards(link_, venue):
                    events.append(event)
            number_page += 1
        return events

    async def get_cards(self, url, venue):
        collected = []
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'ru,en;q=0.9',
            'cache-control': 'max-age=0',
            'connection': 'keep-alive',
            'host': 'www.ticketland.ru',
            'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108", "Yandex";v="23"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': self.user_agent
        }
        old_url = None
        if 'spb' in url:
            headers['host'] = 'spb.ticketland.ru'
            old_url = 'spb'
            url = '/'.join(url.split('/')[-3:])
            url = 'https://spb.ticketland.ru/teatry/' + url
        elif 'sochi' in url:
            headers['host'] = 'sochi.ticketland.ru'
            old_url = 'sochi'
            url = '/'.join(url.split('/')[-3:])
            url = 'https://sochi.ticketland.ru/teatry/' + url

        r = await self.session.get(url, headers=headers)
        # time.sleep(1)

        soup = BeautifulSoup(r.text, 'lxml')
        cards1 = soup.find_all('article', class_='show-card')
        cards2 = soup.find_all('article', class_='show-card--active')
        cards = cards1 + cards2
        list_btn = []
        for card in cards:
            dm, year = card.find_all(class_='show-card__dm')
            event_name = card.find('meta')['content'].replace("'", '"')
            if venue == 'Михайловский театр':
                scene = card.find('span', class_='show-card__hall').text.strip()
                if not self.filter_events_from_mikhailovsky(event_name, scene):
                    continue
            day, month = dm.get_text().strip().split(' ')
            year = year.get_text().strip()
            month = month[:3].capitalize()
            time_ = card.find(class_='show-card__t').get_text().strip()
            formatted_date = f'{day} {month} {year} {time_}'
            btn = card.find(class_='btn btn--primary')
            if btn is None or btn in list_btn:
                continue
            list_btn.append(btn)
            url = btn['href']
            if old_url == 'spb':
                url = 'https://spb.ticketland.ru' + url
            elif 'sochi' == old_url:
                url = 'https://sochi.ticketland.ru' + url
            else:
                url = 'https://www.ticketland.ru' + url
            card_ = [event_name, url, formatted_date]
            collected.append(card_)
        return collected

    async def get_links_teatrs(self, pagecount, places_url, our_places):
        links_venues = []
        for p in range(1, int(pagecount) + 1):
            api = places_url + f"?page={p}&tab=all"
            headers = {
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,'
                          'image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'ru,en;q=0.9',
                'cache-control': 'max-age=0',
                'connection': 'keep-alive',
                'host': 'www.ticketland.ru',
                'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108", "Yandex";v="23"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'none',
                'sec-fetch-user': '?1',
                'upgrade-insecure-requests': '1',
                'user-agent': self.user_agent
            }
            if 'spb' in places_url:
                headers['host'] = 'spb.ticketland.ru'
            elif 'sochi' in places_url:
                headers['host'] = 'sochi.ticketland.ru'

            r = await self.session.get(api, headers=headers)
            soup = BeautifulSoup(r.text, 'lxml')
            items = soup.find_all('div', class_='card-search')
            for item in items:
                link_src = item.find('a', class_='card-search__name')
                venue = link_src.text.strip()
                url_parts = places_url.split('/')
                link = url_parts[0] + '//' + url_parts[2] + link_src.get('href')
                links_venues.append((link, venue))

        our_links_venues = {}
        for our_place in our_places:
            for link, venue in links_venues:
                if venue == 'Большой Московский цирк':
                    venue = 'Цирк на Вернадского'
                if our_place in link:
                    our_links_venues[link] = venue
        return our_links_venues

    # def request_to_ticketland(self, url, headers=None):
    #     r = requests.get(url, headers=headers)
    #     r_text = r.text
    #     if '<div id="id_spinner" class="container"><div class="load">Loading...</div>' in r_text:
    #         raise Exception('Запрос с загрузкой')
    #     return r_text

    async def main(self):
        for places_url, our_places in self.our_places_data.items():
            headers = {
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'ru,en;q=0.9',
                'cache-control': 'max-age=0',
                'connection': 'keep-alive',
                'host': 'www.ticketland.ru',
                'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108", "Yandex";v="23"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'none',
                'sec-fetch-user': '?1',
                'upgrade-insecure-requests': '1',
                'user-agent': self.user_agent
            }
            if 'spb' in places_url:
                headers['host'] = 'spb.ticketland.ru'
            elif 'sochi' in places_url:
                headers['host'] = 'sochi.ticketland.ru'

            r = await self.session.get(places_url, headers=headers)
            soup = BeautifulSoup(r.text, 'lxml')
            papers = soup.find_all('li', class_='search-pagination__item')
            if papers:
                last_paper = papers[-1]
                pagecount = last_paper.get('data-page-count')
            else:
                pagecount = 1
            teatr_links = await self.get_links_teatrs(pagecount, places_url, our_places)
            for link, venue in teatr_links.items():
                for event in await self.get_events(link, places_url, venue):
                    if 'gosudarstvennyy-kremlevskiy-dvorec' in our_places:
                        venue = 'Кремлёвский Дворец'
                        if 'kremlevskiy-dvorec/novogodnee-predstavlenie' not in event[1]:
                            continue
                    if len(event[1]) >= 200 or len(event[0]) >= 200:
                        logger.warning(event, venue, 'too long!!!!!!!!!!!!')
                        continue
                    logger.debug(event)
                    # self.register_event(event[0], event[1], date=event[2], venue=venue)

    def filter_events_from_mikhailovsky(self, title, scene):
        skip_event = [
            ['Лебединое озеро', 'Главный зал'],
            ['Щелкунчик', 'Главный зал'],
            ['Жизель', 'Главный зал'],
        ]
        if [title, scene] not in skip_event:
            return True
        return False
