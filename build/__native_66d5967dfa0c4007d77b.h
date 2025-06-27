#ifndef MYPYC_NATIVE_66d5967dfa0c4007d77b_H
#define MYPYC_NATIVE_66d5967dfa0c4007d77b_H
#include <Python.h>
#include <CPy.h>
#ifndef MYPYC_DECLARED_tuple_T2OO
#define MYPYC_DECLARED_tuple_T2OO
typedef struct tuple_T2OO {
    PyObject *f0;
    PyObject *f1;
} tuple_T2OO;
#endif

#ifndef MYPYC_DECLARED_tuple_T3OOO
#define MYPYC_DECLARED_tuple_T3OOO
typedef struct tuple_T3OOO {
    PyObject *f0;
    PyObject *f1;
    PyObject *f2;
} tuple_T3OOO;
#endif

#ifndef MYPYC_DECLARED_tuple_T6OOOOOO
#define MYPYC_DECLARED_tuple_T6OOOOOO
typedef struct tuple_T6OOOOOO {
    PyObject *f0;
    PyObject *f1;
    PyObject *f2;
    PyObject *f3;
    PyObject *f4;
    PyObject *f5;
} tuple_T6OOOOOO;
#endif

typedef struct {
    PyObject_HEAD
    CPyVTableItem *vtable;
    PyObject *___mypyc_self__;
    PyObject *_address;
    PyObject *_type;
    PyObject *_value;
    PyObject *_traceback;
    PyObject *_arg;
    CPyTagged ___mypyc_next_label__;
    PyObject *_normalized;
    PyObject *_checksummed;
    PyObject *___mypyc_temp__0;
    tuple_T3OOO ___mypyc_temp__1;
} y___convert___to_address_async_envObject;

typedef struct {
    PyObject_HEAD
    CPyVTableItem *vtable;
    PyObject *___mypyc_env__;
} y___convert___to_address_async_genObject;

typedef struct {
    PyObject_HEAD
    CPyVTableItem *vtable;
} y___exceptions___yPriceMagicErrorObject;

typedef struct {
    PyObject_HEAD
    CPyVTableItem *vtable;
} y___exceptions___PriceErrorObject;

typedef struct {
    PyObject_HEAD
    CPyVTableItem *vtable;
} y___exceptions___UnsupportedNetworkObject;

typedef struct {
    PyObject_HEAD
    CPyVTableItem *vtable;
} y___exceptions___NonStandardERC20Object;

typedef struct {
    PyObject_HEAD
    CPyVTableItem *vtable;
} y___exceptions___CantFetchParamObject;

typedef struct {
    PyObject_HEAD
    CPyVTableItem *vtable;
} y___exceptions___TokenErrorObject;

typedef struct {
    PyObject_HEAD
    CPyVTableItem *vtable;
} y___exceptions____ExplorerErrorObject;

typedef struct {
    PyObject_HEAD
    CPyVTableItem *vtable;
} y___exceptions___InvalidAPIKeyErrorObject;

typedef struct {
    PyObject_HEAD
    CPyVTableItem *vtable;
} y___exceptions___ContractNotVerifiedObject;

typedef struct {
    PyObject_HEAD
    CPyVTableItem *vtable;
} y___exceptions___NoProxyImplementationObject;

typedef struct {
    PyObject_HEAD
    CPyVTableItem *vtable;
} y___exceptions___MessedUpBrownieContractObject;

typedef struct {
    PyObject_HEAD
    CPyVTableItem *vtable;
} y___exceptions___NotAUniswapV2PoolObject;

typedef struct {
    PyObject_HEAD
    CPyVTableItem *vtable;
} y___exceptions___NotABalancerV2PoolObject;

typedef struct {
    PyObject_HEAD
    CPyVTableItem *vtable;
} y___exceptions___CantFindSwapPathObject;

typedef struct {
    PyObject_HEAD
    CPyVTableItem *vtable;
} y___exceptions___TokenNotFoundObject;

typedef struct {
    PyObject_HEAD
    CPyVTableItem *vtable;
} y___exceptions___CalldataPreparationErrorObject;

