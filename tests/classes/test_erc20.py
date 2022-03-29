import pytest
from brownie import chain
from tests.fixtures import blocks_for_contract, mutate_token
from y.classes.common import ERC20
from y.networks import Network

ATOKENS = {
    Network.Mainnet: [
        "0xfC1E690f61EFd961294b3e1Ce3313fBD8aa4f85d",
        "0x4DA9b813057D04BAef4e5800E36083717b4a0341",
        "0x9bA00D6856a4eDF4665BcA2C2309936572473B7E",
        "0x71fc860F7D3A592A4a98740e39dB31d25db65ae8",
        "0x625aE63000f46200499120B906716420bd059240",
        "0xE1BA0FB44CCb0D11b80F92f4f8Ed94CA3fF51D00",
        "0x3a3A65aAb0dd2A17E3F1947bA16138cd37d08c04",
        "0x9D91BE44C06d373a8a226E1f3b146956083803eB",
        "0x7deB5e830be29F91E298ba5FF1356BB7f8146998",
        "0x6Ee0f7BB50a54AB5253dA0667B0Dc2ee526C30a8",
        "0x12e51E77DAAA58aA0E9247db7510Ea4B46F9bEAd",
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
        "0xc9BC48c72154ef3e5425641a3c747242112a46AF",
        "0x1E6bb68Acec8fefBD87D192bE09bb274170a0548",
        "0x2e8F4bdbE3d47d7d7DE490437AeA9915D930F1A3",
        "0x6F634c6135D2EBD550000ac92F494F9CB8183dAe",
        "0xd4937682df3C8aEF4FE912A96A74121C0829E664",
        "0x683923dB55Fead99A79Fa01A27EeC3cB19679cC3",
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
        "0x0A6172fb19E85DBae18898eA2f7a596B5681f1eE",
    ]
}.get(chain.id, [])

ATOKENS = [mutation for token in ATOKENS for mutation in mutate_token(token)]

@pytest.mark.parametrize('token',ATOKENS)
def test_erc20(token):
    token = ERC20(token)
    assert token.contract, f'Cannot fetch contract for token {token}'
    assert token.build_name, f'Cannot fetch build name for token {token}'
    assert token.symbol, f'Cannot fetch symbol for token {token}'
    assert token.name, f'Cannot fetch name for token {token}'
    assert token.decimals, f'Cannot fetch decimals for token {token}'
    assert token.scale, f'Cannot fetch scale for token {token}'
    assert 10 ** token.decimals == token.scale, f'Incorrect scale fetched for token {token}'
    assert token.total_supply() is not None, f'Cannot fetch total supply for token {token}'
    assert token.total_supply_readable() is not None, f'Cannot fetch total supply readable for token {token}'
    assert token.total_supply() / token.scale == token.total_supply_readable(), f'Incorrect total supply readable for token {token}'
    assert token.price(), f'Cannot fetch price for token {token}'

    for block in blocks_for_contract(token.address):
        assert token._decimals(block), f'Cannot fetch decimals for token {token}'
        assert token._scale(block), f'Cannot fetch scale for token {token}'
        assert token.total_supply(block) is not None, f'Cannot fetch total supply for token {token}'
        assert token.total_supply_readable(block) is not None, f'Cannot fetch total supply readable for token {token}'
        assert token.total_supply(block) / token._scale(block) == token.total_supply_readable(block), f'Incorrect total supply readable for token {token}'
        assert token.price(block), f'Cannot fetch price for token {token}'
