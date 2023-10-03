import pytest
from brownie import ZERO_ADDRESS, chain
from tests.fixtures import mainnet_only
from y.contracts import contract_creation_block_async
from y.networks import Network
from y.prices.chainlink import FEEDS, chainlink

feeds = set(FEEDS.keys())
feeds.update({
    # Add feeds that *should* come from registry
    Network.Mainnet: [
        "0x0000000000000000000000000000000000000024",
        "0x000000000000000000000000000000000000007c",
        "0x000000000000000000000000000000000000009c",
        "0x0000000000000000000000000000000000000164",
        "0x0000000000000000000000000000000000000188",
        "0x000000000000000000000000000000000000019a",
        "0x000000000000000000000000000000000000022A",
        "0x0000000000000000000000000000000000000236",
        "0x0000000000000000000000000000000000000260",
        #"0x0000000000000000000000000000000000000283", chainlink feed disabled at block 14673916 - 0xd1898776f4f2333c26c170b58ec98430d29c224a81256fd70add5db05a036b20
        "0x00000000000000000000000000000000000002be",
        "0x00000000000000000000000000000000000002c6",
        "0x00000000000000000000000000000000000002F4",
        "0x000000000000000000000000000000000000033a",
        "0x00000000000000000000000000000000000003d2",
        "0x00000000000000000000000000000000000003Da",
        "0x0bc529c00C6401aEF6D220BE8C6Ea1667F6Ad93e",
        "0x0D8775F648430679A709E98d2b0Cb6250d2887EF",
        "0x111111111117dC0aa78b770fA6A738034120C302",
        "0x1776e1F26f98b1A5dF9cD347953a26dd3Cb46671",
        "0x1F573D6Fb3F13d689FF844B4cE37794d79a7FF1C",
        "0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984",
        "0x221657776846890989a759BA2973e427DfF5C9bB",
        "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599",
        "0x3155BA85D5F96b2d030a4966AF206230e46849cb",
        "0x33D0568941C0C64ff7e0FB4fbA0B11BD37deEd9f",
        "0x3432B6A60D23Ca0dFCa7761B7ab56459D9C964D0",
        "0x3472A5A71965499acd81997a54BBA8D852C6E53d",
        "0x3845badAde8e6dFF049820680d1F14bD3903a5d0",
        "0x408e41876cCCDC0F92210600ef50372656052a38",
        "0x4575f41308EC1483f3d399aa9a2826d74Da13Deb",
        "0x4688a8b1F292FDaB17E9a90c8Bc379dC1DBd8713",
        "0x4C19596f5aAfF459fA38B0f7eD92F11AE6543784",
        "0x4Fabb145d64652a948d72533023f6E7A623C7C53",
        "0x514910771AF9Ca656af840dff83E8264EcF986CA",
        "0x57Ab1ec28D129707052df4dF418D58a2D46d5f51",
        "0x584bC13c7D411c00c01A62e8019472dE68768430",
        "0x674C6Ad92Fd080e4004b2312b45f796a192D27a0",
        "0x6B175474E89094C44Da98b954EedeAC495271d0F",
        "0x6B3595068778DD592e39A122f4f5a5cF09C90fE2",
        "0x6f259637dcD74C767781E37Bc6133cd6A68aa161",
        "0x75231F58b43240C9718Dd58B4967c5114342a86c",
        "0x7D1AfA7B718fb893dB30A3aBc0Cfc608AaCfeBB0",
        "0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9",
        "0x8290333ceF9e6D528dD5618Fb97a76f268f3EDD4",
        "0x84cA8bc7997272c7CfB4D0Cd3D55cd942B3c9419",
        "0x8Ab7404063Ec4DBcfd4598215992DC3F8EC853d7",
        "0x8CE9137d39326AD0cD6491fb5CC0CbA0e089b6A9",
        "0x967da4048cD07aB37855c090aAF366e4ce1b9F48",
        "0x9f8F72aA9304c8B593d555F12eF6589cC3A579A2",
        "0xA0b73E1Ff0B80914AB6fe0444E65848C4C34450b",
        "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
        "0xa3BeD4E1c75D00fa6f4E5E6922DB7261B5E9AcD2",
        "0xA9B1Eb5908CfC3cdf91F9B8B3a74108598009096",
        "0xADE00C28244d5CE17D72E40330B1c318cD12B7c3",
        "0xBA11D00c5f74255f56a5E366F4F77f5A186d7f55",
        "0xbBbBBBBbbBBBbbbBbbBbbbbBBbBbbbbBbBbbBBbB",
        "0xBBbbCA6A901c926F240b89EacB641d8Aec7AEafD",
        "0xbE9375C6a420D2eEB258962efB95551A5b722803",
        "0xc00e94Cb662C3520282E6f5717214004A7f26888",
        "0xC011a73ee8576Fb46F5E1c5751cA3B9Fe0af2a6F",
        "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
        "0xc12eCeE46ed65D970EE5C899FCC7AE133AfF9b03",
        "0xC581b735A1688071A1746c968e0798D642EDE491",
        "0xcB3df3108635932D912632ef7132d03EcFC39080",
        "0xd26114cd6EE289AccF82350c8d8487fedB8A0C07",
        "0xD46bA6D942050d489DBd938a2C909A5d5039A161",
        "0xD533a949740bb3306d119CC777fa900bA034cd52",
        "0xD71eCFF9342A5Ced620049e616c5035F1dB98620",
        "0xdAC17F958D2ee523a2206206994597C13D831ec7",
        "0xdB25f211AB05b1c97D595516F45794528a807ad8",
        "0xdd974D5C2e2928deA5F71b9825b8b646686BD200",
        "0xe1aFe1Fd76Fd88f78cBf599ea1846231B8bA3B6B",
        "0xe28b3B32B6c345A34Ff64674606124Dd5Aceca30",
        "0xE41d2489571d322189246DaFA5ebDe1F4699F498",
        "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",
        "0xf8C3527CC04340b208C854E985240c02F7B7793f",
        "0xfF20817765cB7f73d4bde2e66e067E58D11095C2",
    ],
    Network.Fantom: [
        '0x21be370D5312f44cB42ce377BC9b8a0cEF1A4C83',
        '0x321162Cd933E2Be498Cd2267a90534A804051b11',
        '0x2406dCe4dA5aB125A18295f4fB9FD36a0f7879A2',
        '0x74b23882a30290451A17c44f4F05243b6b58C76d',
        '0xBDC8fd437C489Ca3c6DA3B5a336D11532a532303',
        '0xd6070ae98b8069de6B494332d1A1a81B6179D960',
        '0x1E4F97b9f9F913c46F1632781732927B9019C68b',
        '0x6a07A792ab2965C72a5B8088d3a069A7aC3a993B',
        '0x657A1861c15A3deD9AF0B6799a195a249ebdCbc6',
        '0xb3654dc3D10Ea7645f8319668E8F54d2574FBdC8',
        '0x399fe752D39338d28C36F3370fbebd8292fb9E6e',
        '0x56ee926bD8c72B2d5fa1aF4d9E4Cbb515a1E3Adc',
        '0x468003B688943977e6130F4F68F23aad939a1040',
        '0xae75A438b2E0cB8Bb01Ec1E1e376De11D44477CC',
        '0x81740D647493a61329E1c574A11ee7577659fb14',
        '0xe105621721D1293c27be7718e041a4Ce0EbB227E',
        '0x29b0Da86e484E1C0029B56e817912d778aC0EC69',
    ],
}.get(chain.id, []))
FEEDS = list(feeds)


