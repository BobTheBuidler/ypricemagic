from decimal import Decimal

from y.contracts import Contract

from ypricemagic.utils.raw_calls import _totalSupplyReadable


class ERC20:
    def __init__(self, token_address) -> None:
        self.address = token_address
        self.contract = Contract(self.address)
        self.build_name = self.contract.__dict__['_build']['contractName']

    def total_supply(self, block=None) -> Decimal:
        return _totalSupplyReadable(self.address, block)

