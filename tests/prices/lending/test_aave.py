import pytest
from brownie import chain
from multicall.utils import await_awaitable

from tests.fixtures import mainnet_only
from y.networks import Network
from y.prices.lending.aave import AaveRegistry

aDAI = "0x028171bCA77440897B824Ca71D1c56caC55b68A3"
DAI = "0x6B175474E89094C44Da98b954EedeAC495271d0F"

ATOKENS = {
    Network.Mainnet: [
        "0xfC1E690f61EFd961294b3e1Ce3313fBD8aa4f85d",
        "0x4DA9b813057D04BAef4e5800E36083717b4a0341",
        "0x9bA00D6856a4eDF4665BcA2C2309936572473B7E",
        "0x71fc860F7D3A592A4a98740e39dB31d25db65ae8",
        "0x625aE63000f46200499120B906716420bd059240",
        "0x7D2D3688Df45Ce7C552E19c27e007673da9204B8",
        "0xE1BA0FB44CCb0D11b80F92f4f8Ed94CA3fF51D00",
        "0x3a3A65aAb0dd2A17E3F1947bA16138cd37d08c04",
        "0xA64BD6C70Cb9051F6A9ba1F163Fdc07E0DfB5F84",
        "0x9D91BE44C06d373a8a226E1f3b146956083803eB",
        "0x71010A9D003445aC60C4e6A7017c1E89A477B438",
        "0x7deB5e830be29F91E298ba5FF1356BB7f8146998",
        "0x6FCE4A401B6B80ACe52baAefE4421Bd188e76F6f",
        "0x6Fb0855c404E09c47C3fBCA25f08d4E41f9F062f",
        "0x328C4c80BC7aCa0834Db37e6600A6c49E12Da4DE",
        "0xFC4B8ED459e00e5400be803A9BB3954234FD50e3",
        "0x6Ee0f7BB50a54AB5253dA0667B0Dc2ee526C30a8",
        "0x712DB54daA836B53Ef1EcBb9c6ba3b9Efb073F40",
        "0x69948cC03f478B95283F7dbf1CE764d0fc7EC54C",
        "0x12e51E77DAAA58aA0E9247db7510Ea4B46F9bEAd",
        "0xba3D9687Cf50fE253cd2e1cFeEdE1d6787344Ed5",
        "0xB124541127A0A657f056D9Dd06188c4F1b0e5aab",
        "0x3Ed3B47Dd13EC9a98b44e6204A523E766B225811",
        "0x9ff58f4fFB29fA2266Ab25e75e2A8b3503311656",
        "0x030bA81f1c18d280636F32af80b9AAd02Cf0854e",
        "0x5165d24277cD063F5ac44Efd447B27025e888f37",
        "0xDf7FF54aAcAcbFf42dfe29DD6144A69b629f8C9e",
        "0xB9D7CB55f463405CDfBe4E90a6D2Df01C2B92BF1",
        "0xFFC97d72E13E01096502Cb8Eb52dEe56f74DAD7B",
        "0x05Ec93c0365baAeAbF7AefFb0972ea7ECdD39CF1",
        "0xA361718326c15715591c299427c62086F69923D9",
        "0x028171bCA77440897B824Ca71D1c56caC55b68A3",
        "0xaC6Df26a590F08dcC95D5a4705ae8abbc88509Ef",
        "0x39C6b3e42d6A679d7D776778Fe880BC9487C2EDA",
        "0xa06bC25B5805d5F8d82847D191Cb4Af5A3e873E0",
        "0xa685a61171bb30d4072B338c80Cb7b2c865c873E",
        "0xc713e5E149D5D0715DcD1c156a020976e7E56B88",
        "0xCC12AbE4ff81c9378D670De1b57F8e0Dd228D77a",
        "0x35f6B052C598d933D69A4EEC4D04c73A191fE6c2",
        "0x6C5024Cd4F8A59110119C56f8933403A539555EB",
        "0x101cc05f4A51C0319f570d5E146a8C625198e636",
        "0xBcca60bB61934080951369a648Fb03DF4F96263C",
        "0x8dAE6Cb04688C62d939ed9B68d32Bc62e49970b1",
        "0xD37EE7e4f452C6638c96536e68090De8cBcdb583",
        "0x272F97b7a56a387aE942350bBC7Df5700f8a4576",
        "0xF256CC7847E919FAc9B808cC216cAc87CCF2f47a",
        "0x514cd6756CCBe28772d4Cb81bC3156BA9d1744aa",
        "0xc9BC48c72154ef3e5425641a3c747242112a46AF",
        "0x1E6bb68Acec8fefBD87D192bE09bb274170a0548",
        "0x2e8F4bdbE3d47d7d7DE490437AeA9915D930F1A3",
        "0x6F634c6135D2EBD550000ac92F494F9CB8183dAe",
        "0xd4937682df3C8aEF4FE912A96A74121C0829E664",
        "0x683923dB55Fead99A79Fa01A27EeC3cB19679cC3",
        "0x1982b2F5814301d4e9a8b0201555376e62F82428",
        "0x9a14e23A58edf4EFDcB360f68cd1b95ce2081a2F",
        "0xc2e2152647F4C26028482Efaf64b2Aa28779EFC4",
        "0xf9Fb4AD91812b704Ba883B11d2B576E890a6730A",
        "0x79bE75FFC64DD58e66787E4Eae470c8a1FD08ba4",
        "0xd24946147829DEaA935bE2aD85A3291dbf109c80",
        "0x17a79792Fe6fE5C95dFE95Fe3fCEE3CAf4fE4Cb7",
        "0x13B2f6928D7204328b0E8E4BCd0379aA06EA21FA",
        "0x9303EabC860a743aABcc3A1629014CaBcc3F8D36",
        "0xc58F53A8adff2fB4eb16ED56635772075E2EE123",
        "0xe59d2FF6995a926A574390824a657eEd36801E55",
        "0xA1B0edF4460CC4d8bFAA18Ed871bFF15E5b57Eb4",
        "0xE340B25fE32B1011616bb8EC495A4d503e322177",
        "0x0ea20e7fFB006d4Cfe84df2F72d8c7bD89247DB0",
        "0xb8db81B84d30E2387de0FF330420A4AAA6688134",
        "0x370adc71f67f581158Dc56f539dF5F399128Ddf9",
        "0xA9e201A4e269d6cd5E9F0FcbcB78520cf815878B",
        "0x38E491A71291CD43E8DE63b7253E482622184894",
        "0x3D26dcd840fCC8e4B2193AcE8A092e4a65832F9f",
        "0x391E86e2C002C70dEe155eAceB88F7A3c38f5976",
        "0x2365a4890eD8965E564B7E2D27C38Ba67Fec4C6F",
        "0x5394794Be8b6eD5572FCd6b27103F46b5F390E8f",
        "0x358bD0d980E031E23ebA9AA793926857703783BD",
        "0xd109b2A304587569c84308c55465cd9fF0317bFB",
        "0xd145c6ae8931ed5Bca9b5f5B7dA5991F5aB63B5c",
        "0xCa5DFDABBfFD58cfD49A9f78Ca52eC8e0591a3C5",
        "0x2394eAc76A0B7992FB8aa0F0C126317Af76Ae707",
        "0x0EDf29d931b68D673bdCDD35B20e26eEC0532F25",
        "0x762E5982EB0D944A9800D7caBAF640464E892C91",
        "0x50D695cf7a86cFe415642cBCb25B025a9B1597e7",
        "0x0A6172fb19E85DBae18898eA2f7a596B5681f1eE",
    ]
}.get(chain.id, [])

