from stackexchange_client import client


async def test_search():
    response = await client.search(
        intitle='python',
        page=1,
        pagesize=25,
        sort='creation',
        order='desc',
        filter_='!9_bDE.BDp'
    )
    assert response.items is not None
