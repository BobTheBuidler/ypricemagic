from brownie import chain, Contract as _Contract
from ypricemagic.interfaces.ERC20 import ERC20ABI

from y.contracts import Contract
from y.networks import Network

NETWORK_STRING = Network.name(chain.id) if Network.name(chain.id) else f"chain {chain.id}"

EEE_ADDRESS = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"

sushi = None


if chain.id == Network.Mainnet:
    weth = Contract("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2")
    usdc = Contract("0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48")
    dai  = Contract("0x6B175474E89094C44Da98b954EedeAC495271d0F")
    wbtc = Contract("0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599")
    usdt = Contract("0xdAC17F958D2ee523a2206206994597C13D831ec7")
    sushi = Contract("0x6B3595068778DD592e39A122f4f5a5cF09C90fE2")

elif chain.id == Network.BinanceSmartChain:
    weth = Contract("0x2170Ed0880ac9A755fd29B2688956BD959F933F8")
    usdc = Contract("0x8ac76a51cc950d9822d68b83fe1ad97b32cd580d")
    dai  = Contract("0x1af3f329e8be154074d8769d1ffa4ee058b1dbc3")
    wbtc = Contract("0x2ccb7c8c51e55c2364b555ff6e6e3f7246499e16")
    usdt = Contract("0x55d398326f99059ff775485246999027b3197955")
    wbnb = Contract("0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c")
    cake = Contract("0x0e09fabb73bd3ade0a17ecc321fd13a19e81ce82")

elif chain.id == Network.xDai:
    weth = Contract('0x6A023CCd1ff6F2045C3309768eAd9E68F978f6e1')
    wbtc = Contract('0x8e5bBbb09Ed1ebdE8674Cda39A0c169401db4252')
    dai = Contract('0x44fA8E6f47987339850636F88629646662444217')
    usdc = Contract('0xDDAfbb505ad214D7b80b1f830fcCc89B60fb7A83')
    usdt = Contract('0x4ECaBa5870353805a9F068101A40E0f32ed605C6')

elif chain.id == Network.Polygon:
    weth = Contract("0x7ceb23fd6bc0add59e62ac25578270cff1b9f619")
    usdc = Contract("0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174")
    dai  = Contract("0x8f3Cf7ad23Cd3CaDbD9735AFf958023239c6A063")
    wbtc = Contract("0x1bfd67037b42cf73acf2047067bd4f2c47d9bfd6")
    usdt = Contract("0xc2132D05D31c914a87C6611C10748AEb04B58e8F")
    wmatic = Contract("0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270")
    
elif chain.id == Network.Fantom:
    weth = Contract('0x74b23882a30290451A17c44f4F05243b6b58C76d')
    usdc = Contract('0x04068DA6C83AFCFA0e13ba15A6696662335D5B75')
    dai  = Contract('0x8D11eC38a3EB5E956B052f67Da8Bdc9bef8Abf3E')
    wbtc = Contract('0x321162Cd933E2Be498Cd2267a90534A804051b11')
    usdt = Contract('0x049d68029688eAbF473097a2fC38ef61633A3C7A') #fusdt
    wftm = Contract('0x21be370D5312f44cB42ce377BC9b8a0cEF1A4C83')

elif chain.id == Network.Arbitrum:
    weth = Contract('0x82aF49447D8a07e3bd95BD0d56f35241523fBab1')
    # for some reason wbtc unverified on arbi
    wbtc = _Contract.from_abi("wbtc",'0x2f2a2543B76A4166549F7aaB2e75Bef0aefC5B0f',ERC20ABI)
    dai = Contract('0xDA10009cBd5D07dd0CeCc66161FC93D7c9000da1')
    usdc = Contract('0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8')
    usdt = Contract('0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9')

elif chain.id == Network.Avalanche:
    weth = Contract('0x49D5c2BdFfac6CE2BFdB6640F4F80f226bc10bAB')
    wbtc = Contract('0x50b7545627a5162F82A992c33b87aDc75187B218')
    dai = Contract('0xd586E7F844cEa2F87f50152665BCbc2C279D8d70')
    usdc = Contract('0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E')
    usdt = Contract('0x9702230A8Ea53601f5cD2dc00fDBc13d4dF4A8c7')

