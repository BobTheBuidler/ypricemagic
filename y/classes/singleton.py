
from collections import defaultdict


class Singleton(type):
    def __init__(self, *args, **kwargs):
        self.__instance = None
        super().__init__(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        if self.__instance is None:
            self.__instance = super().__call__(*args, **kwargs)
        return self.__instance

class ContractSingleton(type):
    def __init__(self, address: str, *args, **kwargs):
        self.__instances = {}
        super().__init__(address, *args, **kwargs)

    def __call__(self, address: str, *args, **kwargs):
        try: return self.__instances[address]
        except KeyError:
            self.__instances[address] = super().__call__(address, *args, **kwargs)
            return self.__instances[address]
