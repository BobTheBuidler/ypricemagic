
import os

import brownie

brownie.network.connect(os.environ['BROWNIE_NETWORK_ID_MAINNET'])
brownie._config.CONFIG.settings['autofetch_sources'] = True
