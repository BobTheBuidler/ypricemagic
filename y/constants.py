# mypy: disable-error-code="dict-item"
from typing import Dict, Final, Optional

from brownie import Contract as _Contract
from brownie import chain
from eth_typing import ChecksumAddress

from y.contracts import Contract
from y.interfaces.ERC20 import ERC20ABI
from y.networks import Network


CHAINID: Final[int] = chain.id
"""
The chainid for the connected rpc.
"""

NETWORK_NAME: Final = Network.name(CHAINID)
"""
The name of the connected network.
"""

EEE_ADDRESS: Final[ChecksumAddress] = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"  # type: ignore [assignment]
"""
The address used to represent the native token (e.g., ETH on Ethereum, AVAX on Avalanche, etc.) in various DeFi protocols.
"""

weth: Contract

sushi: Optional[Contract] = None
"""
A placeholder for the Sushi token contract, which may be set depending on the network.
"""

if CONNECTED_TO_MAINNET := CHAINID == Network.Mainnet:
    weth = Contract("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2")
    """Wrapped Ether (WETH) contract on Ethereum Mainnet."""

    usdc = Contract("0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48")
    """USD Coin (USDC) contract on Ethereum Mainnet."""

    dai = Contract("0x6B175474E89094C44Da98b954EedeAC495271d0F")
    """Dai Stablecoin (DAI) contract on Ethereum Mainnet."""

    wbtc = Contract("0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599")
    """Wrapped Bitcoin (WBTC) contract on Ethereum Mainnet."""

    usdt = Contract("0xdAC17F958D2ee523a2206206994597C13D831ec7")
    """Tether USD (USDT) contract on Ethereum Mainnet."""

    sushi = Contract("0x6B3595068778DD592e39A122f4f5a5cF09C90fE2")
    """SushiToken (SUSHI) contract on Ethereum Mainnet."""

elif CHAINID == Network.BinanceSmartChain:
    weth = Contract("0x2170Ed0880ac9A755fd29B2688956BD959F933F8")
    """Wrapped Ether (WETH) contract on Binance Smart Chain."""

    usdc = Contract("0x8ac76a51cc950d9822d68b83fe1ad97b32cd580d")
    """USD Coin (USDC) contract on Binance Smart Chain."""

    dai = Contract("0x1af3f329e8be154074d8769d1ffa4ee058b1dbc3")
    """Dai Stablecoin (DAI) contract on Binance Smart Chain."""

    wbtc = Contract("0x2ccb7c8c51e55c2364b555ff6e6e3f7246499e16")
    """Wrapped Bitcoin (WBTC) contract on Binance Smart Chain."""

    usdt = Contract("0x55d398326f99059ff775485246999027b3197955")
    """Tether USD (USDT) contract on Binance Smart Chain."""

    wbnb = Contract("0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c")
    """Wrapped BNB (WBNB) contract on Binance Smart Chain."""

    cake = Contract("0x0e09fabb73bd3ade0a17ecc321fd13a19e81ce82")
    """PancakeSwap Token (CAKE) contract on Binance Smart Chain."""

elif CHAINID == Network.xDai:
    weth = Contract("0x6A023CCd1ff6F2045C3309768eAd9E68F978f6e1")
    """Wrapped Ether (WETH) contract on xDai Chain."""

    wbtc = Contract("0x8e5bBbb09Ed1ebdE8674Cda39A0c169401db4252")
    """Wrapped Bitcoin (WBTC) contract on xDai Chain."""

    dai = Contract("0x44fA8E6f47987339850636F88629646662444217")
    """Dai Stablecoin (DAI) contract on xDai Chain."""

    usdc = Contract("0xDDAfbb505ad214D7b80b1f830fcCc89B60fb7A83")
    """USD Coin (USDC) contract on xDai Chain."""

    usdt = Contract("0x4ECaBa5870353805a9F068101A40E0f32ed605C6")
    """Tether USD (USDT) contract on xDai Chain."""

