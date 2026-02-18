from y.constants import ERC20_TRANSFER_EVENT_HASH
from y.prices import magic, yearn


async def sense_check(token_address, block=None, use_decimals=True, sync=True):
    """Sanity check for pricing."""

    if "0x" not in str(token_address):
        # token_address is probably just a symbol i.e. "DAI". We need to convert it to an address.
        token_address = await magic.get_token_from_symbol(token_address, sync=False)

    # skip checks for yearn and vbtoken (handled via underlying pricing)
    if await yearn.is_yearn_vault(token_address, sync=False) or await yearn.is_vbtoken(
        token_address, sync=False
    ):
        return True

    price = await magic.get_price(token_address, block, sync=False)
    if price is None:
        return None

    # We test a couple different sizes to ensure the price is within range for both small and large amounts.
    for test_amount in [1, 10**18]:
        # we will use the contract to help with figuring out what a transfer means in terms of value,
        # specifically for tokens which have dynamic balances.
        if use_decimals:
            test_amount = test_amount * (await magic.get_decimals(token_address, sync=False))
        try:
            v = await magic.get_value(
                token_address, test_amount, block, sync=False, use_decimals=use_decimals
            )
        except (AssertionError, TypeError):
            return False
        # ensure v is within 2 magnitudes of expected value
        if not (price / 100 < v < price * 100):
            return False

    return True
