import y
from tests.fixtures import async_test, optimism_only


@async_test
@optimism_only
async def test_wtbt():
    """
    Test the price of the WTBT token at a specific block on the Optimism network.

    This test checks the price of the WTBT token using the :func:`y.get_price` function
    with the `skip_cache` parameter set to `True`, ensuring that the price is fetched
    directly without using any cached values.

    The test is marked to run only on the Optimism network and is executed asynchronously.

    See Also:
        - :func:`y.get_price`
    """
    assert (
        await y.get_price(
            "0xdb4eA87fF83eB1c80b8976FC47731Da6a31D35e5",
            106500000,
            skip_cache=True,
            sync=False,
        )
        == 1.0009538615847542
    )


@async_test
@optimism_only
async def test_mseth():
    """
    Test the price of the MSETH token at a specific block on the Optimism network.

    This test checks the price of the MSETH token using the :func:`y.get_price` function
    with the `skip_cache` parameter set to `True`, ensuring that the price is fetched
    directly without using any cached values.

    The test is marked to run only on the Optimism network and is executed asynchronously.

    See Also:
        - :func:`y.get_price`
    """
    assert (
        await y.get_price(
            "0x1610e3c85dd44Af31eD7f33a63642012Dca0C5A5",
            106500000,
            skip_cache=True,
            sync=False,
        )
        == 1909.2991854198503
    )
