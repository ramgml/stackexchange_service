import aiohttp
from .dto import SearchResponse

DEFAULT_FILTER = '!9_bDE.BDp'


class StackexchangeException(Exception):
    pass


class StackExchange:
    base_url = 'https://api.stackexchange.com/2.2'

    @classmethod
    async def search(cls, intitle, page=1, pagesize=25, sort=None, order=None, filter_=DEFAULT_FILTER):
        params = {
            'site': 'stackoverflow',
            'intitle': intitle,
            'page': page,
            'pagesize': pagesize,
            'sort': sort,
            'order': order,
            'filter': filter_
        }
        params = {key: value for key,
                  value in params.items() if value is not None}

        async with aiohttp.ClientSession() as session:
            async with session.get(f'{cls.base_url}/search', params=params) as response:
                if response.status != 200:
                    raise StackexchangeException(response.reason, await response.text())

                return SearchResponse(await response.json())
