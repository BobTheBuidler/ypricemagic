#ifndef MYPYC_NATIVE_839fc216801717d47e67_H
#define MYPYC_NATIVE_839fc216801717d47e67_H
#include <Python.h>
#include <CPy.h>
#ifndef MYPYC_DECLARED_tuple_T3OOO
#define MYPYC_DECLARED_tuple_T3OOO
typedef struct tuple_T3OOO {
    PyObject *f0;
    PyObject *f1;
    PyObject *f2;
} tuple_T3OOO;
#endif

#ifndef MYPYC_DECLARED_tuple_T2OO
#define MYPYC_DECLARED_tuple_T2OO
typedef struct tuple_T2OO {
    PyObject *f0;
    PyObject *f1;
} tuple_T2OO;
#endif

#ifndef MYPYC_DECLARED_tuple_T2CC
#define MYPYC_DECLARED_tuple_T2CC
typedef struct tuple_T2CC {
    char f0;
    char f1;
} tuple_T2CC;
#endif

#ifndef MYPYC_DECLARED_tuple_T16OOOOOOOOOOOOOOOO
#define MYPYC_DECLARED_tuple_T16OOOOOOOOOOOOOOOO
typedef struct tuple_T16OOOOOOOOOOOOOOOO {
    PyObject *f0;
    PyObject *f1;
    PyObject *f2;
    PyObject *f3;
    PyObject *f4;
    PyObject *f5;
    PyObject *f6;
    PyObject *f7;
    PyObject *f8;
    PyObject *f9;
    PyObject *f10;
    PyObject *f11;
    PyObject *f12;
    PyObject *f13;
    PyObject *f14;
    PyObject *f15;
} tuple_T16OOOOOOOOOOOOOOOO;
#endif

#ifndef MYPYC_DECLARED_tuple_T3CIO
#define MYPYC_DECLARED_tuple_T3CIO
typedef struct tuple_T3CIO {
    char f0;
    CPyTagged f1;
    PyObject *f2;
} tuple_T3CIO;
#endif

#ifndef MYPYC_DECLARED_tuple_T4CIOO
#define MYPYC_DECLARED_tuple_T4CIOO
typedef struct tuple_T4CIOO {
    char f0;
    CPyTagged f1;
    PyObject *f2;
    PyObject *f3;
} tuple_T4CIOO;
#endif

#ifndef MYPYC_DECLARED_tuple_T8OOOOOOOO
#define MYPYC_DECLARED_tuple_T8OOOOOOOO
typedef struct tuple_T8OOOOOOOO {
    PyObject *f0;
    PyObject *f1;
    PyObject *f2;
    PyObject *f3;
    PyObject *f4;
    PyObject *f5;
    PyObject *f6;
    PyObject *f7;
} tuple_T8OOOOOOOO;
#endif

#ifndef MYPYC_DECLARED_tuple_T2OI
#define MYPYC_DECLARED_tuple_T2OI
typedef struct tuple_T2OI {
    PyObject *f0;
    CPyTagged f1;
} tuple_T2OI;
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
    PyObject *__filename;
    PyObject *__db;
    char __connected;
    PyObject *__execute;
} y____db___brownie___AsyncCursorObject;

typedef struct {
    PyObject_HEAD
    CPyVTableItem *vtable;
    PyObject *_self;
    int32_t ___mypyc_next_label__;
    PyObject *_db;
    PyObject *___mypyc_temp__0;
    PyObject *___mypyc_temp__1;
    char ___mypyc_temp__2;
    PyObject *___mypyc_temp__3;
    tuple_T3OOO ___mypyc_temp__4;
    PyObject *___mypyc_temp__5;
    PyObject *___mypyc_temp__6;
    tuple_T3OOO ___mypyc_temp__7;
    tuple_T3OOO ___mypyc_temp__8;
    PyObject *___mypyc_temp__9;
    tuple_T3OOO ___mypyc_temp__10;
    PyObject *___mypyc_temp__11;
    tuple_T3OOO ___mypyc_temp__12;
} y____db___brownie___connect_AsyncCursor_genObject;

