import os

from brownie import network

if not network.is_connected():
    try:
        network_name = os.environ["BROWNIE_NETWORK_ID"]
    except KeyError:
        raise KeyError(
            "In order to use pricemagic outside of a brownie project directory, you will need to set $BROWNIE_NETWORK_ID environment variable with the id of your preferred brownie network connection."
        )
    network.connect(network_name)
