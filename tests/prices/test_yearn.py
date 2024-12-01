import pytest

from tests.fixtures import mainnet_only
from y.classes.common import ERC20
from y.constants import usdc
from y.prices.yearn import YearnInspiredVault

"""
These tests are written in a synchronous style using pytest. They verify the correctness of the 
YearnInspiredVault class methods when called in a synchronous context. The tests ensure that the 
YearnInspiredVault methods return expected results for given inputs, specifically focusing on 
share price and underlying asset retrieval for Yearn vaults.
"""


@mainnet_only
def test_share_price_yearn_v1():
    """Test the share price of a Yearn v1 vault."""
    yusdc_v1 = "0xa2609B2b43AC0F5EbE27deB944d2a399C201E3dA"
    block = 14_500_000
    assert YearnInspiredVault(yusdc_v1).share_price(block) == 1.111974132096754


@mainnet_only
def test_underlying_yearn_v1():
    """Test the underlying asset of a Yearn v1 vault."""
    yusdc_v1 = "0xa2609B2b43AC0F5EbE27deB944d2a399C201E3dA"
    assert YearnInspiredVault(yusdc_v1).underlying == ERC20(usdc)


@mainnet_only
def test_share_price_yearn_v2():
    """Test the share price of a Yearn v2 vault."""
    yvusdc_v2 = "0x5f18c75abdae578b483e5f43f12a39cf75b973a9"
    block = 14_500_000
    assert YearnInspiredVault(yvusdc_v2).share_price(block) == 1.096431


@mainnet_only
def test_underlying_yearn_v2():
    """Test the underlying asset of a Yearn v2 vault."""
    yvusdc_v2 = "0x5f18c75abdae578b483e5f43f12a39cf75b973a9"
    assert YearnInspiredVault(yvusdc_v2).underlying == ERC20(usdc)