typedef struct {
    PyObject_HEAD
    CPyVTableItem *vtable;
    PyObject *_self;
    PyObject *_table;
    PyObject *_values;
    int32_t ___mypyc_next_label__;
} y____db___brownie___insert_AsyncCursor_genObject;

typedef struct {
    PyObject_HEAD
    CPyVTableItem *vtable;
    PyObject *_self;
    PyObject *_cmd;
    PyObject *_args;
    int32_t ___mypyc_next_label__;
    PyObject *___mypyc_temp__13;
    tuple_T3OOO ___mypyc_temp__14;
    PyObject *___mypyc_temp__15;
    PyObject *___mypyc_temp__16;
    char ___mypyc_temp__17;
    PyObject *___mypyc_temp__18;
    tuple_T3OOO ___mypyc_temp__19;
    PyObject *___mypyc_temp__20;
    PyObject *___mypyc_temp__21;
    char ___mypyc_temp__22;
    PyObject *___mypyc_temp__23;
    tuple_T3OOO ___mypyc_temp__24;
    PyObject *_cursor;
    PyObject *___mypyc_temp__25;
    tuple_T3OOO ___mypyc_temp__26;
    PyObject *_row;
    PyObject *___mypyc_temp__27;
    PyObject *___mypyc_temp__28;
    PyObject *___mypyc_temp__29;
    PyObject *___mypyc_temp__30;
    PyObject *_i;
    tuple_T3OOO ___mypyc_temp__31;
    PyObject *___mypyc_temp__32;
    tuple_T3OOO ___mypyc_temp__33;
    PyObject *___mypyc_temp__34;
    tuple_T3OOO ___mypyc_temp__35;
    PyObject *___mypyc_temp__36;
    tuple_T3OOO ___mypyc_temp__37;
    PyObject *___mypyc_temp__38;
    tuple_T3OOO ___mypyc_temp__39;
    PyObject *___mypyc_temp__40;
    tuple_T3OOO ___mypyc_temp__41;
} y____db___brownie___fetchone_AsyncCursor_genObject;

typedef struct {
    PyObject_HEAD
    CPyVTableItem *vtable;
    PyObject *_address;
    PyObject *_alias;
    PyObject *_skip_source_keys;
    int32_t ___mypyc_next_label__;
    PyObject *_where_clause;
    PyObject *___mypyc_temp__42;
    tuple_T3OOO ___mypyc_temp__43;
    PyObject *_row;
    tuple_T3OOO ___mypyc_temp__44;
    PyObject *_build_json;
    PyObject *_path_map;
    PyObject *___mypyc_temp__45;
    PyObject *___mypyc_temp__46;
    CPyTagged ___mypyc_temp__47;
    CPyTagged ___mypyc_temp__48;
    PyObject *___mypyc_temp__49;
    PyObject *_val;
    PyObject *_source_key;
    PyObject *___mypyc_temp__50;
    tuple_T3OOO ___mypyc_temp__51;
    PyObject *_sources;
    PyObject *___mypyc_temp__52;
    PyObject *___mypyc_temp__53;
    CPyTagged ___mypyc_temp__54;
    CPyTagged ___mypyc_temp__55;
    PyObject *___mypyc_temp__56;
    PyObject *_k;
    PyObject *_v;
    PyObject *_pc_map;
    PyObject *___mypyc_temp__57;
    PyObject *___mypyc_temp__58;
    CPyTagged ___mypyc_temp__59;
    CPyTagged ___mypyc_temp__60;
    PyObject *___mypyc_temp__61;
    PyObject *_key;
    PyObject *___mypyc_temp__2_0;
} y____db___brownie____get_deployment_genObject;

typedef struct {
    PyObject_HEAD
    CPyVTableItem *vtable;
    PyObject *_hashval;
    int32_t ___mypyc_next_label__;
    PyObject *___mypyc_temp__62;
    tuple_T3OOO ___mypyc_temp__63;
} y____db___brownie_____fetch_source_for_hash_genObject;

typedef struct {
    PyObject_HEAD
    CPyVTableItem *vtable;
    PyObject *___mypyc_self__;
    PyObject *_callable;
    PyObject *_retry_locked_wrap;
} y____db___decorators___retry_locked_envObject;

