
from brownie import chain
from y import Network

FAKE_TOKENS = {
    Network.Mainnet: [
        "0xB1D75F4Fb67c7e93f05890f5eEAC2F3884991FF9", # fake weth
        "0x224e13dF4b4DbF41820ec848B19bB6f015F8bf7b", # fake musd
        "0x719A75aa3Dc05DEF57Be2F3eC0f4098475631D1c", # fake mta
    ],
    Network.Fantom: [
        "0x1B27A9dE6a775F98aaA5B90B62a4e2A0B84DbDd9", # fake usdt
        "0x6E0aA9718C56Ef5d19ccf57955284C7CD95737be", # fake boo
        "0x6F73abe13c58A616fDBd454089e30A806c27Cee2", # fake lqdr
    ]
}.get(chain.id, [])
