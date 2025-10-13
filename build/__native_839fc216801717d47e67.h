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
    PyObject *___mypyc_generator_attribute__self;
    int32_t ___mypyc_next_label__;
    PyObject *___mypyc_generator_attribute__db;
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
    PyObject *___mypyc_generator_attribute__self;
    PyObject *___mypyc_generator_attribute__table;
    PyObject *___mypyc_generator_attribute__values;
    int32_t ___mypyc_next_label__;
} y____db___brownie___insert_AsyncCursor_genObject;

typedef struct {
    PyObject_HEAD
    CPyVTableItem *vtable;
    PyObject *___mypyc_generator_attribute__self;
    PyObject *___mypyc_generator_attribute__cmd;
    PyObject *___mypyc_generator_attribute__args;
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
    PyObject *___mypyc_generator_attribute__cursor;
    PyObject *___mypyc_temp__25;
    tuple_T3OOO ___mypyc_temp__26;
    PyObject *___mypyc_generator_attribute__row;
    PyObject *___mypyc_temp__27;
    PyObject *___mypyc_temp__28;
    PyObject *___mypyc_temp__29;
    PyObject *___mypyc_temp__30;
    PyObject *___mypyc_generator_attribute__i;
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
    PyObject *___mypyc_generator_attribute__address;
    PyObject *___mypyc_generator_attribute__alias;
    PyObject *___mypyc_generator_attribute__skip_source_keys;
    int32_t ___mypyc_next_label__;
    PyObject *___mypyc_generator_attribute__where_clause;
    PyObject *___mypyc_temp__42;
    tuple_T3OOO ___mypyc_temp__43;
    PyObject *___mypyc_generator_attribute__row;
    tuple_T3OOO ___mypyc_temp__44;
    PyObject *___mypyc_generator_attribute__build_json;
    PyObject *___mypyc_generator_attribute__path_map;
    PyObject *___mypyc_temp__45;
    PyObject *___mypyc_temp__46;
    CPyTagged ___mypyc_temp__47;
    int64_t ___mypyc_temp__48;
    PyObject *___mypyc_temp__49;
    PyObject *___mypyc_generator_attribute__val;
    PyObject *___mypyc_generator_attribute__source_key;
    PyObject *___mypyc_temp__50;
    tuple_T3OOO ___mypyc_temp__51;
    PyObject *___mypyc_generator_attribute__sources;
    PyObject *___mypyc_temp__52;
    PyObject *___mypyc_temp__53;
    CPyTagged ___mypyc_temp__54;
    int64_t ___mypyc_temp__55;
    PyObject *___mypyc_temp__56;
    PyObject *___mypyc_generator_attribute__k;
    PyObject *___mypyc_generator_attribute__v;
    PyObject *___mypyc_generator_attribute__pc_map;
    PyObject *___mypyc_temp__57;
    PyObject *___mypyc_temp__58;
    CPyTagged ___mypyc_temp__59;
    int64_t ___mypyc_temp__60;
    PyObject *___mypyc_temp__61;
    PyObject *___mypyc_generator_attribute__key;
    PyObject *___mypyc_temp__2_0;
} y____db___brownie____get_deployment_genObject;

typedef struct {
    PyObject_HEAD
    CPyVTableItem *vtable;
    PyObject *___mypyc_generator_attribute__hashval;
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
    PyObject *___mypyc_generator_attribute__address;
    int32_t ___mypyc_next_label__;
    PyObject *___mypyc_generator_attribute__normalized;
    PyObject *___mypyc_generator_attribute__checksummed;
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
    PyObject *___mypyc_generator_attribute__extra_context;
    char ___mypyc_generator_attribute__after;
    int32_t ___mypyc_next_label__;
    tuple_T3OOO ___mypyc_temp__0;
    PyObject *___mypyc_generator_attribute__e;
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
    PyObject *___mypyc_generator_attribute__token_address;
    PyObject *___mypyc_generator_attribute__block;
    PyObject *___mypyc_generator_attribute__price;
    int32_t ___mypyc_next_label__;
    PyObject *___mypyc_temp__0;
    tuple_T3OOO ___mypyc_temp__1;
    PyObject *___mypyc_generator_attribute__price_readable;
    PyObject *___mypyc_temp__2;
    tuple_T3OOO ___mypyc_temp__3;
    PyObject *___mypyc_generator_attribute__symbol;
    PyObject *___mypyc_generator_attribute__msg;
    tuple_T3OOO ___mypyc_temp__4;
} y___prices___utils___sense_check___sense_check_genObject;

