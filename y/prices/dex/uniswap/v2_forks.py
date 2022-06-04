import logging
from functools import lru_cache
from typing import Dict, List

from brownie import chain
from y.constants import dai, usdc, usdt, wbtc, weth
from y.datatypes import Address
from y.networks import Network
from y.utils.logging import yLazyLogger

logger = logging.getLogger(__name__)


UNISWAPS = {
    Network.Mainnet: {
        "uniswap v2":       {"factory": "0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f", "router": "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"},
        "sushiswap":        {"factory": "0xC0AEe478e3658e2610c5F7A4A2E1777cE9e4f2Ac", "router": "0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F"},
        "shibaswap":        {"factory": "0x115934131916C8b277DD010Ee02de363c09d037c", "router": "0x03f7724180AA6b939894B5Ca4314783B0b36b329"},
        #"kyber":            {"factory": "0x833e4083B7ae46CeA85695c4f7ed25CDAd8886dE", "router": "0x1c87257f5e8609940bc751a07bb085bb7f8cdbe6"}
    },
    Network.BinanceSmartChain: {
        "pancakeswapv2":    {"factory": "0xcA143Ce32Fe78f1f7019d7d551a6402fC5350c73", "router": "0x10ED43C718714eb63d5aA57B78B54704E256024E"},
        "pancakeswapv1":    {"factory": "0xBCfCcbde45cE874adCB698cC183deBcF17952812", "router": "0x05fF2B0DB69458A0750badebc4f9e13aDd608C7F"},
        "sushi":            {"factory": "0xc35DADB65012eC5796536bD9864eD8773aBc74C4", "router": "0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506"},
        "wault":            {"factory": "0xB42E3FE71b7E0673335b3331B3e1053BD9822570", "router": "0xD48745E39BbED146eEC15b79cBF964884F9877c2"},
        "apeswap":          {"factory": "0x0841BD0B734E4F5853f0dD8d7Ea041c241fb0Da6", "router": "0xcF0feBd3f17CEf5b47b0cD257aCf6025c5BFf3b7"},
        "swapliquidity":    {"factory": "0x553990F2CBA90272390f62C5BDb1681fFc899675", "router": "0x70e139f4C3C4A58b2D586490aB608eAf3c1F0995"},
        "thugswap":         {"factory": "0xaC653cE27E04C6ac565FD87F18128aD33ca03Ba2", "router": "0x3bc677674df90A9e5D741f28f6CA303357D0E4Ec"},
        "mdex":             {"factory": "0x3CD1C46068dAEa5Ebb0d3f55F6915B10648062B8", "router": "0x7DAe51BD3E3376B8c7c4900E9107f12Be3AF1bA8"},
        "bakeryswap":       {"factory": "0x01bF7C66c6BD861915CdaaE475042d3c4BaE16A7", "router": "0xCDe540d7eAFE93aC5fE6233Bee57E1270D3E330F"},
        "nyanswop":         {"factory": "0xF38D202723a9376C034eD5b8Cecb4EFe8f249836", "router": "0xc946764369623F560a5962D32c1D16D45F1BD6fa"},
        "narwhalswap":      {"factory": "0xB9fA84912FF2383a617d8b433E926Adf0Dd3FEa1", "router": "0xE85C6ab56A3422E7bAfd71e81Eb7d0f290646078"},
        "cafeswap":         {"factory": "0x3e708FdbE3ADA63fc94F8F61811196f1302137AD", "router": "0x933DAea3a5995Fb94b14A7696a5F3ffD7B1E385A"},
        "jetswap":          {"factory": "0x0eb58E5c8aA63314ff5547289185cC4583DfCBD5", "router": "0xBe65b8f75B9F20f4C522e0067a3887FADa714800"},
        "babyswap":         {"factory": "0x86407bEa2078ea5f5EB5A52B2caA963bC1F889Da", "router": "0x325E343f1dE602396E256B67eFd1F61C3A6B38Bd"},
        "annex":            {"factory": "0x6a616606D9f3BaE02d215db5046b7D1030674622", "router": "0x299385325392F537Fc6B4281d2dbe31280833Dcb"},
        "viralata":         {"factory": "0x12c2B0A1c9C786Bf7AD0E92Ce3f2d1805874e185", "router": "0xdb07Ed70aA18FfC8B422bF3D8AF947E937511FDF"},
        "elk":              {"factory": "0x31aFfd875e9f68cd6Cd12Cee8943566c9A4bBA13", "router": "0xA63B831264183D755756ca9AE5190fF5183d65D6"},
        "pantherswap":      {"factory": "0x670f55c6284c629c23baE99F585e3f17E8b9FC31", "router": "0x24f7C33ae5f77e2A9ECeed7EA858B4ca2fa1B7eC"},
        "complus":          {"factory": "0xDf97982Bf70be91df4ACD3d511c551F06a0D19eC", "router": "0x07DC75E8bc57A21A183129Ec29bbCC232d79eE56"},
        "biswap":           {"factory": "0x858E3312ed3A876947EA49d572A7C42DE08af7EE", "router": "0x3a6d8cA21D1CF76F653A67577FA0D27453350dD8"},
    },
    Network.Polygon: {
        "quickswap":        {"factory": "0x5757371414417b8C6CAad45bAeF941aBc7d3Ab32", "router": "0xa5E0829CaCEd8fFDD4De3c43696c57F7D7A678ff"},
        "sushi":            {"factory": "0xc35DADB65012eC5796536bD9864eD8773aBc74C4", "router": "0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506"},
        "dfyn":             {"factory": "0xE7Fb3e833eFE5F9c441105EB65Ef8b261266423B", "router": "0xA102072A4C07F06EC3B4900FDC4C7B80b6c57429"},
        "wault":            {"factory": "0xa98ea6356A316b44Bf710D5f9b6b4eA0081409Ef", "router": "0x3a1D87f206D12415f5b0A33E786967680AAb4f6d"},
        "cometh":           {"factory": "0x800b052609c355cA8103E06F022aA30647eAd60a", "router": "0x93bcDc45f7e62f89a8e901DC4A0E2c6C427D9F25"},
        "apeswap":          {"factory": "0xCf083Be4164828f00cAE704EC15a36D711491284", "router": "0xC0788A3aD43d79aa53B09c2EaCc313A787d1d607"},
        "jetswap":          {"factory": "0x668ad0ed2622C62E24f0d5ab6B6Ac1b9D2cD4AC7", "router": "0x5C6EC38fb0e2609672BDf628B1fD605A523E5923"},
        "polyzap":          {"factory": "0x34De5ce6c9a395dB5710119419A7a29baa435C88", "router": "0x4aAEC1FA8247F85Dc3Df20F4e03FEAFdCB087Ae9"},
        "cafeswap":         {"factory": "0x5eDe3f4e7203Bf1F12d57aF1810448E5dB20f46C", "router": "0x9055682E58C74fc8DdBFC55Ad2428aB1F96098Fc"},
        "polycat":          {"factory": "0x477Ce834Ae6b7aB003cCe4BC4d8697763FF456FA", "router": "0x94930a328162957FF1dd48900aF67B5439336cBD"},
        "elk":              {"factory": "0xE3BD06c7ac7E1CeB17BdD2E5BA83E40D1515AF2a", "router": "0xf38a7A7Ac2D745E2204c13F824c00139DF831FFf"},
        "polydex":          {"factory": "0xF0681BB7088Ac68A62909929554Aa22ad89a21fB", "router": "0xe5C67Ba380FB2F70A47b489e94BCeD486bb8fB74"},
        "firebird":         {"factory": "0x5De74546d3B86C8Df7FEEc30253865e1149818C8", "router": "0xF6fa9Ea1f64f1BBfA8d71f7f43fAF6D45520bfac"}
    },
    Network.Fantom: {
        "sushi":            {"factory": "0xc35DADB65012eC5796536bD9864eD8773aBc74C4", "router": "0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506"},
        "spookyswap":       {"factory": "0x152eE697f2E276fA89E96742e9bB9aB1F2E61bE3", "router": "0xF491e7B69E4244ad4002BC14e878a34207E38c29"},
        "spiritswap":       {"factory": "0xEF45d134b73241eDa7703fa787148D9C9F4950b0", "router": "0x16327E3FbDaCA3bcF7E38F5Af2599D2DDc33aE52"},
        "paintswap":        {"factory": "0x733A9D1585f2d14c77b49d39BC7d7dd14CdA4aa5", "router": "0xfD000ddCEa75a2E23059881c3589F6425bFf1AbB"},
        "jetswap":          {"factory": "0xf6488205957f0b4497053d6422F49e27944eE3Dd", "router": "0x845E76A8691423fbc4ECb8Dd77556Cb61c09eE25"},
        "wakaswap":         {"factory": "0xB2435253C71FcA27bE41206EB2793E44e1Df6b6D", "router": "0x7B17021FcB7Bc888641dC3bEdfEd3734fCaf2c87"},
        "hyperswap":        {"factory": "0x991152411A7B5A14A8CF0cDDE8439435328070dF", "router": "0x53c153a0df7E050BbEFbb70eE9632061f12795fB"},
        "dfyn":             {"factory": "0xd9820a17053d6314B20642E465a84Bf01a3D64f5", "router": "0x2724B9497b2cF3325C6BE3ea430b3cec34B5Ef2d"},
        'shiba':            {"factory": "0xeAcC845E4db0aB59A326513347a37ed4E999aBD8", "router": "0xB6f7b3d8CD9dBf30805C0dd79809dace5603Ce6A"},
        "zdex":             {"factory": "0x6178C3B21F7cA1adD84c16AD35452c85a85F5df4", "router": "0x40b12a3E261416fF0035586ff96e23c2894560f2"},
        "bomb":             {"factory": "0xD9473A05b2edf4f614593bA5D1dBd3021d8e0Ebe", "router": "0xb9799De71100e20aC1cdbCc63C69ddA2D0D81710"},
    },
    Network.Avalanche: {
        "pangolin":         {"factory": "0xefa94DE7a4656D787667C749f7E1223D71E9FD88", "router": "0xE54Ca86531e17Ef3616d22Ca28b0D458b6C89106"},
        "traderjoe":        {"factory": "0x9Ad6C38BE94206cA50bb0d90783181662f0Cfa10", "router": "0x60aE616a2155Ee3d9A68541Ba4544862310933d4"},
        "lydia":            {"factory": "0xe0C1bb6DF4851feEEdc3E14Bd509FEAF428f7655", "router": "0xA52aBE4676dbfd04Df42eF7755F01A3c41f28D27"},
        "olive":            {"factory": "0x4Fe4D8b01A56706Bc6CaD26E8C59D0C7169976b3", "router": "0x0c45FB63001b56a21e29c7dcc1727bfDA273a368"},
        "complus":          {"factory": "0x5C02e78A3969D0E64aa2CFA765ACc1d671914aC0", "router": "0x78c18E6BE20df11f1f41b9635F3A18B8AD82dDD1"},
        "yeti":             {"factory": "0x58C8CD291Fa36130119E6dEb9E520fbb6AcA1c3a", "router": "0x262DcFB36766C88E6A7a2953c16F8defc40c378A"},
        "canary":           {"factory": "0xCFBA329d49C24b70F3a8b9CC0853493d4645436b", "router": "0x06f8ED60393AC6A4B16900273C9313222dfe9940"},
        "party":            {"factory": "0x58A08bc28f3E8dab8Fb2773D8f243bC740398b09", "router": "0xff164Ede3E7C375E8764E9e3a22D3E35F780EEBC"},
    },
    Network.Arbitrum: {
        "sushiswap":        {"factory": "0xc35DADB65012eC5796536bD9864eD8773aBc74C4", "router": "0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506"},
        "dfyn":             {"factory": "0xA102072A4C07F06EC3B4900FDC4C7B80b6c57429", "router": "0xaedE1EFe768bD8A1663A7608c63290C60B85e71c"},
        "dxswap":           {"factory": "0x359F20Ad0F42D75a5077e65F30274cABe6f4F01a", "router": "0x530476d5583724A89c8841eB6Da76E7Af4C0F17E"},
    },
    Network.Harmony: {
        "defikingdoms":     {"factory": "0x9014B937069918bd319f80e8B3BB4A2cf6FAA5F7", "router": "0x24ad62502d1C652Cc7684081169D04896aC20f30"},
    },
    Network.Aurora: {
        "trisolaris":       {"factory": "0xc66F594268041dB60507F00703b152492fb176E7", "router": "0x2CB45Edb4517d5947aFdE3BEAbF95A582506858B"},
    },
    Network.OKEx: {
        "dfyn":             {"factory": "0xE7Fb3e833eFE5F9c441105EB65Ef8b261266423B", "router": "0x34686CBF7229ed0bff2Fbe7ED2CFC916317764f6"},
    }
}.get(chain.id, {})