elif CHAINID == Network.Polygon:
    weth = Contract("0x7ceb23fd6bc0add59e62ac25578270cff1b9f619")
    """Wrapped Ether (WETH) contract on Polygon."""

    usdc = Contract("0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174")
    """USD Coin (USDC) contract on Polygon."""

    dai = Contract("0x8f3Cf7ad23Cd3CaDbD9735AFf958023239c6A063")
    """Dai Stablecoin (DAI) contract on Polygon."""

    wbtc = Contract("0x1bfd67037b42cf73acf2047067bd4f2c47d9bfd6")
    """Wrapped Bitcoin (WBTC) contract on Polygon."""

    usdt = Contract("0xc2132D05D31c914a87C6611C10748AEb04B58e8F")
    """Tether USD (USDT) contract on Polygon."""

    wmatic = Contract("0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270")
    """Wrapped Matic (WMATIC) contract on Polygon."""

elif CHAINID == Network.Fantom:
    weth = Contract("0x74b23882a30290451A17c44f4F05243b6b58C76d")
    """Wrapped Ether (WETH) contract on Fantom."""

    usdc = Contract("0x04068DA6C83AFCFA0e13ba15A6696662335D5B75")
    """USD Coin (USDC) contract on Fantom."""

    dai = Contract("0x8D11eC38a3EB5E956B052f67Da8Bdc9bef8Abf3E")
    """Dai Stablecoin (DAI) contract on Fantom."""

    wbtc = Contract("0x321162Cd933E2Be498Cd2267a90534A804051b11")
    """Wrapped Bitcoin (WBTC) contract on Fantom."""

    usdt = Contract("0x049d68029688eAbF473097a2fC38ef61633A3C7A")  # fusdt
    """Fantom Tether USD (FUSDT) contract on Fantom."""

    wftm = Contract("0x21be370D5312f44cB42ce377BC9b8a0cEF1A4C83")
    """Wrapped Fantom (WFTM) contract on Fantom."""

elif CHAINID == Network.Arbitrum:
    weth = Contract("0x82aF49447D8a07e3bd95BD0d56f35241523fBab1")
    """Wrapped Ether (WETH) contract on Arbitrum."""
    # NOTE: for some reason wbtc unverified on arbi

    wbtc = _Contract.from_abi("wbtc", "0x2f2a2543B76A4166549F7aaB2e75Bef0aefC5B0f", ERC20ABI)
    """Wrapped Bitcoin (WBTC) contract on Arbitrum."""

    dai = Contract("0xDA10009cBd5D07dd0CeCc66161FC93D7c9000da1")
    """Dai Stablecoin (DAI) contract on Arbitrum."""

    usdc = Contract("0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8")
    """USD Coin (USDC) contract on Arbitrum."""

    usdt = Contract("0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9")
    """Tether USD (USDT) contract on Arbitrum."""

elif CHAINID == Network.Avalanche:
    weth = Contract("0x49D5c2BdFfac6CE2BFdB6640F4F80f226bc10bAB")  # weth.e
    """Wrapped Ether (WETH.e) contract on Avalanche."""

    wbtc = Contract("0x50b7545627a5162F82A992c33b87aDc75187B218")
    """Wrapped Bitcoin (WBTC) contract on Avalanche."""

    dai = Contract("0xd586E7F844cEa2F87f50152665BCbc2C279D8d70")
    """Dai Stablecoin (DAI) contract on Avalanche."""

    usdc = Contract("0xA7D7079b0FEaD91F3e65f86E8915Cb59c1a4C664")  # usdc.e
    """USD Coin (USDC.e) contract on Avalanche."""

    usdt = Contract("0x9702230A8Ea53601f5cD2dc00fDBc13d4dF4A8c7")
    """Tether USD (USDT) contract on Avalanche."""

elif CHAINID == Network.Moonriver:
    weth = Contract("0x639A647fbe20b6c8ac19E48E2de44ea792c62c5C")
    """Wrapped Ether (WETH) contract on Moonriver."""

    wbtc = Contract("0x6aB6d61428fde76768D7b45D8BFeec19c6eF91A8")
    """Wrapped Bitcoin (WBTC) contract on Moonriver."""

    dai = Contract("0x80A16016cC4A2E6a2CACA8a4a498b1699fF0f844")
    """Dai Stablecoin (DAI) contract on Moonriver."""

    usdc = Contract("0xE3F5a90F9cb311505cd691a46596599aA1A0AD7D")
    """USD Coin (USDC) contract on Moonriver."""

    usdt = Contract("0xB44a9B6905aF7c801311e8F4E76932ee959c663C")
    """Tether USD (USDT) contract on Moonriver."""