typedef struct {
    PyObject_HEAD
    CPyVTableItem *vtable;
    vectorcallfunc vectorcall;
    PyObject *___mypyc_env__;
} y____db___decorators___retry_locked_wrap_retry_locked_objObject;

typedef struct {
    PyObject_HEAD
    CPyVTableItem *vtable;
    vectorcallfunc vectorcall;
} y____db___decorators_____mypyc_lambda__0_objObject;

typedef struct {
    PyObject_HEAD
    CPyVTableItem *vtable;
    vectorcallfunc vectorcall;
} y____db___decorators_____mypyc_lambda__1_objObject;

typedef struct {
    PyObject_HEAD
    CPyVTableItem *vtable;
    vectorcallfunc vectorcall;
} y____db___decorators_____mypyc_lambda__2_objObject;

typedef struct {
    PyObject_HEAD
    CPyVTableItem *vtable;
    PyObject *___mypyc_self__;
    PyObject *_name;
    PyObject *_arg_names;
    PyObject *_result_count_deco;
} y____db___decorators___log_result_count_envObject;

typedef struct {
    PyObject_HEAD
    CPyVTableItem *vtable;
    PyObject *___mypyc_self__;
    PyObject *___mypyc_env__;
    PyObject *_fn;
    PyObject *_result_count_wrap;
    PyObject *_name;
    PyObject *_arg_names;
    PyObject *_result_count_deco;
} y____db___decorators___result_count_deco_log_result_count_envObject;

typedef struct {
    PyObject_HEAD
    CPyVTableItem *vtable;
    vectorcallfunc vectorcall;
    PyObject *___mypyc_env__;
} y____db___decorators___result_count_deco_log_result_count_objObject;

typedef struct {
    PyObject_HEAD
    CPyVTableItem *vtable;
    vectorcallfunc vectorcall;
    PyObject *___mypyc_env__;
} y____db___decorators___result_count_wrap_log_result_count_result_count_deco_objObject;

typedef struct {
    PyObject_HEAD
    CPyVTableItem *vtable;
    PyObject *_address;
    int32_t ___mypyc_next_label__;
    PyObject *_normalized;
    PyObject *_checksummed;
    PyObject *___mypyc_temp__0;
    tuple_T3OOO ___mypyc_temp__1;
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
    PyObject *_extra_context;
    char _after;
    int32_t ___mypyc_next_label__;
    tuple_T3OOO ___mypyc_temp__0;
    PyObject *_e;
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
    PyObject *_token_address;
    PyObject *_block;
    PyObject *_price;
    int32_t ___mypyc_next_label__;
    PyObject *___mypyc_temp__0;
    tuple_T3OOO ___mypyc_temp__1;
    PyObject *_price_readable;
    PyObject *___mypyc_temp__2;
    tuple_T3OOO ___mypyc_temp__3;
    PyObject *_symbol;
    tuple_T3OOO ___mypyc_temp__4;
} y___prices___utils___sense_check___sense_check_genObject;

typedef struct {
    PyObject_HEAD
    CPyVTableItem *vtable;
    PyObject *_token_address;
    int32_t ___mypyc_next_label__;
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
} y___prices___utils___sense_check____exit_sense_check_genObject;

typedef struct {
    PyObject_HEAD
    CPyVTableItem *vtable;
    PyObject *_address;
    PyObject *_methods;
    PyObject *_block;
    char _return_exceptions;
    int32_t ___mypyc_next_label__;
    PyObject *___mypyc_temp__0;
    tuple_T3OOO ___mypyc_temp__1;
    PyObject *___mypyc_temp__2;
    tuple_T3OOO ___mypyc_temp__3;
} y___utils___gather___gather_methods_genObject;

typedef struct {
    PyObject_HEAD
    CPyVTableItem *vtable;
    PyObject *_address;
    PyObject *_methods;
    PyObject *_block;
    char _return_exceptions;
    int32_t ___mypyc_next_label__;
    PyObject *___mypyc_temp__4;
    tuple_T3OOO ___mypyc_temp__5;
    PyObject *_contract;
    PyObject *___mypyc_temp__6;
    CPyTagged ___mypyc_temp__7;
    PyObject *_method;
    PyObject *___mypyc_temp__8;
    tuple_T3OOO ___mypyc_temp__9;
} y___utils___gather____gather_methods_brownie_genObject;

