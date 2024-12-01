import a_sync
import pytest
from brownie import chain

from tests.fixtures import blocks_for_contract
from y.constants import WRAPPED_GAS_COIN
from y.networks import Network
from y.prices import popsicle

POPSICLES = {
    Network.Mainnet: [
        "0xa7053782dC3523D2C82B439Acf3f9344Fb47b97f",
        "0xd2C5A739ebfE3E00CFa88A51749d367d7c496CCf",
        "0x949FDF28F437258E7564a35596b1A99b24F81e4e",
        "0xa0273C10b8A4BF0bDC57cb0bC974E3A9d89527b8",
        "0x495410B129A27bC771ce8fb316d804a5686B8Ea7",
        "0x5C08A6762CAF9ec8a42F249eBC23aAE66097218D",
        "0xaE7b92C8B14E7bdB523408aE0A6fFbf3f589adD9",
        "0x9683D433621A83aA7dd290106e1da85251317F55",
        "0x212Aa024E25A9C9bAF5b5397B558B7ccea81740B",
        "0xBE5d1d15617879B22C7b6a8e1e16aDD6d0bE3c61",
        "0xFF338D347E59d6B61E5C69382915D863bb22Ef2f",
        "0xa1BE64Bb138f2B6BCC2fBeCb14c3901b63943d0E",
        "0x8d8B490fCe6Ca1A31752E7cFAFa954Bf30eB7EE2",
        "0x989442D5cCB27E7931095B0f3165c75a6def9bc3",
        "0xbA38029806AbE4B45D5273098137DDb52dA8e62F",
        "0xd2EF15af2649CC46e3E23B96563a3d44ef5E5A06",
        "0xF4f542E4b5E2345A1f2D0fEab9492357Ebc5c8f4",
        "0x36e9B6e7FADC7b8Ee289c8A24Ad96573cda3D7D9",
    ],
    Network.Polygon: [
        "0x5C08A6762CAF9ec8a42F249eBC23aAE66097218D",
        "0xaE7b92C8B14E7bdB523408aE0A6fFbf3f589adD9",
        "0xa0273C10b8A4BF0bDC57cb0bC974E3A9d89527b8",
        "0x949FDF28F437258E7564a35596b1A99b24F81e4e",
        "0x9683D433621A83aA7dd290106e1da85251317F55",
        "0xd2C5A739ebfE3E00CFa88A51749d367d7c496CCf",
        "0xa7053782dC3523D2C82B439Acf3f9344Fb47b97f",
    ],
}.get(chain.id, [])


def test_non_popsicle():
    """Test that a non-Popsicle LP token is not incorrectly identified as a Popsicle LP.

    This test checks that the `WRAPPED_GAS_COIN` is not recognized as a Popsicle LP token
    and that attempting to get its price raises a `TypeError`.

    See Also:
        - :func:`popsicle.is_popsicle_lp`
        - :func:`popsicle.get_price`
    """
    assert not popsicle.is_popsicle_lp(
        WRAPPED_GAS_COIN
    ), "Token incorrectly recognized as Popsicle LP."
    with pytest.raises(TypeError):
        popsicle.get_price(WRAPPED_GAS_COIN)


@pytest.mark.asyncio_cooperative
@pytest.mark.parametrize("token", POPSICLES)
async def test_popsicle_get_price(token):
    """Test fetching the price of Popsicle LP tokens.

    This test verifies that each token in the `POPSICLES` list is correctly identified
    as a Popsicle LP and that its price can be fetched for various blocks.

    Args:
        token: The Popsicle LP token address to test.

    See Also:
        - :func:`popsicle.is_popsicle_lp`
        - :func:`popsicle.get_price`
        - :func:`blocks_for_contract`
    """
    assert await popsicle.is_popsicle_lp(
        token, sync=False
    ), "Popsicle LP not recognized."
    blocks = blocks_for_contract(token, 25)
    async for block, price in a_sync.map(popsicle.get_price, blocks, token=token):
        assert price, f"Failed to fetch price for {token} at block {block}."
