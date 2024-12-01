from brownie import chain
from y import Network

FAKE_TOKENS = {
    Network.Mainnet: [
        "0xB1D75F4Fb67c7e93f05890f5eEAC2F3884991FF9",  # fake weth
        "0xcD545222eBf01143c1188bF712ee5e89c4278Afa",  # fake dai
        "0x6B2751Cd339217B2CAeD3485fc7a92256681053F",  # fake tusd
        "0x224e13dF4b4DbF41820ec848B19bB6f015F8bf7b",  # fake musd
        "0x719A75aa3Dc05DEF57Be2F3eC0f4098475631D1c",  # fake mta
    ],
    Network.Fantom: [
        "0x1B27A9dE6a775F98aaA5B90B62a4e2A0B84DbDd9",  # fake usdt
        "0x6E0aA9718C56Ef5d19ccf57955284C7CD95737be",  # fake boo
        "0x6F73abe13c58A616fDBd454089e30A806c27Cee2",  # fake lqdr
    ],
}.get(chain.id, [])

"""
FAKE_TOKENS is a dictionary that maps network identifiers to lists of fake token addresses.

This dictionary is used to provide a set of fake token addresses for different blockchain networks. 
The keys are network identifiers from the :class:`~y.networks.Network` enum, and the values are lists of 
fake token addresses represented as strings.

Examples:
    >>> from y.utils.fakes import FAKE_TOKENS
    >>> FAKE_TOKENS[Network.Mainnet]
    ['0xB1D75F4Fb67c7e93f05890f5eEAC2F3884991FF9', '0xcD545222eBf01143c1188bF712ee5e89c4278Afa', ...]

    >>> FAKE_TOKENS[Network.Fantom]
    ['0x1B27A9dE6a775F98aaA5B90B62a4e2A0B84DbDd9', '0x6E0aA9718C56Ef5d19ccf57955284C7CD95737be', ...]

See Also:
    - :class:`~y.networks.Network` for network ID definitions.
    - :mod:`brownie` for blockchain interaction.
"""