supported_chains = pytest.mark.skipif(
    not (AaveRegistry(asynchronous=False).pools or ATOKENS),
    reason="Not applicable on chains without known Aaves or forks",
)


@mainnet_only
def test_adai():
    """
    Simple test for a known underlying.

    This test verifies that the underlying asset of a known aToken (aDAI) is correctly identified as DAI.

    See Also:
        - :func:`AaveRegistry.underlying`
    """
    assert AaveRegistry(asynchronous=False).underlying(aDAI) == DAI
    assert await_awaitable(AaveRegistry(asynchronous=True).underlying(aDAI)) == DAI


@supported_chains
def test_AaveRegistry():
    """
    Test the AaveRegistry for pool and aToken availability.

    This test checks that the AaveRegistry can fetch pools and that the `ATOKENS` constant is set up correctly.

    See Also:
        - :class:`AaveRegistry`
    """
    aave = AaveRegistry()
    assert aave.pools, f"Cannot fetch Aave pools on {Network.printable()}"
    assert (
        ATOKENS
    ), f"Please set up `ATOKENS` constant to test Aave on {Network.printable()}"
    for pool in aave.pools:
        assert pool.atokens, f"Cannot find atokens for Aave pool {pool}"


@pytest.mark.parametrize("token", ATOKENS)
@pytest.mark.asyncio_cooperative
async def test_atokens_async(token):
    """
    Test various functions related to aTokens asynchronously.

    This test verifies the following functions:
    - :meth:`AaveRegistry.is_atoken`
    - :meth:`AaveRegistry.pool_for_atoken`
    - :meth:`AaveRegistry.underlying`
    - :meth:`AaveRegistry.get_price`

    Args:
        token: The aToken address to test.

    See Also:
        - :class:`AaveRegistry`
    """
    aave = AaveRegistry(asynchronous=True)
    with pytest.raises(RuntimeError):
        assert token in aave, f"Cannot find atoken {token} in AaveRegistry."

    assert await aave.is_atoken(token), f"Cannot validate atoken {token} as an atoken."
    assert await aave.pool_for_atoken(token), f"Cannot find pool for atoken {token}"
    underlying = await aave.underlying(token)
    assert underlying, f"Cannot find underlying for atoken {token}"
    assert await aave.get_price(token), f"Cannot find price for atoken {token}"


@pytest.mark.asyncio_cooperative
async def test_wrapped_atoken_v2():
    """
    Test for wrapped aToken v2 pricing.

    This test checks if a wrapped aToken v2 is correctly identified and priced.

    See Also:
        - :meth:`AaveRegistry.is_wrapped_atoken_v2`
        - :meth:`AaveRegistry.get_price_wrapped_v2`
    """
    wrapped_ausdt = "0xf8Fd466F12e236f4c96F7Cce6c79EAdB819abF58"
    aave: AaveRegistry = AaveRegistry(asynchronous=True)
    assert await aave.is_wrapped_atoken_v2(wrapped_ausdt)
    assert await aave.get_price_wrapped_v2(wrapped_ausdt, block=17_000_000) == 1.112026


@pytest.mark.asyncio_cooperative
async def test_wrapped_atoken_v3():
    """
    Test for wrapped aToken v3 pricing.

    This test checks if a wrapped aToken v3 is correctly identified and priced.

    See Also:
        - :meth:`AaveRegistry.is_wrapped_atoken_v3`
        - :meth:`AaveRegistry.get_price_wrapped_v3`
    """
    wrapped_ausdc = "0x57d20c946A7A3812a7225B881CdcD8431D23431C"
    aave: AaveRegistry = AaveRegistry(asynchronous=True)
    assert await aave.is_wrapped_atoken_v3(wrapped_ausdc)
    assert await aave.get_price_wrapped_v3(wrapped_ausdc, block=17_000_000) == 1.000168
