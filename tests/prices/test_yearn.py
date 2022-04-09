
from tests.fixtures import mainnet_only
from y.classes.common import ERC20
from y.constants import usdc
from y.prices.yearn import YearnInspiredVault


@mainnet_only
def test_share_price_yearn_v1():
    yusdc_v1 = '0xa2609B2b43AC0F5EbE27deB944d2a399C201E3dA'
    block = 14_500_000
    assert YearnInspiredVault(yusdc_v1).share_price(block) == 1.111974132096754

@mainnet_only
def test_underlying_yearn_v1():
    yusdc_v1 = '0xa2609B2b43AC0F5EbE27deB944d2a399C201E3dA'
    assert YearnInspiredVault(yusdc_v1).underlying == ERC20(usdc)

@mainnet_only
def test_share_price_yearn_v2():
    yvusdc_v2 = '0x5f18c75abdae578b483e5f43f12a39cf75b973a9'
    block = 14_500_000
    assert YearnInspiredVault(yvusdc_v2).share_price(block) == 1.096431

@mainnet_only
def test_underlying_yearn_v2():
    yvusdc_v2 = '0x5f18c75abdae578b483e5f43f12a39cf75b973a9'
    assert YearnInspiredVault(yvusdc_v2).underlying == ERC20(usdc)
