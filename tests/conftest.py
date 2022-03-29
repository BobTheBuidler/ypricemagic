
import os

from brownie import network

network.connect(os.environ['BROWNIE_NETWORK_ID_MAINNET'])