typedef struct {
    PyObject_HEAD
    CPyVTableItem *vtable;
} y___exceptions___CallRevertedObject;

typedef struct {
    PyObject_HEAD
    CPyVTableItem *vtable;
} y___exceptions___NodeNotSyncedObject;

typedef struct {
    PyObject_HEAD
    CPyVTableItem *vtable;
    PyObject *___mypyc_self__;
    PyObject *_extra_context;
    char _after;
    PyObject *_type;
    PyObject *_value;
    PyObject *_traceback;
    PyObject *_arg;
    CPyTagged ___mypyc_next_label__;
    tuple_T3OOO ___mypyc_temp__0;
    PyObject *_e;
} y___exceptions___reraise_excs_with_extra_context_envObject;

typedef struct {
    PyObject_HEAD
    CPyVTableItem *vtable;
    PyObject *___mypyc_env__;
} y___exceptions___reraise_excs_with_extra_context_genObject;

typedef struct {
    PyObject_HEAD
    CPyVTableItem *vtable;
    vectorcallfunc vectorcall;
} y___networks___label_Network_objObject;

typedef struct {
    PyObject_HEAD
    CPyVTableItem *vtable;
    vectorcallfunc vectorcall;
} y___networks___name_Network_objObject;

typedef struct {
    PyObject_HEAD
    CPyVTableItem *vtable;
    vectorcallfunc vectorcall;
} y___networks___printable_Network_objObject;

typedef struct {
    PyObject_HEAD
    CPyVTableItem *vtable;
    PyObject *___mypyc_self__;
    PyObject *_token_address;
    PyObject *_block;
    PyObject *_price;
    PyObject *_type;
    PyObject *_value;
    PyObject *_traceback;
    PyObject *_arg;
    CPyTagged ___mypyc_next_label__;
    PyObject *___mypyc_temp__0;
    tuple_T3OOO ___mypyc_temp__1;
    PyObject *_price_readable;
    PyObject *___mypyc_temp__2;
    tuple_T3OOO ___mypyc_temp__3;
    PyObject *_symbol;
    tuple_T3OOO ___mypyc_temp__4;
} y___prices___utils___sense_check___sense_check_envObject;

typedef struct {
    PyObject_HEAD
    CPyVTableItem *vtable;
    PyObject *___mypyc_env__;
} y___prices___utils___sense_check___sense_check_genObject;

typedef struct {
    PyObject_HEAD
    CPyVTableItem *vtable;
    PyObject *___mypyc_self__;
    PyObject *_token_address;
    PyObject *_type;
    PyObject *_value;
    PyObject *_traceback;
    PyObject *_arg;
    CPyTagged ___mypyc_next_label__;
    PyObject *___mypyc_temp__5;
    tuple_T3OOO ___mypyc_temp__6;
    PyObject *_bucket;
    PyObject *___mypyc_temp__7;
    tuple_T3OOO ___mypyc_temp__8;
    PyObject *_underlyings;
    PyObject *___mypyc_temp__9;
    PyObject *___mypyc_temp__10;
    PyObject *___mypyc_temp__11;
    PyObject *_und;
    PyObject *_questionable_underlyings;
    PyObject *___mypyc_temp__12;
    tuple_T3OOO ___mypyc_temp__13;
    PyObject *___mypyc_temp__14;
    tuple_T3OOO ___mypyc_temp__15;
    PyObject *_underlying;
    PyObject *___mypyc_temp__16;
    tuple_T3OOO ___mypyc_temp__17;
    PyObject *___mypyc_temp__18;
    tuple_T3OOO ___mypyc_temp__19;
    PyObject *_contract;
    PyObject *___mypyc_temp__20;
    tuple_T3OOO ___mypyc_temp__21;
    PyObject *___mypyc_temp__22;
    tuple_T3OOO ___mypyc_temp__23;
    PyObject *_underlying_addr;
    PyObject *___mypyc_temp__24;
    tuple_T3OOO ___mypyc_temp__25;
} y___prices___utils___sense_check____exit_sense_check_envObject;

