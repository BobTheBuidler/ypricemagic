
import pytest
from brownie import chain
from tests.fixtures import blocks_for_contract, mutate_addresses
from y.networks import Network
from y.prices import abracadabra
from y.constants import WRAPPED_GAS_COIN

ABRACADABRAS = {
    # NOTE: from https://docs.abracadabra.money/our-ecosystem/our-contracts
    Network.Mainnet: [
        '0x7b7473a76D6ae86CE19f7352A1E89F6C9dc39020',
        '0x05500e2Ee779329698DF35760bEdcAAC046e7C27',
        '0x003d5A75d284824Af736df51933be522DE9Eed0f',
        '0x98a84EfF6e008c5ed0289655CcdCa899bcb6B99F',
        '0xEBfDe87310dc22404d918058FAa4D56DC4E93f0A',
        '0x0BCa8ebcB26502b013493Bf8fE53aA2B1ED401C1',
        '0x920D9BD936Da4eAFb5E25c6bDC9f6CB528953F9f',
        '0x4EAeD76C3A388f4a841E9c765560BBe7B3E4B3A0',
        '0x252dCf1B621Cc53bc22C256255d2bE5C8c32EaE4',
        '0x35a0Dd182E4bCa59d5931eae13D0A2332fA30321',
        '0xc1879bf24917ebE531FbAA20b0D05Da027B592ce',
        '0x9617b633EF905860D919b88E1d9d9a6191795341',
        '0xCfc571f3203756319c231d3Bc643Cee807E74636',
        '0x3410297D89dCDAf4072B805EFc1ef701Bb3dd9BF',
        '0x59e9082e068ddb27fc5ef1690f9a9f22b32e573f',
        '0x257101F20cB7243E2c7129773eD5dBBcef8B34E0',
        '0x390Db10e65b5ab920C19149C919D970ad9d18A41',
        '0x5ec47EE69BEde0b6C2A2fC0D9d094dF16C192498'
    ],
    Network.Fantom: [
        '0x8E45Af6743422e488aFAcDad842cE75A09eaEd34',
        '0xd4357d43545F793101b592bACaB89943DC89d11b',
        '0xed745b045f9495B8bfC7b58eeA8E0d0597884e12',
        '0xa3Fc1B4b7f06c2391f7AD7D4795C1cD28A59917e'
    ],
    Network.Avalanche: [
        '0x3CFEd0439aB822530b1fFBd19536d897EF30D2a2',
        '0x3b63f81Ad1fc724E44330b4cf5b5B6e355AD964B',
        '0x95cCe62C3eCD9A33090bBf8a9eAC50b699B54210',
        '0x35fA7A723B3B39f15623Ff1Eb26D8701E7D6bB21',
        '0x0a1e6a80E93e62Bd0D3D3BFcF4c362C40FB1cF3D',
        '0x2450Bf8e625e98e14884355205af6F97E3E68d07',
        '0xAcc6821d0F368b02d223158F8aDA4824dA9f28E3'
    ],
    Network.Arbitrum: [
        '0xC89958B03A55B5de2221aCB25B58B89A000215E6'
    ],
    Network.BinanceSmartChain: [ 
        '0xF8049467F3A9D50176f4816b20cDdd9bB8a93319',
        '0x692CF15F80415D83E8c0e139cAbcDA67fcc12C90'
    ]
}.get(chain.id, [])

ABRACADABRAS = mutate_addresses(ABRACADABRAS)

@pytest.mark.parametrize('token',ABRACADABRAS)
def test_abracadabra_get_price(token):
    assert abracadabra.is_cauldron(token), 'Abracadabra cauldron not recognized.'
    blocks = blocks_for_contract(token, 10)
    for block in blocks:
        assert abracadabra.get_price(token, block), 'Failed to fetch price.'

def test_non_abracadabra():
    assert not abracadabra.is_cauldron(WRAPPED_GAS_COIN), 'Token incorrectly recognized as Abracadabra cauldron.'
    with pytest.raises(TypeError):
        abracadabra.get_price(WRAPPED_GAS_COIN)
