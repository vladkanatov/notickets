from datamining.proxy.get import get_proxies
from datetime import datetime, timedelta
from datamining.logger import logger
import random


class ProxyManager:
    def __init__(self):
        self.proxies = self.load_proxies()
        self.last_used_proxy = None

    @staticmethod
    def load_proxies():
        # Загрузка прокси из базы данных или другого источника
        proxies = get_proxies()
        # Устанавливаем текущее время для каждого прокси в поле last_used
        for proxy in proxies:
            proxy['last_used'] = datetime.now()
        return proxies

    def get_least_used_proxy(self):
        if not self.proxies:
            logger.warning('proxy did not load!')

        if self.last_used_proxy is None:
            return self.proxies[0]

        current_time = datetime.now()

        least_used_proxy = min(
            (proxy for proxy in self.proxies if proxy != self.last_used_proxy),
            key=lambda proxy: proxy.get('last_used', datetime.min)
        )

        least_used_time = least_used_proxy.get('last_used', datetime.min)
        if (current_time - least_used_time) > timedelta(seconds=15):  # Assuming 15 seconds threshold for least used
            return least_used_proxy
        else:
            # If the least used proxy has been used recently, return a random one
            return self.get_random()

    def get_random(self):
        return random.choice(self.proxies)

    def update_last_used(self, proxy):
        # Обновляем информацию о последнем использовании прокси
        proxy['last_used'] = datetime.now()
        self.last_used_proxy = proxy
