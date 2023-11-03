test: 
	pytest -W ignore -s --asyncio-task-timeout 7200

test-lf:
	pytest -W ignore -s --asyncio-task-timeout 7200 --lf

debug:
	brownie run debug-price --network $(NETWORK)

test-chainlink:
	pytest -W ignore -s --asyncio-task-timeout 7200 tests/prices/test_chainlink.py

test-chainlink-lf:
	pytest -W ignore -s --asyncio-task-timeout 7200 tests/prices/test_chainlink.py --lf