@pytest.mark.parametrize('token', FEEDS)
def test_chainlink_get_feed(token):
    """
    Tests `chainlink.get_feed` with both lowercase address and checksum address.
    """
    assert chainlink.get_feed(token, sync=True) != ZERO_ADDRESS, 'no feed available'


@pytest.mark.parametrize('token', FEEDS)
@pytest.mark.asyncio_cooperative
async def test_chainlink_latest(token):
    if not await chainlink.get_price(token):
        feed = await chainlink.get_feed(token)
        assert await feed.contract.aggregator.coroutine() == ZERO_ADDRESS, 'no current price available'


@mainnet_only
@pytest.mark.parametrize('token', FEEDS)
@pytest.mark.asyncio_cooperative
async def test_chainlink_before_registry(token):
    test_block = 12800000
    assert chainlink.asynchronous is True
    feed = await chainlink.get_feed(token, sync=False)
    if await contract_creation_block_async(feed.address) > test_block:
        pytest.skip('not applicable to feeds deployed after test block')
    print(type(chainlink.get_price))
    price = chainlink.get_price(token, block=test_block)
    price = await price
    if not price:
        feed = await chainlink.get_feed(token)
        assert await feed.contract.aggregator.coroutine() == ZERO_ADDRESS, 'no price available before registry'


def test_chainlink_nonexistent():
    with pytest.raises(KeyError):
        chainlink.get_feed(ZERO_ADDRESS, sync=True)
    assert chainlink.get_price(ZERO_ADDRESS, sync=True) is None


@mainnet_only
def test_chainlink_before_feed():
    # try to fetch yfi price one block before feed is deployed
    assert chainlink.get_price('0x0bc529c00C6401aEF6D220BE8C6Ea1667F6Ad93e', 12742718, sync=True) is None