typedef struct {
    PyObject_HEAD
    CPyVTableItem *vtable;
    PyObject *___mypyc_env__;
} y___prices___utils___sense_check____exit_sense_check_genObject;

typedef struct {
    PyObject_HEAD
    CPyVTableItem *vtable;
    PyObject *___mypyc_self__;
    PyObject *_address;
    PyObject *_methods;
    PyObject *_block;
    char _return_exceptions;
    PyObject *_type;
    PyObject *_value;
    PyObject *_traceback;
    PyObject *_arg;
    CPyTagged ___mypyc_next_label__;
    PyObject *___mypyc_temp__0;
    tuple_T3OOO ___mypyc_temp__1;
    PyObject *___mypyc_temp__2;
    tuple_T3OOO ___mypyc_temp__3;
} y___utils___gather___gather_methods_envObject;

typedef struct {
    PyObject_HEAD
    CPyVTableItem *vtable;
    PyObject *___mypyc_env__;
} y___utils___gather___gather_methods_genObject;

typedef struct {
    PyObject_HEAD
    CPyVTableItem *vtable;
    PyObject *___mypyc_self__;
    PyObject *_address;
    PyObject *_methods;
    PyObject *_block;
    char _return_exceptions;
    PyObject *_type;
    PyObject *_value;
    PyObject *_traceback;
    PyObject *_arg;
    CPyTagged ___mypyc_next_label__;
    PyObject *___mypyc_temp__4;
    tuple_T3OOO ___mypyc_temp__5;
    PyObject *_contract;
    PyObject *___mypyc_temp__6;
    CPyTagged ___mypyc_temp__7;
    PyObject *_method;
    PyObject *___mypyc_temp__8;
    tuple_T3OOO ___mypyc_temp__9;
} y___utils___gather____gather_methods_brownie_envObject;

typedef struct {
    PyObject_HEAD
    CPyVTableItem *vtable;
    PyObject *___mypyc_env__;
} y___utils___gather____gather_methods_brownie_genObject;

typedef struct {
    PyObject_HEAD
    CPyVTableItem *vtable;
    PyObject *___mypyc_self__;
    PyObject *_address;
    PyObject *_methods;
    PyObject *_block;
    char _return_exceptions;
    PyObject *_type;
    PyObject *_value;
    PyObject *_traceback;
    PyObject *_arg;
    CPyTagged ___mypyc_next_label__;
    PyObject *___mypyc_temp__10;
    CPyTagged ___mypyc_temp__11;
    PyObject *_method;
    PyObject *___mypyc_temp__12;
    tuple_T3OOO ___mypyc_temp__13;
} y___utils___gather____gather_methods_raw_envObject;

typedef struct {
    PyObject_HEAD
    CPyVTableItem *vtable;
    PyObject *___mypyc_env__;
} y___utils___gather____gather_methods_raw_genObject;


