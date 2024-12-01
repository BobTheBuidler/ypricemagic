from tests.fixtures import async_test, mainnet_only
from y import get_price
from y.datatypes import UsdPrice


@async_test
@mainnet_only
async def test_balancer_v2_pool_price():
    """
    Test the price of a Balancer V2 pool.

    This test checks the price of a specific Balancer V2 pool, identified by its address,
    at a given block number. The expected price is compared against the actual price
    obtained using the :func:`y.get_price` function.

    The pool being tested is a 50/50 WETH/USDC pool.

    See Also:
        - :func:`y.get_price`

    """
    v2_weighted_pool = "0x96646936b91d6B9D7D0c47C496AfBF3D6ec7B6f8"  # 50/50 WETH/USDC
    assert await get_price(
        v2_weighted_pool, 14_000_000, skip_cache=True, sync=False
    ) == UsdPrice(62.35369906899849)


@async_test
@mainnet_only
async def test_balancer_v2_token_price():
    """
    Test the price of a Balancer V2 token.

    This test checks the price of a specific Balancer V2 token, identified by its address,
    at a given block number. The expected price is compared against the actual price
    obtained using the :func:`y.get_price` function.

    See Also:
        - :func:`y.get_price`

    """
    v2_token = "0x616e8BfA43F920657B3497DBf40D6b1A02D4608d"
    assert await get_price(
        v2_token, 17_500_000, skip_cache=True, sync=False
    ) == UsdPrice(12.522495269157522)
