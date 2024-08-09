import json
import aiohttp
from aiohttp import ClientResponse, BasicAuth
from aiohttp.typedefs import StrOrURL, JSONDecoder
from typing import Any, Optional
from datamining.proxy.manager import ProxyManager

class AwaitedResponse:

    def __init__(self,
                 response: ClientResponse,
                 content: bytes):
        self.request_info = response.request_info
        self.history = response.history
        self.encoding = response.get_encoding()
        self.content = content
        self.headers = response.headers
        self.status_code = response.status
        self.url = str(response.url)
        self.url_parsed = response.url
        self.ok = response.ok
        self.raw_headers = response.raw_headers
        self.real_url = response.real_url
        self.closed = response.closed
        self.charset = response.charset
        self.content_disposition = response.content_disposition
        self.content_type = response.content_type
        self.content_length = response.content_length
        self.connection = response.connection
        self.text = self.content.decode(self.encoding)  # type: ignore[no-any-return,union-attr]

    def json(self,
             encoding: Optional[str] = None,
             loads: JSONDecoder = json.loads):
        if encoding:
            stripped = self.content.strip()
            decoded = stripped.decode(encoding)
            return loads(decoded)
        else:
            stripped = self.text.strip()
            return loads(stripped)


class AsyncSession(aiohttp.ClientSession):
    # semaphores_on_ip = defaultdict(lambda: asyncio.Semaphore(3))

    def __init__(self):
        super().__init__()

    # def __repr__(self):
    #     return f'<[{self.bot.name}] AsyncProxySession>'

    @property
    def cookies(self):
        return super().cookie_jar

    # async def _request(self, method, url, *args, **kwargs):
    #     # Preparing parameters
    #     str_proxy = self.bot.proxy.async_proxy
    #     kwargs['proxy'] = str_proxy
    #     kwargs['proxy_auth'] = self.bot.proxy.async_proxy_auth
    #     if 'verify' in kwargs:
    #         kwargs['ssl'] = kwargs.pop('verify')
    #
    #     # Spreading
    #     if not self.bot.spreading:
    #         return await super()._request(url, *args, **kwargs)
    #     domain = urlparse(url).netloc
    #     await_key = (domain, str_proxy,)
    #     semaphore = self.semaphores_on_ip[await_key]
    #
    #     await semaphore.acquire()
    #     await self.global_semaphore.acquire()
    #     global in_process
    #     try:
    #         in_process += 1
    #         # logger.debug('aiohttp', in_process)
    #         return await super()._request(method, url, *args, **kwargs)
    #     finally:
    #         in_process -= 1
    #         # logger.debug('aiohttp', in_process)
    #         semaphore.release()
    #         self.global_semaphore.release()

    @staticmethod
    async def _static_response(method, *args, **kwargs):
        response: ClientResponse
        async with method(*args, **kwargs) as response:
            content = await response.read()
            return AwaitedResponse(response, content)

    async def get(self, url: StrOrURL, allow_redirects: bool = True, **kwargs: Any) -> AwaitedResponse:
        """Perform HTTP GET request"""
        return await self._static_response(super().get, url, allow_redirects=allow_redirects, **kwargs)

    async def options(self, url: StrOrURL, allow_redirects: bool = True, **kwargs: Any) -> AwaitedResponse:
        """Perform HTTP OPTIONS request"""
        return await self._static_response(super().options, url, allow_redirects=allow_redirects, **kwargs)

    async def head(self, url: StrOrURL, allow_redirects: bool = False, **kwargs: Any) -> AwaitedResponse:
        """Perform HTTP HEAD request"""
        return await self._static_response(super().head, url, allow_redirects=allow_redirects, **kwargs)

    async def post(self, url: StrOrURL, data: Any = None, **kwargs: Any) -> AwaitedResponse:
        """Perform HTTP POST request"""
        return await self._static_response(super().post, url, data=data, **kwargs)

    async def put(self, url: StrOrURL, data: Any = None, **kwargs: Any) -> AwaitedResponse:
        """Perform HTTP PUT request"""
        return await self._static_response(super().put, url, data=data, **kwargs)

    async def patch(self, url: StrOrURL, data: Any = None, **kwargs: Any) -> AwaitedResponse:
        """Perform HTTP PATCH request"""
        return await self._static_response(super().patch, url, data=data, **kwargs)

    async def delete(self, url: StrOrURL, **kwargs: Any) -> AwaitedResponse:
        """Perform HTTP DELETE request"""
        return await self._static_response(super().delete, url, **kwargs)

    def get_with(self, url: StrOrURL, allow_redirects: bool = True, **kwargs: Any):
        """Perform HTTP GET request with ``with`` constructor"""
        return super().get(url, allow_redirects=allow_redirects, **kwargs)

    def options_with(self, url: StrOrURL, allow_redirects: bool = True, **kwargs: Any):
        """Perform HTTP OPTIONS request with ``with`` constructor"""
        return super().options(url, allow_redirects=allow_redirects, **kwargs)

    def head_with(self, url: StrOrURL, allow_redirects: bool = False, **kwargs: Any):
        """Perform HTTP HEAD request with ``with`` constructor"""
        return super().head(url, allow_redirects=allow_redirects, **kwargs)

    def post_with(self, url: StrOrURL, data: Any = None, **kwargs: Any):
        """Perform HTTP POST request with ``with`` constructor"""
        return super().post(url, data=data, **kwargs)

    def put_with(self, url: StrOrURL, data: Any = None, **kwargs: Any):
        """Perform HTTP PUT request with ``with`` constructor"""
        return super().put(url, data=data, **kwargs)

    def patch_with(self, url: StrOrURL, data: Any = None, **kwargs: Any):
        """Perform HTTP PATCH request with ``with`` constructor"""
        return super().patch(url, data=data, **kwargs)

    def delete_with(self, url: StrOrURL, **kwargs: Any):
        """Perform HTTP DELETE request with ``with`` constructor"""
        return super().delete(url, **kwargs)


