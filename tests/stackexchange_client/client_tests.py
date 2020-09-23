from stackexchange_client.client import StackExchange


async def test_search():
    response = await StackExchange.search(
        intitle='python',
        page=1,
        pagesize=25,
        sort='creation',
        order='desc',
        filter_='!9_bDE.BDp'
    )
    assert response.items is not None
