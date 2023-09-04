test: 
	pytest -W ignore -s --asyncio-task-timeout 7200

test-lf:
	pytest -W ignore -s --asyncio-task-timeout 7200 --lf

debug:
	brownie run debug-price --network $(NETWORK)