class AsyncProxySession(aiohttp.ClientSession):
    def __init__(self):
        super().__init__()
        self.proxy_manager = ProxyManager()

    # def __repr__(self):
    #     return f'<[{self.bot.name}] AsyncProxySession>'

    @property
    def cookies(self):
        return super().cookie_jar

    async def _request(self, url, *args, **kwargs):
        # Preparing parameters
        proxy = self.proxy_manager.get_least_used_proxy()
        proxy_str = f'http://{proxy["ip"]}:{proxy["port"]}'
        proxy_auth = BasicAuth(proxy['login'], proxy['password'])
        kwargs['proxy'] = proxy_str
        kwargs['proxy_auth'] = proxy_auth
        if 'verify' in kwargs:
            kwargs['ssl'] = kwargs.pop('verify')
        self.proxy_manager.update_last_used(proxy)

        return await super()._request(url, *args, **kwargs)

    @staticmethod
    async def _static_response(method, *args, **kwargs):
        response: ClientResponse
        async with method(*args, **kwargs) as response:
            content = await response.read()
            return AwaitedResponse(response, content)

    async def get(self, url: StrOrURL, allow_redirects: bool = True, **kwargs: Any) -> AwaitedResponse:
        """Perform HTTP GET request"""
        return await self._static_response(super().get, url, allow_redirects=allow_redirects, **kwargs)

    async def options(self, url: StrOrURL, allow_redirects: bool = True, **kwargs: Any) -> AwaitedResponse:
        """Perform HTTP OPTIONS request"""
        return await self._static_response(super().options, url, allow_redirects=allow_redirects, **kwargs)

    async def head(self, url: StrOrURL, allow_redirects: bool = False, **kwargs: Any) -> AwaitedResponse:
        """Perform HTTP HEAD request"""
        return await self._static_response(super().head, url, allow_redirects=allow_redirects, **kwargs)

    async def post(self, url: StrOrURL, data: Any = None, **kwargs: Any) -> AwaitedResponse:
        """Perform HTTP POST request"""
        return await self._static_response(super().post, url, data=data, **kwargs)

    async def put(self, url: StrOrURL, data: Any = None, **kwargs: Any) -> AwaitedResponse:
        """Perform HTTP PUT request"""
        return await self._static_response(super().put, url, data=data, **kwargs)

    async def patch(self, url: StrOrURL, data: Any = None, **kwargs: Any) -> AwaitedResponse:
        """Perform HTTP PATCH request"""
        return await self._static_response(super().patch, url, data=data, **kwargs)

    async def delete(self, url: StrOrURL, **kwargs: Any) -> AwaitedResponse:
        """Perform HTTP DELETE request"""
        return await self._static_response(super().delete, url, **kwargs)

    def get_with(self, url: StrOrURL, allow_redirects: bool = True, **kwargs: Any):
        """Perform HTTP GET request with ``with`` constructor"""
        return super().get(url, allow_redirects=allow_redirects, **kwargs)

    def options_with(self, url: StrOrURL, allow_redirects: bool = True, **kwargs: Any):
        """Perform HTTP OPTIONS request with ``with`` constructor"""
        return super().options(url, allow_redirects=allow_redirects, **kwargs)

    def head_with(self, url: StrOrURL, allow_redirects: bool = False, **kwargs: Any):
        """Perform HTTP HEAD request with ``with`` constructor"""
        return super().head(url, allow_redirects=allow_redirects, **kwargs)

    def post_with(self, url: StrOrURL, data: Any = None, **kwargs: Any):
        """Perform HTTP POST request with ``with`` constructor"""
        return super().post(url, data=data, **kwargs)

    def put_with(self, url: StrOrURL, data: Any = None, **kwargs: Any):
        """Perform HTTP PUT request with ``with`` constructor"""
        return super().put(url, data=data, **kwargs)

    def patch_with(self, url: StrOrURL, data: Any = None, **kwargs: Any):
        """Perform HTTP PATCH request with ``with`` constructor"""
        return super().patch(url, data=data, **kwargs)

    def delete_with(self, url: StrOrURL, **kwargs: Any):
        """Perform HTTP DELETE request with ``with`` constructor"""
        return super().delete(url, **kwargs)