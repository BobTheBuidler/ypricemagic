from brownie import chain
from ypricemagic.networks import Network
from ypricemagic.price_modules.balancer.v2.pool import BalancerV2Pool
from ypricemagic.price_modules.balancer.v2.vault import BalancerV2Vault

BALANCER_V2_VAULTS = {
    Network.Mainnet: [
        '0xBA12222222228d8Ba445958a75a0704d566BF2C8',
    ],
    Network.Fantom: [
        '0x20dd72Ed959b6147912C2e529F0a0C651c33c9ce',
    ]
}

BALANCER_V2_VAULTS = [BalancerV2Vault(vault) for vault in BALANCER_V2_VAULTS.get(chain.id, [])]

class BalancerV2:
    def __init__(self) -> None:
        self.vaults = BALANCER_V2_VAULTS

    def is_pool(self, token_address):
        try: return BalancerV2Pool(token_address).is_pool()
        except AttributeError: return False
    
    def get_pool_price(self, pool_address, block=None):
        return BalancerV2Pool(pool_address).get_pool_price()

    def get_token_price(self, token_address, block=None):
        deepest_pool = self.deepest_pool_for(token_address, block=block)
        if not deepest_pool: return
        return deepest_pool.get_token_price(token_address, block)
    
    def deepest_pool_for(self, token_address, block=None):
        deepest_pools = {vault.address: vault.deepest_pool_for(token_address, block=block) for vault in self.vaults}
        deepest_pool_balance = max(pool_balance for pool_address, pool_balance in deepest_pools.values())
        for pool_address, pool_balance in deepest_pools.values():
            if pool_balance == deepest_pool_balance: return BalancerV2Pool(pool_address)

balancer = BalancerV2()