typedef struct {
    PyObject_HEAD
    CPyVTableItem *vtable;
    PyObject *_address;
    PyObject *_methods;
    PyObject *_block;
    char _return_exceptions;
    int32_t ___mypyc_next_label__;
    PyObject *___mypyc_temp__10;
    CPyTagged ___mypyc_temp__11;
    PyObject *_method;
    PyObject *___mypyc_temp__12;
    tuple_T3OOO ___mypyc_temp__13;
} y___utils___gather____gather_methods_raw_genObject;


struct export_table_839fc216801717d47e67 {
    tuple_T16OOOOOOOOOOOOOOOO *CPyStatic_brownie___SOURCE_KEYS;
    tuple_T8OOOOOOOO *CPyStatic_brownie___DISCARD_SOURCE_KEYS;
    PyObject **CPyStatic_brownie___sha1;
    PyObject **CPyStatic_brownie___dumps;
    PyObject **CPyStatic_brownie___loads;
    PyObject **CPyStatic_brownie___sqlite_lock;
    PyObject **CPyStatic_brownie___cur;
    PyObject **CPyStatic_brownie___fetchone;
    PyTypeObject **CPyType_brownie___AsyncCursor;
    PyObject *(*CPyDef_brownie___AsyncCursor)(PyObject *cpy_r_filename);
    PyTypeObject **CPyType_brownie___connect_AsyncCursor_gen;
    PyObject *(*CPyDef_brownie___connect_AsyncCursor_gen)(void);
    PyTypeObject **CPyType_brownie___insert_AsyncCursor_gen;
    PyObject *(*CPyDef_brownie___insert_AsyncCursor_gen)(void);
    PyTypeObject **CPyType_brownie___fetchone_AsyncCursor_gen;
    PyObject *(*CPyDef_brownie___fetchone_AsyncCursor_gen)(void);
    PyTypeObject **CPyType_brownie____get_deployment_gen;
    PyObject *(*CPyDef_brownie____get_deployment_gen)(void);
    PyTypeObject **CPyType_brownie_____fetch_source_for_hash_gen;
    PyObject *(*CPyDef_brownie_____fetch_source_for_hash_gen)(void);
    char (*CPyDef_brownie___AsyncCursor_____init__)(PyObject *cpy_r_self, PyObject *cpy_r_filename);
    PyObject *(*CPyDef_brownie___connect_AsyncCursor_gen_____mypyc_generator_helper__)(PyObject *cpy_r___mypyc_self__, PyObject *cpy_r_type, PyObject *cpy_r_value, PyObject *cpy_r_traceback, PyObject *cpy_r_arg);
    PyObject *(*CPyDef_brownie___connect_AsyncCursor_gen_____next__)(PyObject *cpy_r___mypyc_self__);
    PyObject *(*CPyDef_brownie___connect_AsyncCursor_gen___send)(PyObject *cpy_r___mypyc_self__, PyObject *cpy_r_arg);
    PyObject *(*CPyDef_brownie___connect_AsyncCursor_gen_____iter__)(PyObject *cpy_r___mypyc_self__);
    PyObject *(*CPyDef_brownie___connect_AsyncCursor_gen___throw)(PyObject *cpy_r___mypyc_self__, PyObject *cpy_r_type, PyObject *cpy_r_value, PyObject *cpy_r_traceback);
    PyObject *(*CPyDef_brownie___connect_AsyncCursor_gen___close)(PyObject *cpy_r___mypyc_self__);
    PyObject *(*CPyDef_brownie___connect_AsyncCursor_gen_____await__)(PyObject *cpy_r___mypyc_self__);
    PyObject *(*CPyDef_brownie___AsyncCursor___connect)(PyObject *cpy_r_self);
    PyObject *(*CPyDef_brownie___insert_AsyncCursor_gen_____mypyc_generator_helper__)(PyObject *cpy_r___mypyc_self__, PyObject *cpy_r_type, PyObject *cpy_r_value, PyObject *cpy_r_traceback, PyObject *cpy_r_arg);
    PyObject *(*CPyDef_brownie___insert_AsyncCursor_gen_____next__)(PyObject *cpy_r___mypyc_self__);
    PyObject *(*CPyDef_brownie___insert_AsyncCursor_gen___send)(PyObject *cpy_r___mypyc_self__, PyObject *cpy_r_arg);
    PyObject *(*CPyDef_brownie___insert_AsyncCursor_gen_____iter__)(PyObject *cpy_r___mypyc_self__);
    PyObject *(*CPyDef_brownie___insert_AsyncCursor_gen___throw)(PyObject *cpy_r___mypyc_self__, PyObject *cpy_r_type, PyObject *cpy_r_value, PyObject *cpy_r_traceback);
    PyObject *(*CPyDef_brownie___insert_AsyncCursor_gen___close)(PyObject *cpy_r___mypyc_self__);
    PyObject *(*CPyDef_brownie___insert_AsyncCursor_gen_____await__)(PyObject *cpy_r___mypyc_self__);
    PyObject *(*CPyDef_brownie___AsyncCursor___insert)(PyObject *cpy_r_self, PyObject *cpy_r_table, PyObject *cpy_r_values);
    PyObject *(*CPyDef_brownie___fetchone_AsyncCursor_gen_____mypyc_generator_helper__)(PyObject *cpy_r___mypyc_self__, PyObject *cpy_r_type, PyObject *cpy_r_value, PyObject *cpy_r_traceback, PyObject *cpy_r_arg);
    PyObject *(*CPyDef_brownie___fetchone_AsyncCursor_gen_____next__)(PyObject *cpy_r___mypyc_self__);
    PyObject *(*CPyDef_brownie___fetchone_AsyncCursor_gen___send)(PyObject *cpy_r___mypyc_self__, PyObject *cpy_r_arg);
    PyObject *(*CPyDef_brownie___fetchone_AsyncCursor_gen_____iter__)(PyObject *cpy_r___mypyc_self__);
    PyObject *(*CPyDef_brownie___fetchone_AsyncCursor_gen___throw)(PyObject *cpy_r___mypyc_self__, PyObject *cpy_r_type, PyObject *cpy_r_value, PyObject *cpy_r_traceback);
    PyObject *(*CPyDef_brownie___fetchone_AsyncCursor_gen___close)(PyObject *cpy_r___mypyc_self__);
    PyObject *(*CPyDef_brownie___fetchone_AsyncCursor_gen_____await__)(PyObject *cpy_r___mypyc_self__);
    PyObject *(*CPyDef_brownie___AsyncCursor___fetchone)(PyObject *cpy_r_self, PyObject *cpy_r_cmd, PyObject *cpy_r_args);
    PyObject *(*CPyDef_brownie____get_select_statement)(void);
    PyObject *(*CPyDef_brownie____get_deployment_gen_____mypyc_generator_helper__)(PyObject *cpy_r___mypyc_self__, PyObject *cpy_r_type, PyObject *cpy_r_value, PyObject *cpy_r_traceback, PyObject *cpy_r_arg);
    PyObject *(*CPyDef_brownie____get_deployment_gen_____next__)(PyObject *cpy_r___mypyc_self__);
    PyObject *(*CPyDef_brownie____get_deployment_gen___send)(PyObject *cpy_r___mypyc_self__, PyObject *cpy_r_arg);
    PyObject *(*CPyDef_brownie____get_deployment_gen_____iter__)(PyObject *cpy_r___mypyc_self__);
    PyObject *(*CPyDef_brownie____get_deployment_gen___throw)(PyObject *cpy_r___mypyc_self__, PyObject *cpy_r_type, PyObject *cpy_r_value, PyObject *cpy_r_traceback);
    PyObject *(*CPyDef_brownie____get_deployment_gen___close)(PyObject *cpy_r___mypyc_self__);
    PyObject *(*CPyDef_brownie____get_deployment_gen_____await__)(PyObject *cpy_r___mypyc_self__);
    PyObject *(*CPyDef_brownie____get_deployment)(PyObject *cpy_r_address, PyObject *cpy_r_alias, PyObject *cpy_r_skip_source_keys);
    PyObject *(*CPyDef_brownie_____fetch_source_for_hash_gen_____mypyc_generator_helper__)(PyObject *cpy_r___mypyc_self__, PyObject *cpy_r_type, PyObject *cpy_r_value, PyObject *cpy_r_traceback, PyObject *cpy_r_arg);
    PyObject *(*CPyDef_brownie_____fetch_source_for_hash_gen_____next__)(PyObject *cpy_r___mypyc_self__);
    PyObject *(*CPyDef_brownie_____fetch_source_for_hash_gen___send)(PyObject *cpy_r___mypyc_self__, PyObject *cpy_r_arg);
    PyObject *(*CPyDef_brownie_____fetch_source_for_hash_gen_____iter__)(PyObject *cpy_r___mypyc_self__);
    PyObject *(*CPyDef_brownie_____fetch_source_for_hash_gen___throw)(PyObject *cpy_r___mypyc_self__, PyObject *cpy_r_type, PyObject *cpy_r_value, PyObject *cpy_r_traceback);
    PyObject *(*CPyDef_brownie_____fetch_source_for_hash_gen___close)(PyObject *cpy_r___mypyc_self__);
    PyObject *(*CPyDef_brownie_____fetch_source_for_hash_gen_____await__)(PyObject *cpy_r___mypyc_self__);
    PyObject *(*CPyDef_brownie_____fetch_source_for_hash)(PyObject *cpy_r_hashval);
    char (*CPyDef_brownie_____top_level__)(void);
    PyObject **CPyStatic_config___DEFAULT_SQLITE_DIR;
    PyObject **CPyStatic_config___db_provider;
    char (*CPyDef_config_____top_level__)(void);
    CPyTagged *CPyStatic_decorators___DEBUG;
    PyObject **CPyStatic_decorators___logger;
    PyObject **CPyStatic_decorators___log_warning;
    PyObject **CPyStatic_decorators___log_debug;
    PyObject **CPyStatic_decorators___ydb_read_threads;
    PyObject **CPyStatic_decorators___ydb_write_threads;
    PyObject **CPyStatic_decorators___db_session_retry_locked;
    PyObject **CPyStatic_decorators___a_sync_read_db_session;
    PyObject **CPyStatic_decorators___db_session_cached;
    PyObject **CPyStatic_decorators____result_count_logger;
    PyObject **CPyStatic_decorators____result_count_logger_debug;
    PyObject **CPyStatic_decorators____result_count_logger_is_enabled_for;
    tuple_T2OI *CPyStatic_decorators____CHAIN_INFO;
    PyObject **CPyStatic_decorators___y____db___decorators___log_result_count___arg_names;
    PyTypeObject **CPyType_decorators___retry_locked_env;
    PyObject *(*CPyDef_decorators___retry_locked_env)(void);
    PyTypeObject **CPyType_decorators___retry_locked_wrap_retry_locked_obj;
    PyObject *(*CPyDef_decorators___retry_locked_wrap_retry_locked_obj)(void);
    PyTypeObject **CPyType_decorators_____mypyc_lambda__0_obj;
    PyObject *(*CPyDef_decorators_____mypyc_lambda__0_obj)(void);
    PyTypeObject **CPyType_decorators_____mypyc_lambda__1_obj;
    PyObject *(*CPyDef_decorators_____mypyc_lambda__1_obj)(void);
    PyTypeObject **CPyType_decorators_____mypyc_lambda__2_obj;
    PyObject *(*CPyDef_decorators_____mypyc_lambda__2_obj)(void);
    PyTypeObject **CPyType_decorators___log_result_count_env;
    PyObject *(*CPyDef_decorators___log_result_count_env)(void);
    PyTypeObject **CPyType_decorators___result_count_deco_log_result_count_env;
    PyObject *(*CPyDef_decorators___result_count_deco_log_result_count_env)(void);
    PyTypeObject **CPyType_decorators___result_count_deco_log_result_count_obj;
    PyObject *(*CPyDef_decorators___result_count_deco_log_result_count_obj)(void);
    PyTypeObject **CPyType_decorators___result_count_wrap_log_result_count_result_count_deco_obj;
    PyObject *(*CPyDef_decorators___result_count_wrap_log_result_count_result_count_deco_obj)(void);
    PyObject *(*CPyDef_decorators___retry_locked_wrap_retry_locked_obj_____get__)(PyObject *cpy_r___mypyc_self__, PyObject *cpy_r_instance, PyObject *cpy_r_owner);
    PyObject *(*CPyDef_decorators___retry_locked_wrap_retry_locked_obj_____call__)(PyObject *cpy_r___mypyc_self__, PyObject *cpy_r_args, PyObject *cpy_r_kwargs);
    PyObject *(*CPyDef_decorators___retry_locked)(PyObject *cpy_r_callable);
    PyObject *(*CPyDef_decorators_____mypyc_lambda__0_obj_____get__)(PyObject *cpy_r___mypyc_self__, PyObject *cpy_r_instance, PyObject *cpy_r_owner);
    PyObject *(*CPyDef_decorators_____mypyc_lambda__0_obj_____call__)(PyObject *cpy_r___mypyc_self__, PyObject *cpy_r_func);
    PyObject *(*CPyDef_decorators_____mypyc_lambda__1_obj_____get__)(PyObject *cpy_r___mypyc_self__, PyObject *cpy_r_instance, PyObject *cpy_r_owner);
    PyObject *(*CPyDef_decorators_____mypyc_lambda__1_obj_____call__)(PyObject *cpy_r___mypyc_self__, PyObject *cpy_r_fn);
    PyObject *(*CPyDef_decorators_____mypyc_lambda__2_obj_____get__)(PyObject *cpy_r___mypyc_self__, PyObject *cpy_r_instance, PyObject *cpy_r_owner);
    PyObject *(*CPyDef_decorators_____mypyc_lambda__2_obj_____call__)(PyObject *cpy_r___mypyc_self__, PyObject *cpy_r_func);
    PyObject *(*CPyDef_decorators___result_count_wrap_log_result_count_result_count_deco_obj_____get__)(PyObject *cpy_r___mypyc_self__, PyObject *cpy_r_instance, PyObject *cpy_r_owner);
    PyObject *(*CPyDef_decorators___result_count_wrap_log_result_count_result_count_deco_obj_____call__)(PyObject *cpy_r___mypyc_self__, PyObject *cpy_r_args, PyObject *cpy_r_kwargs);
    PyObject *(*CPyDef_decorators___result_count_deco_log_result_count_obj_____get__)(PyObject *cpy_r___mypyc_self__, PyObject *cpy_r_instance, PyObject *cpy_r_owner);
    PyObject *(*CPyDef_decorators___result_count_deco_log_result_count_obj_____call__)(PyObject *cpy_r___mypyc_self__, PyObject *cpy_r_fn);
    PyObject *(*CPyDef_decorators___log_result_count)(PyObject *cpy_r_name, PyObject *cpy_r_arg_names);
    char (*CPyDef_decorators_____top_level__)(void);
    PyObject **CPyStatic_stringify___UTC;
    PyObject **CPyStatic_stringify___astimezone;
    PyObject **CPyStatic_stringify___isoformat;
    PyObject *(*CPyDef_stringify___stringify_column_value)(PyObject *cpy_r_value, PyObject *cpy_r_provider);
    PyObject *(*CPyDef_stringify___build_row)(PyObject *cpy_r_row, PyObject *cpy_r_provider);
    PyObject *(*CPyDef_stringify___build_query)(PyObject *cpy_r_provider_name, PyObject *cpy_r_entity_name, PyObject *cpy_r_columns, PyObject *cpy_r_items);
    char (*CPyDef_stringify_____top_level__)(void);
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
    PyTypeObject **CPyType_sense_check___sense_check_gen;
    PyObject *(*CPyDef_sense_check___sense_check_gen)(void);
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
    PyTypeObject **CPyType_gather___gather_methods_gen;
    PyObject *(*CPyDef_gather___gather_methods_gen)(void);
    PyTypeObject **CPyType_gather____gather_methods_brownie_gen;
    PyObject *(*CPyDef_gather____gather_methods_brownie_gen)(void);
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
