
.PHONY: docs

test:
	@rm -rf build/temp.* build/bdist.* build/lib.*
	pytest -W ignore -s

test-lf:
	pytest -W ignore -s --lf

debug:
	brownie run debug-price --network $(NETWORK)

debug-curve:
	brownie run debug-curve --network $(NETWORK)

test-chainlink:
	pytest -W ignore -s tests/prices/test_chainlink.py

test-chainlink-lf:
	pytest -W ignore -s tests/prices/test_chainlink.py --lf

docs:
	rm -r ./docs/source -f
	rm -r ./docs/_templates -f
	rm -r ./docs/_build -f
	sphinx-apidoc -o ./docs/source ./y