elif CHAINID == Network.Heco:
    weth = Contract("0x64FF637fB478863B7468bc97D30a5bF3A428a1fD")
    """Wrapped Ether (WETH) contract on HECO Chain."""

    wbtc = Contract("0x70D171d269D964d14aF9617858540061e7bE9EF1")
    """Wrapped Bitcoin (WBTC) contract on HECO Chain."""

    dai = Contract("0x3D760a45D0887DFD89A2F5385a236B29Cb46ED2a")
    """Dai Stablecoin (DAI) contract on HECO Chain."""

    usdc = Contract("0x9362Bbef4B8313A8Aa9f0c9808B80577Aa26B73B")
    """USD Coin (USDC) contract on HECO Chain."""

    usdt = Contract("0xa71EdC38d189767582C38A3145b5873052c3e47a")
    """Tether USD (USDT) contract on HECO Chain."""

elif CHAINID == Network.Harmony:
    weth = Contract("0x6983D1E6DEf3690C4d616b13597A09e6193EA013")
    """Wrapped Ether (WETH) contract on Harmony."""

    wbtc = Contract("0x3095c7557bCb296ccc6e363DE01b760bA031F2d9")
    """Wrapped Bitcoin (WBTC) contract on Harmony."""

    dai = Contract("0xEf977d2f931C1978Db5F6747666fa1eACB0d0339")
    """Dai Stablecoin (DAI) contract on Harmony."""

    usdc = Contract("0x985458E523dB3d53125813eD68c274899e9DfAb4")
    """USD Coin (USDC) contract on Harmony."""

    usdt = Contract("0x3C2B8Be99c50593081EAA2A724F0B8285F5aba8f")
    """Tether USD (USDT) contract on Harmony."""

elif CHAINID == Network.Aurora:
    weth = Contract("0xC9BdeEd33CD01541e1eeD10f90519d2C06Fe3feB")
    """Wrapped Ether (WETH) contract on Aurora."""

    wbtc = _Contract.from_abi(
        "ERC20 [forced]", "0xF4eB217Ba2454613b15dBdea6e5f22276410e89e", ERC20ABI
    )
    """Wrapped Bitcoin (WBTC) contract on Aurora."""

    dai = _Contract.from_abi(
        "ERC20 [forced]", "0xe3520349F477A5F6EB06107066048508498A291b", ERC20ABI
    )
    """Dai Stablecoin (DAI) contract on Aurora."""

    usdc = _Contract.from_abi(
        "ERC20 [forced]", "0xB12BFcA5A55806AaF64E99521918A4bf0fC40802", ERC20ABI
    )
    """USD Coin (USDC) contract on Aurora."""

    usdt = _Contract.from_abi(
        "ERC20 [forced]", "0x4988a896b1227218e4A686fdE5EabdcAbd91571f", ERC20ABI
    )
    """Tether USD (USDT) contract on Aurora."""

elif CHAINID == Network.Cronos:
    weth = Contract("0xe44Fd7fCb2b1581822D0c862B68222998a0c299a")
    """Wrapped Ether (WETH) contract on Cronos."""

    wbtc = Contract("0x062E66477Faf219F25D27dCED647BF57C3107d52")
    """Wrapped Bitcoin (WBTC) contract on Cronos."""

    dai = Contract("0xF2001B145b43032AAF5Ee2884e456CCd805F677D")
    """Dai Stablecoin (DAI) contract on Cronos."""

    usdc = Contract("0xc21223249CA28397B4B6541dfFaEcC539BfF0c59")
    """USD Coin (USDC) contract on Cronos."""

    usdt = Contract("0x66e428c3f67a68878562e79A0234c1F83c208770")
    """Tether USD (USDT) contract on Cronos."""