typedef struct {
    PyObject_HEAD
    CPyVTableItem *vtable;
    PyObject *___mypyc_generator_attribute__token_address;
    int32_t ___mypyc_next_label__;
    PyObject *___mypyc_temp__5;
    tuple_T3OOO ___mypyc_temp__6;
    PyObject *___mypyc_generator_attribute__bucket;
    PyObject *___mypyc_temp__7;
    tuple_T3OOO ___mypyc_temp__8;
    PyObject *___mypyc_generator_attribute__underlyings;
    PyObject *___mypyc_temp__9;
    PyObject *___mypyc_temp__10;
    PyObject *___mypyc_temp__11;
    PyObject *___mypyc_generator_attribute__und;
    PyObject *___mypyc_generator_attribute__questionable_underlyings;
    PyObject *___mypyc_temp__12;
    tuple_T3OOO ___mypyc_temp__13;
    PyObject *___mypyc_temp__14;
    tuple_T3OOO ___mypyc_temp__15;
    PyObject *___mypyc_generator_attribute__underlying;
    PyObject *___mypyc_temp__16;
    tuple_T3OOO ___mypyc_temp__17;
    PyObject *___mypyc_temp__18;
    tuple_T3OOO ___mypyc_temp__19;
    PyObject *___mypyc_generator_attribute__contract;
    PyObject *___mypyc_temp__20;
    tuple_T3OOO ___mypyc_temp__21;
    PyObject *___mypyc_temp__22;
    tuple_T3OOO ___mypyc_temp__23;
    PyObject *___mypyc_generator_attribute__underlying_addr;
    PyObject *___mypyc_temp__24;
    tuple_T3OOO ___mypyc_temp__25;
} y___prices___utils___sense_check____exit_sense_check_genObject;

typedef struct {
    PyObject_HEAD
    CPyVTableItem *vtable;
    PyObject *___mypyc_generator_attribute__address;
    PyObject *___mypyc_generator_attribute__methods;
    PyObject *___mypyc_generator_attribute__block;
    char ___mypyc_generator_attribute__return_exceptions;
    int32_t ___mypyc_next_label__;
    PyObject *___mypyc_temp__0;
    tuple_T3OOO ___mypyc_temp__1;
    PyObject *___mypyc_temp__2;
    tuple_T3OOO ___mypyc_temp__3;
} y___utils___gather___gather_methods_genObject;

typedef struct {
    PyObject_HEAD
    CPyVTableItem *vtable;
    PyObject *___mypyc_generator_attribute__address;
    PyObject *___mypyc_generator_attribute__methods;
    PyObject *___mypyc_generator_attribute__block;
    char ___mypyc_generator_attribute__return_exceptions;
    int32_t ___mypyc_next_label__;
    PyObject *___mypyc_temp__4;
    tuple_T3OOO ___mypyc_temp__5;
    PyObject *___mypyc_generator_attribute__contract;
    PyObject *___mypyc_temp__6;
    int64_t ___mypyc_temp__7;
    int64_t ___mypyc_temp__8;
    PyObject *___mypyc_generator_attribute__method;
    PyObject *___mypyc_temp__9;
    tuple_T3OOO ___mypyc_temp__10;
} y___utils___gather____gather_methods_brownie_genObject;

typedef struct {
    PyObject_HEAD
    CPyVTableItem *vtable;
    PyObject *___mypyc_generator_attribute__address;
    PyObject *___mypyc_generator_attribute__methods;
    PyObject *___mypyc_generator_attribute__block;
    char ___mypyc_generator_attribute__return_exceptions;
    int32_t ___mypyc_next_label__;
    PyObject *___mypyc_temp__11;
    int64_t ___mypyc_temp__12;
    int64_t ___mypyc_temp__13;
    PyObject *___mypyc_generator_attribute__method;
    PyObject *___mypyc_temp__14;
    tuple_T3OOO ___mypyc_temp__15;
} y___utils___gather____gather_methods_raw_genObject;

#endif
