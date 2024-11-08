from decimal import Decimal

from tests.fixtures import mainnet_only
from y.prices.gearbox import gearbox
import pytest

ddai = "0x6CFaF95457d7688022FC53e7AbE052ef8DFBbdBA"


@mainnet_only
@pytest.mark.asyncio_cooperative
async def test_is_dtoken():
    assert await gearbox.is_diesel_token(ddai) is True


@mainnet_only
@pytest.mark.asyncio_cooperative
async def test_get_price():
    assert await gearbox.get_price(ddai, 16980000) == Decimal("1.007850150784062913")