elif CHAINID == Network.Optimism:
    weth = Contract("0x4200000000000000000000000000000000000006")
    """Wrapped Ether (WETH) contract on Optimism."""

    wbtc = Contract("0x68f180fcCe6836688e9084f035309E29Bf0A2095")
    """Wrapped Bitcoin (WBTC) contract on Optimism."""

    dai = Contract("0xDA10009cBd5D07dd0CeCc66161FC93D7c9000da1")
    """Dai Stablecoin (DAI) contract on Optimism."""

    usdc = Contract("0x7F5c764cBc14f9669B88837ca1490cCa17c31607")
    """USD Coin (USDC) contract on Optimism."""

    usdt = Contract("0x94b008aA00579c1307B0EF2c499aD98a8ce58e58")
    """Tether USD (USDT) contract on Optimism."""

elif CHAINID == Network.Base:
    dai = Contract("0x50c5725949A6F0c72E6C4a641F24049A917DB0Cb")
    """Dai Stablecoin (DAI) contract on Base."""

    weth = Contract("0x4200000000000000000000000000000000000006")
    """Wrapped Ether (WETH) contract on Base."""

    usdc = Contract("0xd9aAEc86B65D86f6A7B5B1b0c42FFA531710b6CA")  # usdbc
    """USD Coin (USDC) contract on Base."""

    usdt = Contract("0x4A3A6Dd60A34bB2Aba60D73B4C88315E9CeB6A3D")
    """Tether USD (USDT) contract on Base."""

    wbtc = Contract("0x77852193BD608A518dd7b7C2f891A1d02ceeB4d4")
    """
    Wrapped Bitcoin (WBTC) contract on Base.

    Note:
        This is a temporary placeholder and may not represent the actual WBTC contract on Base.
    """

else:
    weth, dai, wbtc, usdc, usdt = None, None, None, None, None

_STABLECOINS: Final[Dict[Network, Dict[ChecksumAddress, str]]] = {
    Network.Mainnet: {
        "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48": "usdc",
        "0x0000000000085d4780B73119b644AE5ecd22b376": "tusd",
        "0x6B175474E89094C44Da98b954EedeAC495271d0F": "dai",
        "0xdAC17F958D2ee523a2206206994597C13D831ec7": "usdt",
        "0x57Ab1E02fEE23774580C119740129eAC7081e9D3": "susd_old",
    },
    Network.BinanceSmartChain: {
        "0x8ac76a51cc950d9822d68b83fe1ad97b32cd580d": "usdc",
        "0x1af3f329e8be154074d8769d1ffa4ee058b1dbc3": "dai",
        "0x55d398326f99059ff775485246999027b3197955": "usdt",
        "0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56": "busd",
        "0x23396cF899Ca06c4472205fC903bDB4de249D6fC": "wust",
        "0x14016E85a25aeb13065688cAFB43044C2ef86784": "tusd",
    },
    Network.Polygon: {
        "0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359": "usdc",
        "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174": "usdc.e",
        "0x8f3Cf7ad23Cd3CaDbD9735AFf958023239c6A063": "dai",
        "0xc2132D05D31c914a87C6611C10748AEb04B58e8F": "usdt",
        "0xE840B73E5287865EEc17d250bFb1536704B43B21": "musd",
    },
    Network.Fantom: {
        "0x04068DA6C83AFCFA0e13ba15A6696662335D5B75": "usdc",
        "0x8D11eC38a3EB5E956B052f67Da8Bdc9bef8Abf3E": "dai",
        "0x049d68029688eAbF473097a2fC38ef61633A3C7A": "fusdt",
        "0x9879aBDea01a879644185341F7aF7d8343556B7a": "tusd",
    },
    Network.Arbitrum: {
        "0xDA10009cBd5D07dd0CeCc66161FC93D7c9000da1": "dai",
        "0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8": "usdc",
        "0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9": "usdt",
    },
    Network.Avalanche: {
        "0xde3A24028580884448a5397872046a019649b084": "usdt",
        "0xc7198437980c041c805A1EDcbA50c1Ce5db95118": "usdt.e",
        "0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E": "usdc",
        "0xA7D7079b0FEaD91F3e65f86E8915Cb59c1a4C664": "usdc.e",
        "0xbA7dEebBFC5fA1100Fb055a87773e1E99Cd3507a": "dai",
        "0xd586E7F844cEa2F87f50152665BCbc2C279D8d70": "dai.e",
        "0x130966628846BFd36ff31a822705796e8cb8C18D": "mim",
        "0xaEb044650278731Ef3DC244692AB9F64C78FfaEA": "busd",
    },
    Network.Heco: {
        "0xa71EdC38d189767582C38A3145b5873052c3e47a": "usdt",
        "0x9362Bbef4B8313A8Aa9f0c9808B80577Aa26B73B": "usdc",
        "0x3D760a45D0887DFD89A2F5385a236B29Cb46ED2a": "dai",
    },
    Network.Harmony: {
        "0x3C2B8Be99c50593081EAA2A724F0B8285F5aba8f": "usdt",
        "0x985458E523dB3d53125813eD68c274899e9DfAb4": "usdc",
        "0xEf977d2f931C1978Db5F6747666fa1eACB0d0339": "dai",
    },
    Network.Cronos: {
        "0x66e428c3f67a68878562e79A0234c1F83c208770": "usdt",
        "0xc21223249CA28397B4B6541dfFaEcC539BfF0c59": "usdc",
        "0xF2001B145b43032AAF5Ee2884e456CCd805F677D": "dai",
    },
    Network.Optimism: {
        "0xDA10009cBd5D07dd0CeCc66161FC93D7c9000da1": "dai",
        "0x7F5c764cBc14f9669B88837ca1490cCa17c31607": "usdc",
        "0x94b008aA00579c1307B0EF2c499aD98a8ce58e58": "usdt",
    },
    Network.Base: {
        "0xd9aAEc86B65D86f6A7B5B1b0c42FFA531710b6CA": "usdbc",
        "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913": "usdc",
    },
}

