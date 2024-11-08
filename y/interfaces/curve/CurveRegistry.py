CURVE_REGISTRY_ABI = [
    {
        "name": "PoolAdded",
        "inputs": [
            {"type": "address", "name": "pool", "indexed": True},
            {"type": "bytes", "name": "rate_method_id", "indexed": False},
        ],
        "anonymous": False,
        "type": "event",
    },
    {
        "name": "PoolRemoved",
        "inputs": [{"type": "address", "name": "pool", "indexed": True}],
        "anonymous": False,
        "type": "event",
    },
    {
        "outputs": [],
        "inputs": [
            {"type": "address", "name": "_address_provider"},
            {"type": "address", "name": "_gauge_controller"},
        ],
        "stateMutability": "nonpayable",
        "type": "constructor",
    },
    {
        "name": "find_pool_for_coins",
        "outputs": [{"type": "address", "name": ""}],
        "inputs": [
            {"type": "address", "name": "_from"},
            {"type": "address", "name": "_to"},
        ],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "name": "find_pool_for_coins",
        "outputs": [{"type": "address", "name": ""}],
        "inputs": [
            {"type": "address", "name": "_from"},
            {"type": "address", "name": "_to"},
            {"type": "uint256", "name": "i"},
        ],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "name": "get_n_coins",
        "outputs": [{"type": "uint256[2]", "name": ""}],
        "inputs": [{"type": "address", "name": "_pool"}],
        "stateMutability": "view",
        "type": "function",
        "gas": 1704,
    },
    {
        "name": "get_coins",
        "outputs": [{"type": "address[8]", "name": ""}],
        "inputs": [{"type": "address", "name": "_pool"}],
        "stateMutability": "view",
        "type": "function",
        "gas": 12285,
    },
    {
        "name": "get_underlying_coins",
        "outputs": [{"type": "address[8]", "name": ""}],
        "inputs": [{"type": "address", "name": "_pool"}],
        "stateMutability": "view",
        "type": "function",
        "gas": 12347,
    },
    {
        "name": "get_decimals",
        "outputs": [{"type": "uint256[8]", "name": ""}],
        "inputs": [{"type": "address", "name": "_pool"}],
        "stateMutability": "view",
        "type": "function",
        "gas": 8199,
    },
    {
        "name": "get_underlying_decimals",
        "outputs": [{"type": "uint256[8]", "name": ""}],
        "inputs": [{"type": "address", "name": "_pool"}],
        "stateMutability": "view",
        "type": "function",
        "gas": 8261,
    },
    {
        "name": "get_rates",
        "outputs": [{"type": "uint256[8]", "name": ""}],
        "inputs": [{"type": "address", "name": "_pool"}],
        "stateMutability": "view",
        "type": "function",
        "gas": 34780,
    },
    {
        "name": "get_gauges",
        "outputs": [
            {"type": "address[10]", "name": ""},
            {"type": "int128[10]", "name": ""},
        ],
        "inputs": [{"type": "address", "name": "_pool"}],
        "stateMutability": "view",
        "type": "function",
        "gas": 20310,
    },
    {
        "name": "get_balances",
        "outputs": [{"type": "uint256[8]", "name": ""}],
        "inputs": [{"type": "address", "name": "_pool"}],
        "stateMutability": "view",
        "type": "function",
        "gas": 16818,
    },
    {
        "name": "get_underlying_balances",
        "outputs": [{"type": "uint256[8]", "name": ""}],
        "inputs": [{"type": "address", "name": "_pool"}],
        "stateMutability": "view",
        "type": "function",
        "gas": 158953,
    },
    {
        "name": "get_virtual_price_from_lp_token",
        "outputs": [{"type": "uint256", "name": ""}],
        "inputs": [{"type": "address", "name": "_token"}],
        "stateMutability": "view",
        "type": "function",
        "gas": 2080,
    },
    {
        "name": "get_A",
        "outputs": [{"type": "uint256", "name": ""}],
        "inputs": [{"type": "address", "name": "_pool"}],
        "stateMutability": "view",
        "type": "function",
        "gas": 1198,
    },
    {
        "name": "get_parameters",
        "outputs": [
            {"type": "uint256", "name": "A"},
            {"type": "uint256", "name": "future_A"},
            {"type": "uint256", "name": "fee"},
            {"type": "uint256", "name": "admin_fee"},
            {"type": "uint256", "name": "future_fee"},
            {"type": "uint256", "name": "future_admin_fee"},
            {"type": "address", "name": "future_owner"},
            {"type": "uint256", "name": "initial_A"},
            {"type": "uint256", "name": "initial_A_time"},
            {"type": "uint256", "name": "future_A_time"},
        ],
        "inputs": [{"type": "address", "name": "_pool"}],
        "stateMutability": "view",
        "type": "function",
        "gas": 6458,
    },
    {
        "name": "get_fees",
        "outputs": [{"type": "uint256[2]", "name": ""}],
        "inputs": [{"type": "address", "name": "_pool"}],
        "stateMutability": "view",
        "type": "function",
        "gas": 1603,
    },
    {
        "name": "get_admin_balances",
        "outputs": [{"type": "uint256[8]", "name": ""}],
        "inputs": [{"type": "address", "name": "_pool"}],
        "stateMutability": "view",
        "type": "function",
        "gas": 36719,
    },
    {
        "name": "get_coin_indices",
        "outputs": [
            {"type": "int128", "name": ""},
            {"type": "int128", "name": ""},
            {"type": "bool", "name": ""},
        ],
        "inputs": [
            {"type": "address", "name": "_pool"},
            {"type": "address", "name": "_from"},
            {"type": "address", "name": "_to"},
        ],
        "stateMutability": "view",
        "type": "function",
        "gas": 27456,
    },
    {
        "name": "estimate_gas_used",
        "outputs": [{"type": "uint256", "name": ""}],
        "inputs": [
            {"type": "address", "name": "_pool"},
            {"type": "address", "name": "_from"},
            {"type": "address", "name": "_to"},
        ],
        "stateMutability": "view",
        "type": "function",
        "gas": 32329,
    },
    {
        "name": "add_pool",
        "outputs": [],
        "inputs": [
            {"type": "address", "name": "_pool"},
            {"type": "uint256", "name": "_n_coins"},
            {"type": "address", "name": "_lp_token"},
            {"type": "bytes32", "name": "_rate_method_id"},
            {"type": "uint256", "name": "_decimals"},
            {"type": "uint256", "name": "_underlying_decimals"},
            {"type": "bool", "name": "_has_initial_A"},
            {"type": "bool", "name": "_is_v1"},
        ],
        "stateMutability": "nonpayable",
        "type": "function",
        "gas": 10196577,
    },
    {
        "name": "add_pool_without_underlying",
        "outputs": [],
        "inputs": [
            {"type": "address", "name": "_pool"},
            {"type": "uint256", "name": "_n_coins"},
            {"type": "address", "name": "_lp_token"},
            {"type": "bytes32", "name": "_rate_method_id"},
            {"type": "uint256", "name": "_decimals"},
            {"type": "uint256", "name": "_use_rates"},
            {"type": "bool", "name": "_has_initial_A"},
            {"type": "bool", "name": "_is_v1"},
        ],
        "stateMutability": "nonpayable",
        "type": "function",
        "gas": 5590664,
    },
    {
        "name": "add_metapool",
        "outputs": [],
        "inputs": [
            {"type": "address", "name": "_pool"},
            {"type": "uint256", "name": "_n_coins"},
            {"type": "address", "name": "_lp_token"},
            {"type": "uint256", "name": "_decimals"},
        ],
        "stateMutability": "nonpayable",
        "type": "function",
        "gas": 10226976,
    },
    {
        "name": "remove_pool",
        "outputs": [],
        "inputs": [{"type": "address", "name": "_pool"}],
        "stateMutability": "nonpayable",
        "type": "function",
        "gas": 779646579509,
    },
    {
        "name": "set_pool_gas_estimates",
        "outputs": [],
        "inputs": [
            {"type": "address[5]", "name": "_addr"},
            {"type": "uint256[2][5]", "name": "_amount"},
        ],
        "stateMutability": "nonpayable",
        "type": "function",
        "gas": 355578,
    },
    {
        "name": "set_coin_gas_estimates",
        "outputs": [],
        "inputs": [
            {"type": "address[10]", "name": "_addr"},
            {"type": "uint256[10]", "name": "_amount"},
        ],
        "stateMutability": "nonpayable",
        "type": "function",
        "gas": 357165,
    },
    {
        "name": "set_gas_estimate_contract",
        "outputs": [],
        "inputs": [
            {"type": "address", "name": "_pool"},
            {"type": "address", "name": "_estimator"},
        ],
        "stateMutability": "nonpayable",
        "type": "function",
        "gas": 37747,
    },
    {
        "name": "set_liquidity_gauges",
        "outputs": [],
        "inputs": [
            {"type": "address", "name": "_pool"},
            {"type": "address[10]", "name": "_liquidity_gauges"},
        ],
        "stateMutability": "nonpayable",
        "type": "function",
        "gas": 365793,
    },
    {
        "name": "address_provider",
        "outputs": [{"type": "address", "name": ""}],
        "inputs": [],
        "stateMutability": "view",
        "type": "function",
        "gas": 2111,
    },
    {
        "name": "gauge_controller",
        "outputs": [{"type": "address", "name": ""}],
        "inputs": [],
        "stateMutability": "view",
        "type": "function",
        "gas": 2141,
    },
    {
        "name": "pool_list",
        "outputs": [{"type": "address", "name": ""}],
        "inputs": [{"type": "uint256", "name": "arg0"}],
        "stateMutability": "view",
        "type": "function",
        "gas": 2280,
    },
    {
        "name": "pool_count",
        "outputs": [{"type": "uint256", "name": ""}],
        "inputs": [],
        "stateMutability": "view",
        "type": "function",
        "gas": 2201,
    },
    {
        "name": "get_pool_from_lp_token",
        "outputs": [{"type": "address", "name": ""}],
        "inputs": [{"type": "address", "name": "arg0"}],
        "stateMutability": "view",
        "type": "function",
        "gas": 2446,
    },
    {
        "name": "get_lp_token",
        "outputs": [{"type": "address", "name": ""}],
        "inputs": [{"type": "address", "name": "arg0"}],
        "stateMutability": "view",
        "type": "function",
        "gas": 2476,
    },
]