FACTORY_TO_ROUTER = {UNISWAPS[name]['factory']: UNISWAPS[name]['router'] for name in UNISWAPS}

ROUTER_TO_FACTORY = {UNISWAPS[name]['router']: UNISWAPS[name]['factory'] for name in UNISWAPS}

FACTORY_TO_PROTOCOL = {UNISWAPS[name]['factory']: name for name in UNISWAPS}

ROUTER_TO_PROTOCOL = {UNISWAPS[name]['router']: name for name in UNISWAPS}

SPECIAL_PATHS = {
    Network.Mainnet: {
        "sushiswap": {
            "0xEF69B5697f2Fb0345cC680210fD39b593a2f9684": ["0xEF69B5697f2Fb0345cC680210fD39b593a2f9684","0x6B3595068778DD592e39A122f4f5a5cF09C90fE2",weth,usdc]
            ,"0xbf2179859fc6D5BEE9Bf9158632Dc51678a4100e": ["0xbf2179859fc6D5BEE9Bf9158632Dc51678a4100e","0xC28E27870558cF22ADD83540d2126da2e4b464c2",weth,usdc]
            ,"0x3166C570935a7D8554c8f4eA792ff965D2EFe1f2": ["0x3166C570935a7D8554c8f4eA792ff965D2EFe1f2","0x4954Db6391F4feB5468b6B943D4935353596aEC9",usdc]
            ,"0xE6279E1c65DD41b30bA3760DCaC3CD8bbb4420D6": ["0xE6279E1c65DD41b30bA3760DCaC3CD8bbb4420D6","0x87F5F9eBE40786D49D35E1B5997b07cCAA8ADbFF",weth,usdc]
            ,"0x4954Db6391F4feB5468b6B943D4935353596aEC9": ["0x4954Db6391F4feB5468b6B943D4935353596aEC9",usdc]
            ,"0x1E18821E69B9FAA8e6e75DFFe54E7E25754beDa0": ["0x1E18821E69B9FAA8e6e75DFFe54E7E25754beDa0","0xEF69B5697f2Fb0345cC680210fD39b593a2f9684","0x6B3595068778DD592e39A122f4f5a5cF09C90fE2",weth,usdc]
            ,"0xfC1E690f61EFd961294b3e1Ce3313fBD8aa4f85d": ["0xfC1E690f61EFd961294b3e1Ce3313fBD8aa4f85d","0xba100000625a3754423978a60c9317c58a424e3D",weth,usdc]
            ,"0xBA50933C268F567BDC86E1aC131BE072C6B0b71a": ["0xBA50933C268F567BDC86E1aC131BE072C6B0b71a",weth,usdc]
            ,"0x6102407f07029892eB5Ff02164ADFaFb85f4d222": ["0x6102407f07029892eB5Ff02164ADFaFb85f4d222",usdt]
            ,"0x85034b3b2e292493D029443455Cc62ab669573B3": ["0x85034b3b2e292493D029443455Cc62ab669573B3","0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984",weth,usdc]
            ,"0xb220D53F7D0f52897Bcf25E47c4c3DC0bac344F8": ["0xb220D53F7D0f52897Bcf25E47c4c3DC0bac344F8", usdc]
            ,"0x383518188C0C6d7730D91b2c03a03C837814a899": ["0x383518188C0C6d7730D91b2c03a03C837814a899",dai]
            ,"0xafcE9B78D409bF74980CACF610AFB851BF02F257": ["0xafcE9B78D409bF74980CACF610AFB851BF02F257",wbtc,weth,usdc]
            ,"0x62B9c7356A2Dc64a1969e19C23e4f579F9810Aa7": ["0x62B9c7356A2Dc64a1969e19C23e4f579F9810Aa7","0xD533a949740bb3306d119CC777fa900bA034cd52",weth,usdc]
        },
    },
}.get(chain.id, {})

@yLazyLogger(logger)
@lru_cache
def special_paths(router_address: str) -> Dict[str,Dict[Address,List[Address]]]:
    protocol = ROUTER_TO_PROTOCOL[router_address]
    return SPECIAL_PATHS.get(protocol, {})
