from brownie import chain

from y.contracts import Contract
from y.networks import Network

sushi = None

if chain.id == 1:
    weth = Contract("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2")
    usdc = Contract("0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48")
    dai  = Contract("0x6B175474E89094C44Da98b954EedeAC495271d0F")
    wbtc = Contract("0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599")
    usdt = Contract("0xdAC17F958D2ee523a2206206994597C13D831ec7")
    sushi = Contract("0x6B3595068778DD592e39A122f4f5a5cF09C90fE2")

elif chain.id == 56:
    weth = Contract("0x2170Ed0880ac9A755fd29B2688956BD959F933F8")
    usdc = Contract("0x8ac76a51cc950d9822d68b83fe1ad97b32cd580d")
    dai  = Contract("0x1af3f329e8be154074d8769d1ffa4ee058b1dbc3")
    wbtc = Contract("0x2ccb7c8c51e55c2364b555ff6e6e3f7246499e16")
    usdt = Contract("0x55d398326f99059ff775485246999027b3197955")
    wbnb = Contract("0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c")
    cake = Contract("0x0e09fabb73bd3ade0a17ecc321fd13a19e81ce82")

elif chain.id == 137: #poly
    weth = Contract("0x7ceb23fd6bc0add59e62ac25578270cff1b9f619")
    usdc = Contract("0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174")
    dai  = Contract("0x8f3Cf7ad23Cd3CaDbD9735AFf958023239c6A063")
    wbtc = Contract("0x1bfd67037b42cf73acf2047067bd4f2c47d9bfd6")
    usdt = Contract("0xc2132D05D31c914a87C6611C10748AEb04B58e8F")
    wmatic = Contract("0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270")
    
elif chain.id == 250:
    weth = Contract('0x74b23882a30290451A17c44f4F05243b6b58C76d')
    usdc = Contract('0x04068DA6C83AFCFA0e13ba15A6696662335D5B75')
    dai  = Contract('0x8D11eC38a3EB5E956B052f67Da8Bdc9bef8Abf3E')
    wbtc = Contract('0x321162Cd933E2Be498Cd2267a90534A804051b11')
    usdt = Contract('0x049d68029688eAbF473097a2fC38ef61633A3C7A') #fusdt
    wftm = Contract('0x21be370D5312f44cB42ce377BC9b8a0cEF1A4C83')

elif chain.id == 42161: pass
elif chain.id == 43114: pass

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
}


WRAPPED_GAS_COIN = {
    Network.Mainnet: "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
    Network.BinanceSmartChain: "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c",
    Network.Polygon: "0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270",
    Network.Fantom: "0x21be370D5312f44cB42ce377BC9b8a0cEF1A4C83",
    #Network.Arbitrum: "",
    #Network.Avalanche: "",
}.get(chain.id)