elif chain.id == Network.Moonriver:
    weth = Contract('0x639A647fbe20b6c8ac19E48E2de44ea792c62c5C')
    wbtc = Contract('0x6aB6d61428fde76768D7b45D8BFeec19c6eF91A8')
    dai  = Contract('0x80A16016cC4A2E6a2CACA8a4a498b1699fF0f844')
    usdc = Contract('0xE3F5a90F9cb311505cd691a46596599aA1A0AD7D')
    usdt = Contract('0xB44a9B6905aF7c801311e8F4E76932ee959c663C')

elif chain.id == Network.Heco:
    weth = Contract('0x64FF637fB478863B7468bc97D30a5bF3A428a1fD')
    wbtc = Contract('0x70D171d269D964d14aF9617858540061e7bE9EF1')
    dai  = Contract('0x3D760a45D0887DFD89A2F5385a236B29Cb46ED2a')
    usdc = Contract('0x9362Bbef4B8313A8Aa9f0c9808B80577Aa26B73B')
    usdt = Contract('0xa71EdC38d189767582C38A3145b5873052c3e47a')

elif chain.id == Network.Harmony:
    weth = Contract('0x6983D1E6DEf3690C4d616b13597A09e6193EA013')
    wbtc = Contract('0x3095c7557bCb296ccc6e363DE01b760bA031F2d9')
    dai  = Contract('0xEf977d2f931C1978Db5F6747666fa1eACB0d0339')
    usdc = Contract('0x985458E523dB3d53125813eD68c274899e9DfAb4')
    usdt = Contract('0x3C2B8Be99c50593081EAA2A724F0B8285F5aba8f')

else: weth, dai, wbtc, usdc, usdt = None, None, None, None, None

STABLECOINS = {
    Network.Mainnet: {
        "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48": "usdc",
        "0x0000000000085d4780B73119b644AE5ecd22b376": "tusd",
        "0x6B175474E89094C44Da98b954EedeAC495271d0F": "dai",
        "0xdAC17F958D2ee523a2206206994597C13D831ec7": "usdt",
        "0x4Fabb145d64652a948d72533023f6E7A623C7C53": "busd",
        "0x57Ab1ec28D129707052df4dF418D58a2D46d5f51": "susd",
        "0x57Ab1E02fEE23774580C119740129eAC7081e9D3": "susd_old",
        "0x1456688345527bE1f37E9e627DA0837D6f08C925": "usdp",
        "0x674C6Ad92Fd080e4004b2312b45f796a192D27a0": "usdn",
        "0x853d955aCEf822Db058eb8505911ED77F175b99e": "frax",
        "0x5f98805A4E8be255a32880FDeC7F6728C6568bA0": "lusd",
        "0xBC6DA0FE9aD5f3b0d58160288917AA56653660E9": "alusd",
        "0x8e870d67f660d95d5be530380d0ec0bd388289e1": "pax",
        "0xe2f2a5C287993345a840Db3B0845fbC70f5935a5": "musd"
    },
    Network.BinanceSmartChain: {
        "0x8ac76a51cc950d9822d68b83fe1ad97b32cd580d": "usdc",
        "0x1af3f329e8be154074d8769d1ffa4ee058b1dbc3": "dai",
        "0x55d398326f99059ff775485246999027b3197955": "usdt",
        "0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56": "busd",
        "0x23396cF899Ca06c4472205fC903bDB4de249D6fC": "wust",
        "0x14016E85a25aeb13065688cAFB43044C2ef86784": "tusd",
        "0x03ab98f5dc94996F8C33E15cD4468794d12d41f9": "usdn",
    },
    Network.Polygon: {
        "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174": "usdc",
        "0x8f3Cf7ad23Cd3CaDbD9735AFf958023239c6A063": "dai",
        "0xc2132D05D31c914a87C6611C10748AEb04B58e8F": "usdt",
        "0xE840B73E5287865EEc17d250bFb1536704B43B21": "musd",
    },
    Network.Fantom: {
        "0x04068DA6C83AFCFA0e13ba15A6696662335D5B75": "usdc",
        "0x8D11eC38a3EB5E956B052f67Da8Bdc9bef8Abf3E": "dai",
        "0x049d68029688eAbF473097a2fC38ef61633A3C7A": "fusdt",
    },
    Network.Arbitrum: {
        "": "",
    },
    Network.Avalanche: {
        "": "",
    }
}.get(chain.id, {})


WRAPPED_GAS_COIN = {
    Network.Mainnet: "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
    Network.BinanceSmartChain: "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c",
    Network.Polygon: "0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270",
    Network.Fantom: "0x21be370D5312f44cB42ce377BC9b8a0cEF1A4C83",
    #Network.Arbitrum: "",
    #Network.Avalanche: "",
}.get(chain.id)



