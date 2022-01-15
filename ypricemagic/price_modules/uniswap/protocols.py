
from brownie import chain
from y.constants import dai, usdc, usdt, wbtc, weth
from y.networks import Network

TRY_ORDER = {
    Network.Mainnet: ['sushiswap', 'uniswap v2', 'uniswap v1', 'shibaswap'],
    Network.BinanceSmartChain: ['pancakeswapv2', 'pancakeswapv1', 'apeswap', 'wault', 'swapliquidity', 'thugswap', 'mdex', 'bakeryswap', 'nyanswop', 'narwhalswap', 'cafeswap', 'jetswap', 'babyswap', 'annex', 'viralata', 'elk', 'pantherswap', 'complus'],
    Network.Polygon: ['quickswap', 'sushi', 'apeswap', 'dfyn', 'wault', 'cometh', 'jetswap', 'polyzap', 'cafeswap'],
    Network.Fantom: ['sushi', 'spookyswap', 'spiritswap', 'paintswap', 'jetswap'],
}.get(chain.id, set())

UNISWAPS = {
    Network.Mainnet: {
        "uniswap v2":       {"factory": "0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f", "router": "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"},
        "sushiswap":        {"factory": "0xC0AEe478e3658e2610c5F7A4A2E1777cE9e4f2Ac", "router": "0xD9E1CE17F2641F24AE83637AB66A2CCA9C378B9F"},
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
    },
    Network.Polygon: {
        "quickswap":        {"factory": "0x5757371414417b8C6CAad45bAeF941aBc7d3Ab32", "router": "0xa5E0829CaCEd8fFDD4De3c43696c57F7D7A678ff"},
        "sushi":            {"factory": "0xc35DADB65012eC5796536bD9864eD8773aBc74C4", "router": "0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506"},
        "dfyn":             {"factory": "0xE7Fb3e833eFE5F9c441105EB65Ef8b261266423B", "router": "0xa5E0829CaCEd8fFDD4De3c43696c57F7D7A678ff"},
        "wault":            {"factory": "0xa98ea6356A316b44Bf710D5f9b6b4eA0081409Ef", "router": "0x3a1D87f206D12415f5b0A33E786967680AAb4f6d"},
        "cometh":           {"factory": "0x800b052609c355cA8103E06F022aA30647eAd60a", "router": "0x28E73C83C0f85784543300B96A1A3c2e900F7a35"},
        "apeswap":          {"factory": "0xCf083Be4164828f00cAE704EC15a36D711491284", "router": "0xC0788A3aD43d79aa53B09c2EaCc313A787d1d607"},
        "jetswap":          {"factory": "0x668ad0ed2622C62E24f0d5ab6B6Ac1b9D2cD4AC7", "router": "0x5C6EC38fb0e2609672BDf628B1fD605A523E5923"},
        "polyzap":          {"factory": "0x34De5ce6c9a395dB5710119419A7a29baa435C88", "router": "0x4aAEC1FA8247F85Dc3Df20F4e03FEAFdCB087Ae9"},
        "cafeswap":         {"factory": "0x5eDe3f4e7203Bf1F12d57aF1810448E5dB20f46C", "router": "0x9055682E58C74fc8DdBFC55Ad2428aB1F96098Fc"},
    },
    Network.Fantom: {
        "sushi":            {"factory": "0xc35DADB65012eC5796536bD9864eD8773aBc74C4", "router": "0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506"},
        "spookyswap":       {"factory": "0x152eE697f2E276fA89E96742e9bB9aB1F2E61bE3", "router": "0xF491e7B69E4244ad4002BC14e878a34207E38c29"},
        "spiritswap":       {"factory": "0xEF45d134b73241eDa7703fa787148D9C9F4950b0", "router": "0x16327E3FbDaCA3bcF7E38F5Af2599D2DDc33aE52"},
        "paintswap":        {"factory": "0x733A9D1585f2d14c77b49d39BC7d7dd14CdA4aa5", "router": "0xfD000ddCEa75a2E23059881c3589F6425bFf1AbB"},
        "jetswap":          {"factory": "0xf6488205957f0b4497053d6422F49e27944eE3Dd", "router": "0x845E76A8691423fbc4ECb8Dd77556Cb61c09eE25"},
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

def special_paths(router_address: str):
    protocol = ROUTER_TO_PROTOCOL[router_address]
    return SPECIAL_PATHS.get(protocol, {})
