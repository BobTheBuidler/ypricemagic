import os

import brownie

brownie.network.connect(os.environ["BROWNIE_NETWORK"])
brownie._config.CONFIG.settings["autofetch_sources"] = False
