
import y
from tests.fixtures import async_test, optimism_only


@async_test
@optimism_only
async def test_wtbt():
    assert await y.get_price("0xdb4eA87fF83eB1c80b8976FC47731Da6a31D35e5", 106500000, sync=False) == 1.0009538615847542

@async_test
@optimism_only
async def test_mseth():
    assert await y.get_price("0x1610e3c85dd44Af31eD7f33a63642012Dca0C5A5", 106500000, sync=False) == 1909.2991854198503
