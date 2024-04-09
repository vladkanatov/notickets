from datamining.module.proxy.get import get_proxies
from datetime import datetime


class ProxyManager:
    def __init__(self):
        self.proxies = get_proxies()
        self.last_used_proxy = None

    def get_least_used_proxy(self):
        if not self.proxies:
            raise ValueError("No proxies loaded")

        # Если last_used_proxy не установлен, выбираем первый прокси из списка
        if self.last_used_proxy is None:
            return self.proxies[0]

        # Возвращаем прокси, которое было использовано давнее всех остальных
        least_used_proxy = min(self.proxies, key=lambda proxy: proxy.get('last_used', datetime.min))
        return least_used_proxy

    @staticmethod
    def update_last_used(proxy):
        # Обновляем информацию о последнем использовании прокси
        proxy['last_used'] = datetime.now()
