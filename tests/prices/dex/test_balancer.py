
from tests.fixtures import mainnet_only
from y import get_price
from y.datatypes import UsdPrice

@mainnet_only
def test_balancer_v2_pool_price():
    v2_weighted_pool = "0x96646936b91d6B9D7D0c47C496AfBF3D6ec7B6f8" # 50/50 WETH/USDC
    assert get_price(v2_weighted_pool, 14_000_000) == UsdPrice(62.35369906899849)