STABLECOINS: Final[Dict[ChecksumAddress, str]] = _STABLECOINS.get(CHAINID, {})
"""
A dictionary mapping network IDs to stablecoin contract addresses and their corresponding symbols.

Each network has a set of stablecoin addresses with their associated symbols. This allows for easy lookup of stablecoin contracts on different networks. If the current `chain.id` is not recognized, it defaults to an empty dictionary.

Example:
    >>> STABLECOINS.get(Network.Mainnet, {}).get("0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48")
    'usdc'

See Also:
    - :class:`~y.networks.Network` for network ID definitions.
"""

WRAPPED_GAS_COINS: Final[Dict[Network, ChecksumAddress]] = {
    Network.Mainnet: "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
    Network.BinanceSmartChain: "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c",
    Network.Polygon: "0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270",
    Network.Fantom: "0x21be370D5312f44cB42ce377BC9b8a0cEF1A4C83",
    Network.Arbitrum: "0x82aF49447D8a07e3bd95BD0d56f35241523fBab1",
    Network.Avalanche: "0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7",
    Network.Heco: "0x5545153CCFcA01fbd7Dd11C0b23ba694D9509A6F",
    Network.Harmony: "0xcF664087a5bB0237a0BAd6742852ec6c8d69A27a",
    Network.Cronos: "0x5C7F8A570d578ED84E63fdFA7b1eE72dEae1AE23",
    Network.Optimism: "0x4200000000000000000000000000000000000006",
    Network.Base: "0x4200000000000000000000000000000000000006",
}

WRAPPED_GAS_COIN: Final[ChecksumAddress] = WRAPPED_GAS_COINS[CHAINID]
"""
The address of the wrapped version of the native token on the active network.

For example, on Ethereum Mainnet, `WRAPPED_GAS_COIN` == the WETH address. On Fantom, it is equal to the WFTM address. And so on.

Example:
    >>> WRAPPED_GAS_COIN
    '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'  # On Ethereum Mainnet

See Also:
    - :class:`~y.networks.Network` for network ID definitions.
"""
