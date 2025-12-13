#ifndef MYPYC_NATIVE_ypricemagic_H
#define MYPYC_NATIVE_ypricemagic_H
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
    PyObject *___mypyc_generator_attribute__execute;
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
    PyObject *___mypyc_generator_attribute__row;
} y____db___brownie_____fetch_source_for_hash_genObject;

#endif