struct export_table_66d5967dfa0c4007d77b {
    PyObject **CPyStatic_stringify___UTC;
    PyObject **CPyStatic_stringify___astimezone;
    PyObject **CPyStatic_stringify___isoformat;
    PyObject *(*CPyDef_stringify___stringify_column_value)(PyObject *cpy_r_value, PyObject *cpy_r_provider);
    PyObject *(*CPyDef_stringify___build_row)(PyObject *cpy_r_row, PyObject *cpy_r_provider);
    PyObject *(*CPyDef_stringify___build_query)(PyObject *cpy_r_provider_name, PyObject *cpy_r_entity_name, PyObject *cpy_r_columns, PyObject *cpy_r_items);
    char (*CPyDef_stringify_____top_level__)(void);
    PyObject **CPyStatic_config___DEFAULT_SQLITE_DIR;
    PyObject **CPyStatic_config___db_provider;
    char (*CPyDef_config_____top_level__)(void);
    PyObject **CPyStatic_ENVIRONMENT_VARIABLES____envs;
    PyObject **CPyStatic_ENVIRONMENT_VARIABLES___CACHE_TTL;
    PyObject **CPyStatic_ENVIRONMENT_VARIABLES___CONTRACT_CACHE_TTL;
    PyObject **CPyStatic_ENVIRONMENT_VARIABLES___GETLOGS_BATCH_SIZE;
    PyObject **CPyStatic_ENVIRONMENT_VARIABLES___GETLOGS_DOP;
    PyObject **CPyStatic_ENVIRONMENT_VARIABLES___CHECKSUM_CACHE_MAXSIZE;
    PyObject **CPyStatic_ENVIRONMENT_VARIABLES___DB_PROVIDER;
    PyObject **CPyStatic_ENVIRONMENT_VARIABLES___SQLITE_PATH;
    PyObject **CPyStatic_ENVIRONMENT_VARIABLES___DB_HOST;
    PyObject **CPyStatic_ENVIRONMENT_VARIABLES___DB_PORT;
    PyObject **CPyStatic_ENVIRONMENT_VARIABLES___DB_USER;
    PyObject **CPyStatic_ENVIRONMENT_VARIABLES___DB_PASSWORD;
    PyObject **CPyStatic_ENVIRONMENT_VARIABLES___DB_DATABASE;
    PyObject **CPyStatic_ENVIRONMENT_VARIABLES___SKIP_CACHE;
    PyObject **CPyStatic_ENVIRONMENT_VARIABLES___SKIP_YPRICEAPI;
    char (*CPyDef_ENVIRONMENT_VARIABLES_____top_level__)(void);
    PyObject **CPyStatic_convert___HexBytes;
    PyObject **CPyStatic_convert___to_checksum_address;
    PyObject **CPyStatic_convert____checksum_thread;
    PyObject **CPyStatic_convert____is_checksummed;
    PyObject **CPyStatic_convert____is_not_checksummed;
    PyTypeObject **CPyType_convert___to_address_async_env;
    PyObject *(*CPyDef_convert___to_address_async_env)(void);
    PyTypeObject **CPyType_convert___to_address_async_gen;
    PyObject *(*CPyDef_convert___to_address_async_gen)(void);
    PyObject *(*CPyDef_convert___checksum)(PyObject *cpy_r_address);
    PyObject *(*CPyDef_convert___to_address)(PyObject *cpy_r_address);
    PyObject *(*CPyDef_convert___to_address_async_gen_____mypyc_generator_helper__)(PyObject *cpy_r___mypyc_self__, PyObject *cpy_r_type, PyObject *cpy_r_value, PyObject *cpy_r_traceback, PyObject *cpy_r_arg);
    PyObject *(*CPyDef_convert___to_address_async_gen_____next__)(PyObject *cpy_r___mypyc_self__);
    PyObject *(*CPyDef_convert___to_address_async_gen___send)(PyObject *cpy_r___mypyc_self__, PyObject *cpy_r_arg);
    PyObject *(*CPyDef_convert___to_address_async_gen_____iter__)(PyObject *cpy_r___mypyc_self__);
    PyObject *(*CPyDef_convert___to_address_async_gen___throw)(PyObject *cpy_r___mypyc_self__, PyObject *cpy_r_type, PyObject *cpy_r_value, PyObject *cpy_r_traceback);
    PyObject *(*CPyDef_convert___to_address_async_gen___close)(PyObject *cpy_r___mypyc_self__);
    PyObject *(*CPyDef_convert___to_address_async_gen_____await__)(PyObject *cpy_r___mypyc_self__);
    PyObject *(*CPyDef_convert___to_address_async)(PyObject *cpy_r_address);
    PyObject *(*CPyDef_convert_____get_checksum_from_cache)(PyObject *cpy_r_address);
    char (*CPyDef_convert_____cache_if_is_checksummed)(PyObject *cpy_r_address, PyObject *cpy_r_checksummed);
    PyObject *(*CPyDef_convert_____normalize_input_to_string)(PyObject *cpy_r_address);
    PyObject *(*CPyDef_convert____int_to_address)(CPyTagged cpy_r_int_address);
    char (*CPyDef_convert_____top_level__)(void);
    PyObject **CPyStatic_exceptions___logger;
    PyTypeObject **CPyType_exceptions___yPriceMagicError;
    PyTypeObject **CPyType_exceptions___PriceError;
    PyTypeObject **CPyType_exceptions___UnsupportedNetwork;
    PyTypeObject **CPyType_exceptions___NonStandardERC20;
    PyTypeObject **CPyType_exceptions___CantFetchParam;
    PyTypeObject **CPyType_exceptions___TokenError;
    PyTypeObject **CPyType_exceptions____ExplorerError;
    PyTypeObject **CPyType_exceptions___InvalidAPIKeyError;
    PyTypeObject **CPyType_exceptions___ContractNotVerified;
    PyTypeObject **CPyType_exceptions___NoProxyImplementation;
    PyTypeObject **CPyType_exceptions___MessedUpBrownieContract;
    PyTypeObject **CPyType_exceptions___NotAUniswapV2Pool;
    PyTypeObject **CPyType_exceptions___NotABalancerV2Pool;
    PyTypeObject **CPyType_exceptions___CantFindSwapPath;
    PyTypeObject **CPyType_exceptions___TokenNotFound;
    PyTypeObject **CPyType_exceptions___CalldataPreparationError;
    PyTypeObject **CPyType_exceptions___CallReverted;
    PyTypeObject **CPyType_exceptions___NodeNotSynced;
    PyTypeObject **CPyType_exceptions___reraise_excs_with_extra_context_env;
    PyObject *(*CPyDef_exceptions___reraise_excs_with_extra_context_env)(void);
    PyTypeObject **CPyType_exceptions___reraise_excs_with_extra_context_gen;
    PyObject *(*CPyDef_exceptions___reraise_excs_with_extra_context_gen)(void);
    char (*CPyDef_exceptions___yPriceMagicError_____init__)(PyObject *cpy_r_self, PyObject *cpy_r_exc, PyObject *cpy_r_token_address, PyObject *cpy_r_block, PyObject *cpy_r_symbol);
    char (*CPyDef_exceptions___PriceError_____init__)(PyObject *cpy_r_self, PyObject *cpy_r_logger, PyObject *cpy_r_symbol);
    char (*CPyDef_exceptions___TokenError_____init__)(PyObject *cpy_r_self, PyObject *cpy_r_token, PyObject *cpy_r_desired_type, PyObject *cpy_r_optional_extra_args);
    char (*CPyDef_exceptions___InvalidAPIKeyError_____init__)(PyObject *cpy_r_self, PyObject *cpy_r_msg);
    char (*CPyDef_exceptions___MessedUpBrownieContract_____init__)(PyObject *cpy_r_self, PyObject *cpy_r_address, PyObject *cpy_r_args);
    char (*CPyDef_exceptions___contract_not_verified)(PyObject *cpy_r_e);
    char (*CPyDef_exceptions___NotAUniswapV2Pool_____init__)(PyObject *cpy_r_self, PyObject *cpy_r_non_pool);
    char (*CPyDef_exceptions___TokenNotFound_____init__)(PyObject *cpy_r_self, PyObject *cpy_r_token, PyObject *cpy_r_container);
    char (*CPyDef_exceptions___call_reverted)(PyObject *cpy_r_e);
    char (*CPyDef_exceptions___continue_if_call_reverted)(PyObject *cpy_r_e);
    char (*CPyDef_exceptions___out_of_gas)(PyObject *cpy_r_e);
    PyObject *(*CPyDef_exceptions___reraise_excs_with_extra_context_gen_____mypyc_generator_helper__)(PyObject *cpy_r___mypyc_self__, PyObject *cpy_r_type, PyObject *cpy_r_value, PyObject *cpy_r_traceback, PyObject *cpy_r_arg);
    PyObject *(*CPyDef_exceptions___reraise_excs_with_extra_context_gen_____next__)(PyObject *cpy_r___mypyc_self__);
    PyObject *(*CPyDef_exceptions___reraise_excs_with_extra_context_gen___send)(PyObject *cpy_r___mypyc_self__, PyObject *cpy_r_arg);
    PyObject *(*CPyDef_exceptions___reraise_excs_with_extra_context_gen_____iter__)(PyObject *cpy_r___mypyc_self__);
    PyObject *(*CPyDef_exceptions___reraise_excs_with_extra_context_gen___throw)(PyObject *cpy_r___mypyc_self__, PyObject *cpy_r_type, PyObject *cpy_r_value, PyObject *cpy_r_traceback);
    PyObject *(*CPyDef_exceptions___reraise_excs_with_extra_context_gen___close)(PyObject *cpy_r___mypyc_self__);
    PyObject *(*CPyDef_exceptions___reraise_excs_with_extra_context)(PyObject *cpy_r_extra_context, char cpy_r_after);
    char (*CPyDef_exceptions_____top_level__)(void);
    CPyTagged *CPyStatic_networks___CHAINID;
    PyObject **CPyStatic_networks___Network___Mainnet;
    PyObject **CPyStatic_networks___Network___Optimism;
    PyObject **CPyStatic_networks___Network___Cronos;
    PyObject **CPyStatic_networks___Network___BinanceSmartChain;
    PyObject **CPyStatic_networks___Network___OKEx;
    PyObject **CPyStatic_networks___Network___Gnosis;
    PyObject **CPyStatic_networks___Network___xDai;
    PyObject **CPyStatic_networks___Network___Heco;
    PyObject **CPyStatic_networks___Network___Polygon;
    PyObject **CPyStatic_networks___Network___Fantom;
    PyObject **CPyStatic_networks___Network___Moonriver;
    PyObject **CPyStatic_networks___Network___Base;
    PyObject **CPyStatic_networks___Network___Arbitrum;
    PyObject **CPyStatic_networks___Network___Avalanche;
    PyObject **CPyStatic_networks___Network___Harmony;
    PyObject **CPyStatic_networks___Network___Aurora;
    PyObject **CPyStatic_networks___NETWORK_NAME;
    PyTypeObject **CPyType_networks___Network;
    PyTypeObject **CPyType_networks___label_Network_obj;
    PyObject *(*CPyDef_networks___label_Network_obj)(void);
    PyTypeObject **CPyType_networks___name_Network_obj;
    PyObject *(*CPyDef_networks___name_Network_obj)(void);
    PyTypeObject **CPyType_networks___printable_Network_obj;
    PyObject *(*CPyDef_networks___printable_Network_obj)(void);
    PyObject *(*CPyDef_networks___label_Network_obj_____get__)(PyObject *cpy_r___mypyc_self__, PyObject *cpy_r_instance, PyObject *cpy_r_owner);
    PyObject *(*CPyDef_networks___label_Network_obj_____call__)(PyObject *cpy_r___mypyc_self__, PyObject *cpy_r_chain_id);
    PyObject *(*CPyDef_networks___name_Network_obj_____get__)(PyObject *cpy_r___mypyc_self__, PyObject *cpy_r_instance, PyObject *cpy_r_owner);
    PyObject *(*CPyDef_networks___name_Network_obj_____call__)(PyObject *cpy_r___mypyc_self__, PyObject *cpy_r_chain_id);
    PyObject *(*CPyDef_networks___printable_Network_obj_____get__)(PyObject *cpy_r___mypyc_self__, PyObject *cpy_r_instance, PyObject *cpy_r_owner);
    PyObject *(*CPyDef_networks___printable_Network_obj_____call__)(PyObject *cpy_r___mypyc_self__, PyObject *cpy_r_chain_id);
    char (*CPyDef_networks_____top_level__)(void);
    PyObject **CPyStatic_sense_check___logger;
    PyObject **CPyStatic_sense_check___acceptable_all_chains;
    PyObject **CPyStatic_sense_check___ACCEPTABLE_HIGH_PRICES;
    PyTypeObject **CPyType_sense_check___sense_check_env;
    PyObject *(*CPyDef_sense_check___sense_check_env)(void);
    PyTypeObject **CPyType_sense_check___sense_check_gen;
    PyObject *(*CPyDef_sense_check___sense_check_gen)(void);
    PyTypeObject **CPyType_sense_check____exit_sense_check_env;
    PyObject *(*CPyDef_sense_check____exit_sense_check_env)(void);
    PyTypeObject **CPyType_sense_check____exit_sense_check_gen;
    PyObject *(*CPyDef_sense_check____exit_sense_check_gen)(void);
    PyObject *(*CPyDef_sense_check___sense_check_gen_____mypyc_generator_helper__)(PyObject *cpy_r___mypyc_self__, PyObject *cpy_r_type, PyObject *cpy_r_value, PyObject *cpy_r_traceback, PyObject *cpy_r_arg);
    PyObject *(*CPyDef_sense_check___sense_check_gen_____next__)(PyObject *cpy_r___mypyc_self__);
    PyObject *(*CPyDef_sense_check___sense_check_gen___send)(PyObject *cpy_r___mypyc_self__, PyObject *cpy_r_arg);
    PyObject *(*CPyDef_sense_check___sense_check_gen_____iter__)(PyObject *cpy_r___mypyc_self__);
    PyObject *(*CPyDef_sense_check___sense_check_gen___throw)(PyObject *cpy_r___mypyc_self__, PyObject *cpy_r_type, PyObject *cpy_r_value, PyObject *cpy_r_traceback);
    PyObject *(*CPyDef_sense_check___sense_check_gen___close)(PyObject *cpy_r___mypyc_self__);
    PyObject *(*CPyDef_sense_check___sense_check_gen_____await__)(PyObject *cpy_r___mypyc_self__);
    PyObject *(*CPyDef_sense_check___sense_check)(PyObject *cpy_r_token_address, PyObject *cpy_r_block, PyObject *cpy_r_price);
    PyObject *(*CPyDef_sense_check____exit_sense_check_gen_____mypyc_generator_helper__)(PyObject *cpy_r___mypyc_self__, PyObject *cpy_r_type, PyObject *cpy_r_value, PyObject *cpy_r_traceback, PyObject *cpy_r_arg);
    PyObject *(*CPyDef_sense_check____exit_sense_check_gen_____next__)(PyObject *cpy_r___mypyc_self__);
    PyObject *(*CPyDef_sense_check____exit_sense_check_gen___send)(PyObject *cpy_r___mypyc_self__, PyObject *cpy_r_arg);
    PyObject *(*CPyDef_sense_check____exit_sense_check_gen_____iter__)(PyObject *cpy_r___mypyc_self__);
    PyObject *(*CPyDef_sense_check____exit_sense_check_gen___throw)(PyObject *cpy_r___mypyc_self__, PyObject *cpy_r_type, PyObject *cpy_r_value, PyObject *cpy_r_traceback);
    PyObject *(*CPyDef_sense_check____exit_sense_check_gen___close)(PyObject *cpy_r___mypyc_self__);
    PyObject *(*CPyDef_sense_check____exit_sense_check_gen_____await__)(PyObject *cpy_r___mypyc_self__);
    PyObject *(*CPyDef_sense_check____exit_sense_check)(PyObject *cpy_r_token_address);
    char (*CPyDef_sense_check_____top_level__)(void);
    PyObject **CPyStatic_gather___Call;
    PyObject **CPyStatic_gather___igather;
    PyTypeObject **CPyType_gather___gather_methods_env;
    PyObject *(*CPyDef_gather___gather_methods_env)(void);
    PyTypeObject **CPyType_gather___gather_methods_gen;
    PyObject *(*CPyDef_gather___gather_methods_gen)(void);
    PyTypeObject **CPyType_gather____gather_methods_brownie_env;
    PyObject *(*CPyDef_gather____gather_methods_brownie_env)(void);
    PyTypeObject **CPyType_gather____gather_methods_brownie_gen;
    PyObject *(*CPyDef_gather____gather_methods_brownie_gen)(void);
    PyTypeObject **CPyType_gather____gather_methods_raw_env;
    PyObject *(*CPyDef_gather____gather_methods_raw_env)(void);
    PyTypeObject **CPyType_gather____gather_methods_raw_gen;
    PyObject *(*CPyDef_gather____gather_methods_raw_gen)(void);
    PyObject *(*CPyDef_gather___gather_methods_gen_____mypyc_generator_helper__)(PyObject *cpy_r___mypyc_self__, PyObject *cpy_r_type, PyObject *cpy_r_value, PyObject *cpy_r_traceback, PyObject *cpy_r_arg);
    PyObject *(*CPyDef_gather___gather_methods_gen_____next__)(PyObject *cpy_r___mypyc_self__);
    PyObject *(*CPyDef_gather___gather_methods_gen___send)(PyObject *cpy_r___mypyc_self__, PyObject *cpy_r_arg);
    PyObject *(*CPyDef_gather___gather_methods_gen_____iter__)(PyObject *cpy_r___mypyc_self__);
    PyObject *(*CPyDef_gather___gather_methods_gen___throw)(PyObject *cpy_r___mypyc_self__, PyObject *cpy_r_type, PyObject *cpy_r_value, PyObject *cpy_r_traceback);
    PyObject *(*CPyDef_gather___gather_methods_gen___close)(PyObject *cpy_r___mypyc_self__);
    PyObject *(*CPyDef_gather___gather_methods_gen_____await__)(PyObject *cpy_r___mypyc_self__);
    PyObject *(*CPyDef_gather___gather_methods)(PyObject *cpy_r_address, PyObject *cpy_r_methods, PyObject *cpy_r_block, char cpy_r_return_exceptions);
    PyObject *(*CPyDef_gather____gather_methods_brownie_gen_____mypyc_generator_helper__)(PyObject *cpy_r___mypyc_self__, PyObject *cpy_r_type, PyObject *cpy_r_value, PyObject *cpy_r_traceback, PyObject *cpy_r_arg);
    PyObject *(*CPyDef_gather____gather_methods_brownie_gen_____next__)(PyObject *cpy_r___mypyc_self__);
    PyObject *(*CPyDef_gather____gather_methods_brownie_gen___send)(PyObject *cpy_r___mypyc_self__, PyObject *cpy_r_arg);
    PyObject *(*CPyDef_gather____gather_methods_brownie_gen_____iter__)(PyObject *cpy_r___mypyc_self__);
    PyObject *(*CPyDef_gather____gather_methods_brownie_gen___throw)(PyObject *cpy_r___mypyc_self__, PyObject *cpy_r_type, PyObject *cpy_r_value, PyObject *cpy_r_traceback);
    PyObject *(*CPyDef_gather____gather_methods_brownie_gen___close)(PyObject *cpy_r___mypyc_self__);
    PyObject *(*CPyDef_gather____gather_methods_brownie_gen_____await__)(PyObject *cpy_r___mypyc_self__);
    PyObject *(*CPyDef_gather____gather_methods_brownie)(PyObject *cpy_r_address, PyObject *cpy_r_methods, PyObject *cpy_r_block, char cpy_r_return_exceptions);
    PyObject *(*CPyDef_gather____gather_methods_raw_gen_____mypyc_generator_helper__)(PyObject *cpy_r___mypyc_self__, PyObject *cpy_r_type, PyObject *cpy_r_value, PyObject *cpy_r_traceback, PyObject *cpy_r_arg);
    PyObject *(*CPyDef_gather____gather_methods_raw_gen_____next__)(PyObject *cpy_r___mypyc_self__);
    PyObject *(*CPyDef_gather____gather_methods_raw_gen___send)(PyObject *cpy_r___mypyc_self__, PyObject *cpy_r_arg);
    PyObject *(*CPyDef_gather____gather_methods_raw_gen_____iter__)(PyObject *cpy_r___mypyc_self__);
    PyObject *(*CPyDef_gather____gather_methods_raw_gen___throw)(PyObject *cpy_r___mypyc_self__, PyObject *cpy_r_type, PyObject *cpy_r_value, PyObject *cpy_r_traceback);
    PyObject *(*CPyDef_gather____gather_methods_raw_gen___close)(PyObject *cpy_r___mypyc_self__);
    PyObject *(*CPyDef_gather____gather_methods_raw_gen_____await__)(PyObject *cpy_r___mypyc_self__);
    PyObject *(*CPyDef_gather____gather_methods_raw)(PyObject *cpy_r_address, PyObject *cpy_r_methods, PyObject *cpy_r_block, char cpy_r_return_exceptions);
    char (*CPyDef_gather_____top_level__)(void);
};
#endif
