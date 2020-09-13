import aiohttp
from .dto import SearchResponse


BASE_URL = 'https://api.stackexchange.com/2.2'
DEFAULT_FILTER = '!9_bDE.BDp'


class StackexchangeException(Exception):
    pass


async def search(intitle, page=1, pagesize=25, sort=None, order=None, filter_=DEFAULT_FILTER):
    params = {
        'site': 'stackoverflow',
        'intitle': intitle,
        'page': page,
        'pagesize': pagesize,
        'sort': sort,
        'order': order,
        'filter': filter_
    }
    params = {key: value for key, value in params.items() if value is not None}

    async with aiohttp.ClientSession() as session:
        async with session.get(f'{BASE_URL}/search', params=params) as response:
            if response.status != 200:
                raise StackexchangeException(response.reason, await response.text())

            return SearchResponse(await response.json())
