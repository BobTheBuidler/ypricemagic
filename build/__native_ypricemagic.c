#ifndef DIFFCHECK_PLACEHOLDER
#define DIFFCHECK_PLACEHOLDER 0
#endif
#include "init.c"
#include "getargs.c"
#include "getargsfast.c"
#include "int_ops.c"
#include "float_ops.c"
#include "str_ops.c"
#include "bytes_ops.c"
#include "list_ops.c"
#include "dict_ops.c"
#include "set_ops.c"
#include "tuple_ops.c"
#include "exc_ops.c"
#include "misc_ops.c"
#include "generic_ops.c"
#include "pythonsupport.c"
#include "__native_ypricemagic.h"
#include "__native_internal_ypricemagic.h"

static int
brownie___AsyncCursor_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    return 0;
}
PyObject *CPyDef_brownie_____mypyc__AsyncCursor_setup(PyObject *cpy_r_type);
PyObject *CPyDef_brownie___AsyncCursor(PyObject *cpy_r_filename);

static PyObject *
brownie___AsyncCursor_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    if (type != CPyType_brownie___AsyncCursor) {
        PyErr_SetString(PyExc_TypeError, "interpreted classes cannot inherit from compiled");
        return NULL;
    }
    PyObject *self = CPyDef_brownie_____mypyc__AsyncCursor_setup((PyObject*)type);
    if (self == NULL)
        return NULL;
    PyObject *ret = CPyPy_brownie___AsyncCursor_____init__(self, args, kwds);
    if (ret == NULL)
        return NULL;
    return self;
}

static int
brownie___AsyncCursor_traverse(y____db___brownie___AsyncCursorObject *self, visitproc visit, void *arg)
{
    Py_VISIT(self->__filename);
    Py_VISIT(self->__db);
    Py_VISIT(self->__execute);
    return 0;
}

static int
brownie___AsyncCursor_clear(y____db___brownie___AsyncCursorObject *self)
{
    Py_CLEAR(self->__filename);
    Py_CLEAR(self->__db);
    Py_CLEAR(self->__execute);
    return 0;
}

static void
brownie___AsyncCursor_dealloc(y____db___brownie___AsyncCursorObject *self)
{
    PyObject_GC_UnTrack(self);
    CPy_TRASHCAN_BEGIN(self, brownie___AsyncCursor_dealloc)
    brownie___AsyncCursor_clear(self);
    Py_TYPE(self)->tp_free((PyObject *)self);
    CPy_TRASHCAN_END(self)
    done: ;
}

static CPyVTableItem brownie___AsyncCursor_vtable[4];
static bool
CPyDef_brownie___AsyncCursor_trait_vtable_setup(void)
{
    CPyVTableItem brownie___AsyncCursor_vtable_scratch[] = {
        (CPyVTableItem)CPyDef_brownie___AsyncCursor_____init__,
        (CPyVTableItem)CPyDef_brownie___AsyncCursor___connect,
        (CPyVTableItem)CPyDef_brownie___AsyncCursor___insert,
        (CPyVTableItem)CPyDef_brownie___AsyncCursor___fetchone,
    };
    memcpy(brownie___AsyncCursor_vtable, brownie___AsyncCursor_vtable_scratch, sizeof(brownie___AsyncCursor_vtable));
    return 1;
}

static PyObject *
brownie___AsyncCursor_get__filename(y____db___brownie___AsyncCursorObject *self, void *closure);
static int
brownie___AsyncCursor_set__filename(y____db___brownie___AsyncCursorObject *self, PyObject *value, void *closure);
static PyObject *
brownie___AsyncCursor_get__db(y____db___brownie___AsyncCursorObject *self, void *closure);
static int
brownie___AsyncCursor_set__db(y____db___brownie___AsyncCursorObject *self, PyObject *value, void *closure);
static PyObject *
brownie___AsyncCursor_get__connected(y____db___brownie___AsyncCursorObject *self, void *closure);
static int
brownie___AsyncCursor_set__connected(y____db___brownie___AsyncCursorObject *self, PyObject *value, void *closure);
static PyObject *
brownie___AsyncCursor_get__execute(y____db___brownie___AsyncCursorObject *self, void *closure);
static int
brownie___AsyncCursor_set__execute(y____db___brownie___AsyncCursorObject *self, PyObject *value, void *closure);

static PyGetSetDef brownie___AsyncCursor_getseters[] = {
    {"_filename",
     (getter)brownie___AsyncCursor_get__filename, (setter)brownie___AsyncCursor_set__filename,
     NULL, NULL},
    {"_db",
     (getter)brownie___AsyncCursor_get__db, (setter)brownie___AsyncCursor_set__db,
     NULL, NULL},
    {"_connected",
     (getter)brownie___AsyncCursor_get__connected, (setter)brownie___AsyncCursor_set__connected,
     NULL, NULL},
    {"_execute",
     (getter)brownie___AsyncCursor_get__execute, (setter)brownie___AsyncCursor_set__execute,
     NULL, NULL},
    {NULL}  /* Sentinel */
};

static PyMethodDef brownie___AsyncCursor_methods[] = {
    {"__internal_mypyc_setup", (PyCFunction)CPyDef_brownie_____mypyc__AsyncCursor_setup, METH_O, NULL},
    {"__init__",
     (PyCFunction)CPyPy_brownie___AsyncCursor_____init__,
     METH_FASTCALL | METH_KEYWORDS, PyDoc_STR("__init__($self, filename)\n--\n\n")},
    {"connect",
     (PyCFunction)CPyPy_brownie___AsyncCursor___connect,
     METH_FASTCALL | METH_KEYWORDS, PyDoc_STR("connect($self)\n--\n\n")},
    {"insert",
     (PyCFunction)CPyPy_brownie___AsyncCursor___insert,
     METH_FASTCALL | METH_KEYWORDS, PyDoc_STR("insert($self, table, *values)\n--\n\n")},
    {"fetchone",
     (PyCFunction)CPyPy_brownie___AsyncCursor___fetchone,
     METH_FASTCALL | METH_KEYWORDS, PyDoc_STR("fetchone($self, cmd, *args)\n--\n\n")},
    {"__setstate__", (PyCFunction)CPyPickle_SetState, METH_O, NULL},
    {"__getstate__", (PyCFunction)CPyPickle_GetState, METH_NOARGS, NULL},
    {NULL}  /* Sentinel */
};

static PyTypeObject CPyType_brownie___AsyncCursor_template_ = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "AsyncCursor",
    .tp_new = brownie___AsyncCursor_new,
    .tp_dealloc = (destructor)brownie___AsyncCursor_dealloc,
    .tp_traverse = (traverseproc)brownie___AsyncCursor_traverse,
    .tp_clear = (inquiry)brownie___AsyncCursor_clear,
    .tp_getset = brownie___AsyncCursor_getseters,
    .tp_methods = brownie___AsyncCursor_methods,
    .tp_init = brownie___AsyncCursor_init,
    .tp_basicsize = sizeof(y____db___brownie___AsyncCursorObject),
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HEAPTYPE | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_HAVE_GC,
    .tp_doc = PyDoc_STR("AsyncCursor(filename)\n--\n\n"),
};
static PyTypeObject *CPyType_brownie___AsyncCursor_template = &CPyType_brownie___AsyncCursor_template_;

PyObject *CPyDef_brownie_____mypyc__AsyncCursor_setup(PyObject *cpy_r_type)
{
    PyTypeObject *type = (PyTypeObject*)cpy_r_type;
    y____db___brownie___AsyncCursorObject *self;
    self = (y____db___brownie___AsyncCursorObject *)type->tp_alloc(type, 0);
    if (self == NULL)
        return NULL;
    self->vtable = brownie___AsyncCursor_vtable;
    self->__connected = 2;
    return (PyObject *)self;
}

PyObject *CPyDef_brownie___AsyncCursor(PyObject *cpy_r_filename)
{
    PyObject *self = CPyDef_brownie_____mypyc__AsyncCursor_setup((PyObject *)CPyType_brownie___AsyncCursor);
    if (self == NULL)
        return NULL;
    char res = CPyDef_brownie___AsyncCursor_____init__(self, cpy_r_filename);
    if (res == 2) {
        Py_DECREF(self);
        return NULL;
    }
    return self;
}

static PyObject *
brownie___AsyncCursor_get__filename(y____db___brownie___AsyncCursorObject *self, void *closure)
{
    if (unlikely(self->__filename == NULL)) {
        PyErr_SetString(PyExc_AttributeError,
            "attribute '_filename' of 'AsyncCursor' undefined");
        return NULL;
    }
    CPy_INCREF(self->__filename);
    PyObject *retval = self->__filename;
    return retval;
}

static int
brownie___AsyncCursor_set__filename(y____db___brownie___AsyncCursorObject *self, PyObject *value, void *closure)
{
    if (value == NULL) {
        PyErr_SetString(PyExc_AttributeError,
            "'AsyncCursor' object attribute '_filename' cannot be deleted");
        return -1;
    }
    if (self->__filename != NULL) {
        CPy_DECREF(self->__filename);
    }
    PyObject *tmp = value;
    CPy_INCREF(tmp);
    self->__filename = tmp;
    return 0;
}

static PyObject *
brownie___AsyncCursor_get__db(y____db___brownie___AsyncCursorObject *self, void *closure)
{
    if (unlikely(self->__db == NULL)) {
        PyErr_SetString(PyExc_AttributeError,
            "attribute '_db' of 'AsyncCursor' undefined");
        return NULL;
    }
    CPy_INCREF(self->__db);
    PyObject *retval = self->__db;
    return retval;
}

static int
brownie___AsyncCursor_set__db(y____db___brownie___AsyncCursorObject *self, PyObject *value, void *closure)
{
    if (value == NULL) {
        PyErr_SetString(PyExc_AttributeError,
            "'AsyncCursor' object attribute '_db' cannot be deleted");
        return -1;
    }
    if (self->__db != NULL) {
        CPy_DECREF(self->__db);
    }
    PyObject *tmp;
    tmp = value;
    if (tmp != NULL) goto __LL1;
    if (value == Py_None)
        tmp = value;
    else {
        tmp = NULL;
    }
    if (tmp != NULL) goto __LL1;
    CPy_TypeError("object or None", value); 
    tmp = NULL;
__LL1: ;
    if (!tmp)
        return -1;
    CPy_INCREF(tmp);
    self->__db = tmp;
    return 0;
}

static PyObject *
brownie___AsyncCursor_get__connected(y____db___brownie___AsyncCursorObject *self, void *closure)
{
    PyObject *retval = self->__connected ? Py_True : Py_False;
    CPy_INCREF(retval);
    return retval;
}

static int
brownie___AsyncCursor_set__connected(y____db___brownie___AsyncCursorObject *self, PyObject *value, void *closure)
{
    if (value == NULL) {
        PyErr_SetString(PyExc_AttributeError,
            "'AsyncCursor' object attribute '_connected' cannot be deleted");
        return -1;
    }
    char tmp;
    if (unlikely(!PyBool_Check(value))) {
        CPy_TypeError("bool", value); return -1;
    } else
        tmp = value == Py_True;
    self->__connected = tmp;
    return 0;
}

static PyObject *
brownie___AsyncCursor_get__execute(y____db___brownie___AsyncCursorObject *self, void *closure)
{
    if (unlikely(self->__execute == NULL)) {
        PyErr_SetString(PyExc_AttributeError,
            "attribute '_execute' of 'AsyncCursor' undefined");
        return NULL;
    }
    CPy_INCREF(self->__execute);
    PyObject *retval = self->__execute;
    return retval;
}

static int
brownie___AsyncCursor_set__execute(y____db___brownie___AsyncCursorObject *self, PyObject *value, void *closure)
{
    if (value == NULL) {
        PyErr_SetString(PyExc_AttributeError,
            "'AsyncCursor' object attribute '_execute' cannot be deleted");
        return -1;
    }
    if (self->__execute != NULL) {
        CPy_DECREF(self->__execute);
    }
    PyObject *tmp;
    tmp = value;
    if (tmp != NULL) goto __LL2;
    if (value == Py_None)
        tmp = value;
    else {
        tmp = NULL;
    }
    if (tmp != NULL) goto __LL2;
    CPy_TypeError("object or None", value); 
    tmp = NULL;
__LL2: ;
    if (!tmp)
        return -1;
    CPy_INCREF(tmp);
    self->__execute = tmp;
    return 0;
}

static PyAsyncMethods brownie___connect_AsyncCursor_gen_as_async = {
    .am_await = CPyDef_brownie___connect_AsyncCursor_gen_____await__,
};
PyObject *CPyDef_brownie_____mypyc__connect_AsyncCursor_gen_setup(PyObject *cpy_r_type);
PyObject *CPyDef_brownie___connect_AsyncCursor_gen(void);

static PyObject *
brownie___connect_AsyncCursor_gen_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    if (type != CPyType_brownie___connect_AsyncCursor_gen) {
        PyErr_SetString(PyExc_TypeError, "interpreted classes cannot inherit from compiled");
        return NULL;
    }
    PyObject *self = CPyDef_brownie_____mypyc__connect_AsyncCursor_gen_setup((PyObject*)type);
    if (self == NULL)
        return NULL;
    return self;
}

static int
brownie___connect_AsyncCursor_gen_traverse(y____db___brownie___connect_AsyncCursor_genObject *self, visitproc visit, void *arg)
{
    Py_VISIT(self->___mypyc_generator_attribute__self);
    Py_VISIT(self->___mypyc_generator_attribute__db);
    Py_VISIT(self->___mypyc_temp__0);
    Py_VISIT(self->___mypyc_temp__1);
    Py_VISIT(self->___mypyc_temp__3);
    Py_VISIT(self->___mypyc_temp__4.f0);
    Py_VISIT(self->___mypyc_temp__4.f1);
    Py_VISIT(self->___mypyc_temp__4.f2);
    Py_VISIT(self->___mypyc_temp__5);
    Py_VISIT(self->___mypyc_temp__6);
    Py_VISIT(self->___mypyc_temp__7.f0);
    Py_VISIT(self->___mypyc_temp__7.f1);
    Py_VISIT(self->___mypyc_temp__7.f2);
    Py_VISIT(self->___mypyc_temp__8.f0);
    Py_VISIT(self->___mypyc_temp__8.f1);
    Py_VISIT(self->___mypyc_temp__8.f2);
    Py_VISIT(self->___mypyc_temp__9);
    Py_VISIT(self->___mypyc_temp__10.f0);
    Py_VISIT(self->___mypyc_temp__10.f1);
    Py_VISIT(self->___mypyc_temp__10.f2);
    Py_VISIT(self->___mypyc_temp__11);
    Py_VISIT(self->___mypyc_temp__12.f0);
    Py_VISIT(self->___mypyc_temp__12.f1);
    Py_VISIT(self->___mypyc_temp__12.f2);
    return 0;
}

static int
brownie___connect_AsyncCursor_gen_clear(y____db___brownie___connect_AsyncCursor_genObject *self)
{
    Py_CLEAR(self->___mypyc_generator_attribute__self);
    Py_CLEAR(self->___mypyc_generator_attribute__db);
    Py_CLEAR(self->___mypyc_temp__0);
    Py_CLEAR(self->___mypyc_temp__1);
    Py_CLEAR(self->___mypyc_temp__3);
    Py_CLEAR(self->___mypyc_temp__4.f0);
    Py_CLEAR(self->___mypyc_temp__4.f1);
    Py_CLEAR(self->___mypyc_temp__4.f2);
    Py_CLEAR(self->___mypyc_temp__5);
    Py_CLEAR(self->___mypyc_temp__6);
    Py_CLEAR(self->___mypyc_temp__7.f0);
    Py_CLEAR(self->___mypyc_temp__7.f1);
    Py_CLEAR(self->___mypyc_temp__7.f2);
    Py_CLEAR(self->___mypyc_temp__8.f0);
    Py_CLEAR(self->___mypyc_temp__8.f1);
    Py_CLEAR(self->___mypyc_temp__8.f2);
    Py_CLEAR(self->___mypyc_temp__9);
    Py_CLEAR(self->___mypyc_temp__10.f0);
    Py_CLEAR(self->___mypyc_temp__10.f1);
    Py_CLEAR(self->___mypyc_temp__10.f2);
    Py_CLEAR(self->___mypyc_temp__11);
    Py_CLEAR(self->___mypyc_temp__12.f0);
    Py_CLEAR(self->___mypyc_temp__12.f1);
    Py_CLEAR(self->___mypyc_temp__12.f2);
    return 0;
}

static void
brownie___connect_AsyncCursor_gen_dealloc(y____db___brownie___connect_AsyncCursor_genObject *self)
{
    PyObject_GC_UnTrack(self);
    if (brownie___connect_AsyncCursor_gen_free_instance == NULL) {
        brownie___connect_AsyncCursor_gen_free_instance = self;
        Py_CLEAR(self->___mypyc_generator_attribute__self);
        self->___mypyc_next_label__ = -113;
        Py_CLEAR(self->___mypyc_generator_attribute__db);
        Py_CLEAR(self->___mypyc_temp__0);
        Py_CLEAR(self->___mypyc_temp__1);
        self->___mypyc_temp__2 = 2;
        Py_CLEAR(self->___mypyc_temp__3);
        Py_CLEAR(self->___mypyc_temp__4.f0);
        Py_CLEAR(self->___mypyc_temp__4.f1);
        Py_CLEAR(self->___mypyc_temp__4.f2);
        Py_CLEAR(self->___mypyc_temp__5);
        Py_CLEAR(self->___mypyc_temp__6);
        Py_CLEAR(self->___mypyc_temp__7.f0);
        Py_CLEAR(self->___mypyc_temp__7.f1);
        Py_CLEAR(self->___mypyc_temp__7.f2);
        Py_CLEAR(self->___mypyc_temp__8.f0);
        Py_CLEAR(self->___mypyc_temp__8.f1);
        Py_CLEAR(self->___mypyc_temp__8.f2);
        Py_CLEAR(self->___mypyc_temp__9);
        Py_CLEAR(self->___mypyc_temp__10.f0);
        Py_CLEAR(self->___mypyc_temp__10.f1);
        Py_CLEAR(self->___mypyc_temp__10.f2);
        Py_CLEAR(self->___mypyc_temp__11);
        Py_CLEAR(self->___mypyc_temp__12.f0);
        Py_CLEAR(self->___mypyc_temp__12.f1);
        Py_CLEAR(self->___mypyc_temp__12.f2);
        return;
    }
    CPy_TRASHCAN_BEGIN(self, brownie___connect_AsyncCursor_gen_dealloc)
    brownie___connect_AsyncCursor_gen_clear(self);
    Py_TYPE(self)->tp_free((PyObject *)self);
    CPy_TRASHCAN_END(self)
    done: ;
}

static CPyVTableItem brownie___connect_AsyncCursor_gen_vtable[7];
static bool
CPyDef_brownie___connect_AsyncCursor_gen_trait_vtable_setup(void)
{
    CPyVTableItem brownie___connect_AsyncCursor_gen_vtable_scratch[] = {
        (CPyVTableItem)CPyDef_brownie___connect_AsyncCursor_gen_____mypyc_generator_helper__,
        (CPyVTableItem)CPyDef_brownie___connect_AsyncCursor_gen_____next__,
        (CPyVTableItem)CPyDef_brownie___connect_AsyncCursor_gen___send,
        (CPyVTableItem)CPyDef_brownie___connect_AsyncCursor_gen_____iter__,
        (CPyVTableItem)CPyDef_brownie___connect_AsyncCursor_gen___throw,
        (CPyVTableItem)CPyDef_brownie___connect_AsyncCursor_gen___close,
        (CPyVTableItem)CPyDef_brownie___connect_AsyncCursor_gen_____await__,
    };
    memcpy(brownie___connect_AsyncCursor_gen_vtable, brownie___connect_AsyncCursor_gen_vtable_scratch, sizeof(brownie___connect_AsyncCursor_gen_vtable));
    return 1;
}

static PyMethodDef brownie___connect_AsyncCursor_gen_methods[] = {
    {"__internal_mypyc_setup", (PyCFunction)CPyDef_brownie_____mypyc__connect_AsyncCursor_gen_setup, METH_O, NULL},
    {"__next__",
     (PyCFunction)CPyPy_brownie___connect_AsyncCursor_gen_____next__,
     METH_FASTCALL | METH_KEYWORDS, PyDoc_STR("__next__()\n--\n\n")},
    {"send",
     (PyCFunction)CPyPy_brownie___connect_AsyncCursor_gen___send,
     METH_FASTCALL | METH_KEYWORDS, PyDoc_STR("send($arg)\n--\n\n")},
    {"__iter__",
     (PyCFunction)CPyPy_brownie___connect_AsyncCursor_gen_____iter__,
     METH_FASTCALL | METH_KEYWORDS, PyDoc_STR("__iter__()\n--\n\n")},
    {"throw",
     (PyCFunction)CPyPy_brownie___connect_AsyncCursor_gen___throw,
     METH_FASTCALL | METH_KEYWORDS, PyDoc_STR(NULL)},
    {"close",
     (PyCFunction)CPyPy_brownie___connect_AsyncCursor_gen___close,
     METH_FASTCALL | METH_KEYWORDS, PyDoc_STR("close()\n--\n\n")},
    {"__await__",
     (PyCFunction)CPyPy_brownie___connect_AsyncCursor_gen_____await__,
     METH_FASTCALL | METH_KEYWORDS, PyDoc_STR("__await__()\n--\n\n")},
    {"__setstate__", (PyCFunction)CPyPickle_SetState, METH_O, NULL},
    {"__getstate__", (PyCFunction)CPyPickle_GetState, METH_NOARGS, NULL},
    {NULL}  /* Sentinel */
};

static PyTypeObject CPyType_brownie___connect_AsyncCursor_gen_template_ = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "connect_AsyncCursor_gen",
    .tp_new = brownie___connect_AsyncCursor_gen_new,
    .tp_dealloc = (destructor)brownie___connect_AsyncCursor_gen_dealloc,
    .tp_traverse = (traverseproc)brownie___connect_AsyncCursor_gen_traverse,
    .tp_clear = (inquiry)brownie___connect_AsyncCursor_gen_clear,
    .tp_methods = brownie___connect_AsyncCursor_gen_methods,
    .tp_iter = CPyDef_brownie___connect_AsyncCursor_gen_____iter__,
    .tp_iternext = CPyDef_brownie___connect_AsyncCursor_gen_____next__,
    .tp_as_async = &brownie___connect_AsyncCursor_gen_as_async,
    .tp_basicsize = sizeof(y____db___brownie___connect_AsyncCursor_genObject),
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HEAPTYPE | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_HAVE_GC,
    .tp_doc = PyDoc_STR("connect_AsyncCursor_gen()\n--\n\n"),
};
static PyTypeObject *CPyType_brownie___connect_AsyncCursor_gen_template = &CPyType_brownie___connect_AsyncCursor_gen_template_;

PyObject *CPyDef_brownie_____mypyc__connect_AsyncCursor_gen_setup(PyObject *cpy_r_type)
{
    PyTypeObject *type = (PyTypeObject*)cpy_r_type;
    y____db___brownie___connect_AsyncCursor_genObject *self;
    if (brownie___connect_AsyncCursor_gen_free_instance != NULL) {
        self = brownie___connect_AsyncCursor_gen_free_instance;
        brownie___connect_AsyncCursor_gen_free_instance = NULL;
        Py_SET_REFCNT(self, 1);
        PyObject_GC_Track(self);
        return (PyObject *)self;
    }
    self = (y____db___brownie___connect_AsyncCursor_genObject *)type->tp_alloc(type, 0);
    if (self == NULL)
        return NULL;
    self->vtable = brownie___connect_AsyncCursor_gen_vtable;
    self->___mypyc_next_label__ = -113;
    self->___mypyc_temp__2 = 2;
    self->___mypyc_temp__4 = (tuple_T3OOO) { NULL, NULL, NULL };
    self->___mypyc_temp__7 = (tuple_T3OOO) { NULL, NULL, NULL };
    self->___mypyc_temp__8 = (tuple_T3OOO) { NULL, NULL, NULL };
    self->___mypyc_temp__10 = (tuple_T3OOO) { NULL, NULL, NULL };
    self->___mypyc_temp__12 = (tuple_T3OOO) { NULL, NULL, NULL };
    return (PyObject *)self;
}

PyObject *CPyDef_brownie___connect_AsyncCursor_gen(void)
{
    PyObject *self = CPyDef_brownie_____mypyc__connect_AsyncCursor_gen_setup((PyObject *)CPyType_brownie___connect_AsyncCursor_gen);
    if (self == NULL)
        return NULL;
    return self;
}


static PyAsyncMethods brownie___insert_AsyncCursor_gen_as_async = {
    .am_await = CPyDef_brownie___insert_AsyncCursor_gen_____await__,
};
PyObject *CPyDef_brownie_____mypyc__insert_AsyncCursor_gen_setup(PyObject *cpy_r_type);
PyObject *CPyDef_brownie___insert_AsyncCursor_gen(void);

static PyObject *
brownie___insert_AsyncCursor_gen_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    if (type != CPyType_brownie___insert_AsyncCursor_gen) {
        PyErr_SetString(PyExc_TypeError, "interpreted classes cannot inherit from compiled");
        return NULL;
    }
    PyObject *self = CPyDef_brownie_____mypyc__insert_AsyncCursor_gen_setup((PyObject*)type);
    if (self == NULL)
        return NULL;
    return self;
}

static int
brownie___insert_AsyncCursor_gen_traverse(y____db___brownie___insert_AsyncCursor_genObject *self, visitproc visit, void *arg)
{
    Py_VISIT(self->___mypyc_generator_attribute__self);
    Py_VISIT(self->___mypyc_generator_attribute__table);
    Py_VISIT(self->___mypyc_generator_attribute__values);
    return 0;
}

static int
brownie___insert_AsyncCursor_gen_clear(y____db___brownie___insert_AsyncCursor_genObject *self)
{
    Py_CLEAR(self->___mypyc_generator_attribute__self);
    Py_CLEAR(self->___mypyc_generator_attribute__table);
    Py_CLEAR(self->___mypyc_generator_attribute__values);
    return 0;
}

static void
brownie___insert_AsyncCursor_gen_dealloc(y____db___brownie___insert_AsyncCursor_genObject *self)
{
    PyObject_GC_UnTrack(self);
    if (brownie___insert_AsyncCursor_gen_free_instance == NULL) {
        brownie___insert_AsyncCursor_gen_free_instance = self;
        Py_CLEAR(self->___mypyc_generator_attribute__self);
        Py_CLEAR(self->___mypyc_generator_attribute__table);
        Py_CLEAR(self->___mypyc_generator_attribute__values);
        self->___mypyc_next_label__ = -113;
        return;
    }
    CPy_TRASHCAN_BEGIN(self, brownie___insert_AsyncCursor_gen_dealloc)
    brownie___insert_AsyncCursor_gen_clear(self);
    Py_TYPE(self)->tp_free((PyObject *)self);
    CPy_TRASHCAN_END(self)
    done: ;
}

static CPyVTableItem brownie___insert_AsyncCursor_gen_vtable[7];
static bool
CPyDef_brownie___insert_AsyncCursor_gen_trait_vtable_setup(void)
{
    CPyVTableItem brownie___insert_AsyncCursor_gen_vtable_scratch[] = {
        (CPyVTableItem)CPyDef_brownie___insert_AsyncCursor_gen_____mypyc_generator_helper__,
        (CPyVTableItem)CPyDef_brownie___insert_AsyncCursor_gen_____next__,
        (CPyVTableItem)CPyDef_brownie___insert_AsyncCursor_gen___send,
        (CPyVTableItem)CPyDef_brownie___insert_AsyncCursor_gen_____iter__,
        (CPyVTableItem)CPyDef_brownie___insert_AsyncCursor_gen___throw,
        (CPyVTableItem)CPyDef_brownie___insert_AsyncCursor_gen___close,
        (CPyVTableItem)CPyDef_brownie___insert_AsyncCursor_gen_____await__,
    };
    memcpy(brownie___insert_AsyncCursor_gen_vtable, brownie___insert_AsyncCursor_gen_vtable_scratch, sizeof(brownie___insert_AsyncCursor_gen_vtable));
    return 1;
}

static PyMethodDef brownie___insert_AsyncCursor_gen_methods[] = {
    {"__internal_mypyc_setup", (PyCFunction)CPyDef_brownie_____mypyc__insert_AsyncCursor_gen_setup, METH_O, NULL},
    {"__next__",
     (PyCFunction)CPyPy_brownie___insert_AsyncCursor_gen_____next__,
     METH_FASTCALL | METH_KEYWORDS, PyDoc_STR("__next__()\n--\n\n")},
    {"send",
     (PyCFunction)CPyPy_brownie___insert_AsyncCursor_gen___send,
     METH_FASTCALL | METH_KEYWORDS, PyDoc_STR("send($arg)\n--\n\n")},
    {"__iter__",
     (PyCFunction)CPyPy_brownie___insert_AsyncCursor_gen_____iter__,
     METH_FASTCALL | METH_KEYWORDS, PyDoc_STR("__iter__()\n--\n\n")},
    {"throw",
     (PyCFunction)CPyPy_brownie___insert_AsyncCursor_gen___throw,
     METH_FASTCALL | METH_KEYWORDS, PyDoc_STR(NULL)},
    {"close",
     (PyCFunction)CPyPy_brownie___insert_AsyncCursor_gen___close,
     METH_FASTCALL | METH_KEYWORDS, PyDoc_STR("close()\n--\n\n")},
    {"__await__",
     (PyCFunction)CPyPy_brownie___insert_AsyncCursor_gen_____await__,
     METH_FASTCALL | METH_KEYWORDS, PyDoc_STR("__await__()\n--\n\n")},
    {"__setstate__", (PyCFunction)CPyPickle_SetState, METH_O, NULL},
    {"__getstate__", (PyCFunction)CPyPickle_GetState, METH_NOARGS, NULL},
    {NULL}  /* Sentinel */
};

static PyTypeObject CPyType_brownie___insert_AsyncCursor_gen_template_ = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "insert_AsyncCursor_gen",
    .tp_new = brownie___insert_AsyncCursor_gen_new,
    .tp_dealloc = (destructor)brownie___insert_AsyncCursor_gen_dealloc,
    .tp_traverse = (traverseproc)brownie___insert_AsyncCursor_gen_traverse,
    .tp_clear = (inquiry)brownie___insert_AsyncCursor_gen_clear,
    .tp_methods = brownie___insert_AsyncCursor_gen_methods,
    .tp_iter = CPyDef_brownie___insert_AsyncCursor_gen_____iter__,
    .tp_iternext = CPyDef_brownie___insert_AsyncCursor_gen_____next__,
    .tp_as_async = &brownie___insert_AsyncCursor_gen_as_async,
    .tp_basicsize = sizeof(y____db___brownie___insert_AsyncCursor_genObject),
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HEAPTYPE | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_HAVE_GC,
    .tp_doc = PyDoc_STR("insert_AsyncCursor_gen()\n--\n\n"),
};
static PyTypeObject *CPyType_brownie___insert_AsyncCursor_gen_template = &CPyType_brownie___insert_AsyncCursor_gen_template_;

PyObject *CPyDef_brownie_____mypyc__insert_AsyncCursor_gen_setup(PyObject *cpy_r_type)
{
    PyTypeObject *type = (PyTypeObject*)cpy_r_type;
    y____db___brownie___insert_AsyncCursor_genObject *self;
    if (brownie___insert_AsyncCursor_gen_free_instance != NULL) {
        self = brownie___insert_AsyncCursor_gen_free_instance;
        brownie___insert_AsyncCursor_gen_free_instance = NULL;
        Py_SET_REFCNT(self, 1);
        PyObject_GC_Track(self);
        return (PyObject *)self;
    }
    self = (y____db___brownie___insert_AsyncCursor_genObject *)type->tp_alloc(type, 0);
    if (self == NULL)
        return NULL;
    self->vtable = brownie___insert_AsyncCursor_gen_vtable;
    self->___mypyc_next_label__ = -113;
    return (PyObject *)self;
}

PyObject *CPyDef_brownie___insert_AsyncCursor_gen(void)
{
    PyObject *self = CPyDef_brownie_____mypyc__insert_AsyncCursor_gen_setup((PyObject *)CPyType_brownie___insert_AsyncCursor_gen);
    if (self == NULL)
        return NULL;
    return self;
}


static PyAsyncMethods brownie___fetchone_AsyncCursor_gen_as_async = {
    .am_await = CPyDef_brownie___fetchone_AsyncCursor_gen_____await__,
};
PyObject *CPyDef_brownie_____mypyc__fetchone_AsyncCursor_gen_setup(PyObject *cpy_r_type);
PyObject *CPyDef_brownie___fetchone_AsyncCursor_gen(void);

static PyObject *
brownie___fetchone_AsyncCursor_gen_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    if (type != CPyType_brownie___fetchone_AsyncCursor_gen) {
        PyErr_SetString(PyExc_TypeError, "interpreted classes cannot inherit from compiled");
        return NULL;
    }
    PyObject *self = CPyDef_brownie_____mypyc__fetchone_AsyncCursor_gen_setup((PyObject*)type);
    if (self == NULL)
        return NULL;
    return self;
}

static int
brownie___fetchone_AsyncCursor_gen_traverse(y____db___brownie___fetchone_AsyncCursor_genObject *self, visitproc visit, void *arg)
{
    Py_VISIT(self->___mypyc_generator_attribute__self);
    Py_VISIT(self->___mypyc_generator_attribute__cmd);
    Py_VISIT(self->___mypyc_generator_attribute__args);
    Py_VISIT(self->___mypyc_temp__13);
    Py_VISIT(self->___mypyc_temp__14.f0);
    Py_VISIT(self->___mypyc_temp__14.f1);
    Py_VISIT(self->___mypyc_temp__14.f2);
    Py_VISIT(self->___mypyc_temp__15);
    Py_VISIT(self->___mypyc_temp__16);
    Py_VISIT(self->___mypyc_temp__18);
    Py_VISIT(self->___mypyc_temp__19.f0);
    Py_VISIT(self->___mypyc_temp__19.f1);
    Py_VISIT(self->___mypyc_temp__19.f2);
    Py_VISIT(self->___mypyc_generator_attribute__execute);
    Py_VISIT(self->___mypyc_temp__20);
    Py_VISIT(self->___mypyc_temp__21);
    Py_VISIT(self->___mypyc_temp__23);
    Py_VISIT(self->___mypyc_temp__24.f0);
    Py_VISIT(self->___mypyc_temp__24.f1);
    Py_VISIT(self->___mypyc_temp__24.f2);
    Py_VISIT(self->___mypyc_generator_attribute__cursor);
    Py_VISIT(self->___mypyc_temp__25);
    Py_VISIT(self->___mypyc_temp__26.f0);
    Py_VISIT(self->___mypyc_temp__26.f1);
    Py_VISIT(self->___mypyc_temp__26.f2);
    Py_VISIT(self->___mypyc_generator_attribute__row);
    Py_VISIT(self->___mypyc_temp__27);
    Py_VISIT(self->___mypyc_temp__28);
    Py_VISIT(self->___mypyc_temp__29);
    Py_VISIT(self->___mypyc_temp__30);
    Py_VISIT(self->___mypyc_generator_attribute__i);
    Py_VISIT(self->___mypyc_temp__31.f0);
    Py_VISIT(self->___mypyc_temp__31.f1);
    Py_VISIT(self->___mypyc_temp__31.f2);
    Py_VISIT(self->___mypyc_temp__32);
    Py_VISIT(self->___mypyc_temp__33.f0);
    Py_VISIT(self->___mypyc_temp__33.f1);
    Py_VISIT(self->___mypyc_temp__33.f2);
    Py_VISIT(self->___mypyc_temp__34);
    Py_VISIT(self->___mypyc_temp__35.f0);
    Py_VISIT(self->___mypyc_temp__35.f1);
    Py_VISIT(self->___mypyc_temp__35.f2);
    Py_VISIT(self->___mypyc_temp__36);
    Py_VISIT(self->___mypyc_temp__37.f0);
    Py_VISIT(self->___mypyc_temp__37.f1);
    Py_VISIT(self->___mypyc_temp__37.f2);
    Py_VISIT(self->___mypyc_temp__38);
    Py_VISIT(self->___mypyc_temp__39.f0);
    Py_VISIT(self->___mypyc_temp__39.f1);
    Py_VISIT(self->___mypyc_temp__39.f2);
    Py_VISIT(self->___mypyc_temp__40);
    Py_VISIT(self->___mypyc_temp__41.f0);
    Py_VISIT(self->___mypyc_temp__41.f1);
    Py_VISIT(self->___mypyc_temp__41.f2);
    return 0;
}

static int
brownie___fetchone_AsyncCursor_gen_clear(y____db___brownie___fetchone_AsyncCursor_genObject *self)
{
    Py_CLEAR(self->___mypyc_generator_attribute__self);
    Py_CLEAR(self->___mypyc_generator_attribute__cmd);
    Py_CLEAR(self->___mypyc_generator_attribute__args);
    Py_CLEAR(self->___mypyc_temp__13);
    Py_CLEAR(self->___mypyc_temp__14.f0);
    Py_CLEAR(self->___mypyc_temp__14.f1);
    Py_CLEAR(self->___mypyc_temp__14.f2);
    Py_CLEAR(self->___mypyc_temp__15);
    Py_CLEAR(self->___mypyc_temp__16);
    Py_CLEAR(self->___mypyc_temp__18);
    Py_CLEAR(self->___mypyc_temp__19.f0);
    Py_CLEAR(self->___mypyc_temp__19.f1);
    Py_CLEAR(self->___mypyc_temp__19.f2);
    Py_CLEAR(self->___mypyc_generator_attribute__execute);
    Py_CLEAR(self->___mypyc_temp__20);
    Py_CLEAR(self->___mypyc_temp__21);
    Py_CLEAR(self->___mypyc_temp__23);
    Py_CLEAR(self->___mypyc_temp__24.f0);
    Py_CLEAR(self->___mypyc_temp__24.f1);
    Py_CLEAR(self->___mypyc_temp__24.f2);
    Py_CLEAR(self->___mypyc_generator_attribute__cursor);
    Py_CLEAR(self->___mypyc_temp__25);
    Py_CLEAR(self->___mypyc_temp__26.f0);
    Py_CLEAR(self->___mypyc_temp__26.f1);
    Py_CLEAR(self->___mypyc_temp__26.f2);
    Py_CLEAR(self->___mypyc_generator_attribute__row);
    Py_CLEAR(self->___mypyc_temp__27);
    Py_CLEAR(self->___mypyc_temp__28);
    Py_CLEAR(self->___mypyc_temp__29);
    Py_CLEAR(self->___mypyc_temp__30);
    Py_CLEAR(self->___mypyc_generator_attribute__i);
    Py_CLEAR(self->___mypyc_temp__31.f0);
    Py_CLEAR(self->___mypyc_temp__31.f1);
    Py_CLEAR(self->___mypyc_temp__31.f2);
    Py_CLEAR(self->___mypyc_temp__32);
    Py_CLEAR(self->___mypyc_temp__33.f0);
    Py_CLEAR(self->___mypyc_temp__33.f1);
    Py_CLEAR(self->___mypyc_temp__33.f2);
    Py_CLEAR(self->___mypyc_temp__34);
    Py_CLEAR(self->___mypyc_temp__35.f0);
    Py_CLEAR(self->___mypyc_temp__35.f1);
    Py_CLEAR(self->___mypyc_temp__35.f2);
    Py_CLEAR(self->___mypyc_temp__36);
    Py_CLEAR(self->___mypyc_temp__37.f0);
    Py_CLEAR(self->___mypyc_temp__37.f1);
    Py_CLEAR(self->___mypyc_temp__37.f2);
    Py_CLEAR(self->___mypyc_temp__38);
    Py_CLEAR(self->___mypyc_temp__39.f0);
    Py_CLEAR(self->___mypyc_temp__39.f1);
    Py_CLEAR(self->___mypyc_temp__39.f2);
    Py_CLEAR(self->___mypyc_temp__40);
    Py_CLEAR(self->___mypyc_temp__41.f0);
    Py_CLEAR(self->___mypyc_temp__41.f1);
    Py_CLEAR(self->___mypyc_temp__41.f2);
    return 0;
}

static void
brownie___fetchone_AsyncCursor_gen_dealloc(y____db___brownie___fetchone_AsyncCursor_genObject *self)
{
    PyObject_GC_UnTrack(self);
    if (brownie___fetchone_AsyncCursor_gen_free_instance == NULL) {
        brownie___fetchone_AsyncCursor_gen_free_instance = self;
        Py_CLEAR(self->___mypyc_generator_attribute__self);
        Py_CLEAR(self->___mypyc_generator_attribute__cmd);
        Py_CLEAR(self->___mypyc_generator_attribute__args);
        self->___mypyc_next_label__ = -113;
        Py_CLEAR(self->___mypyc_temp__13);
        Py_CLEAR(self->___mypyc_temp__14.f0);
        Py_CLEAR(self->___mypyc_temp__14.f1);
        Py_CLEAR(self->___mypyc_temp__14.f2);
        Py_CLEAR(self->___mypyc_temp__15);
        Py_CLEAR(self->___mypyc_temp__16);
        self->___mypyc_temp__17 = 2;
        Py_CLEAR(self->___mypyc_temp__18);
        Py_CLEAR(self->___mypyc_temp__19.f0);
        Py_CLEAR(self->___mypyc_temp__19.f1);
        Py_CLEAR(self->___mypyc_temp__19.f2);
        Py_CLEAR(self->___mypyc_generator_attribute__execute);
        Py_CLEAR(self->___mypyc_temp__20);
        Py_CLEAR(self->___mypyc_temp__21);
        self->___mypyc_temp__22 = 2;
        Py_CLEAR(self->___mypyc_temp__23);
        Py_CLEAR(self->___mypyc_temp__24.f0);
        Py_CLEAR(self->___mypyc_temp__24.f1);
        Py_CLEAR(self->___mypyc_temp__24.f2);
        Py_CLEAR(self->___mypyc_generator_attribute__cursor);
        Py_CLEAR(self->___mypyc_temp__25);
        Py_CLEAR(self->___mypyc_temp__26.f0);
        Py_CLEAR(self->___mypyc_temp__26.f1);
        Py_CLEAR(self->___mypyc_temp__26.f2);
        Py_CLEAR(self->___mypyc_generator_attribute__row);
        Py_CLEAR(self->___mypyc_temp__27);
        Py_CLEAR(self->___mypyc_temp__28);
        Py_CLEAR(self->___mypyc_temp__29);
        Py_CLEAR(self->___mypyc_temp__30);
        Py_CLEAR(self->___mypyc_generator_attribute__i);
        Py_CLEAR(self->___mypyc_temp__31.f0);
        Py_CLEAR(self->___mypyc_temp__31.f1);
        Py_CLEAR(self->___mypyc_temp__31.f2);
        Py_CLEAR(self->___mypyc_temp__32);
        Py_CLEAR(self->___mypyc_temp__33.f0);
        Py_CLEAR(self->___mypyc_temp__33.f1);
        Py_CLEAR(self->___mypyc_temp__33.f2);
        Py_CLEAR(self->___mypyc_temp__34);
        Py_CLEAR(self->___mypyc_temp__35.f0);
        Py_CLEAR(self->___mypyc_temp__35.f1);
        Py_CLEAR(self->___mypyc_temp__35.f2);
        Py_CLEAR(self->___mypyc_temp__36);
        Py_CLEAR(self->___mypyc_temp__37.f0);
        Py_CLEAR(self->___mypyc_temp__37.f1);
        Py_CLEAR(self->___mypyc_temp__37.f2);
        Py_CLEAR(self->___mypyc_temp__38);
        Py_CLEAR(self->___mypyc_temp__39.f0);
        Py_CLEAR(self->___mypyc_temp__39.f1);
        Py_CLEAR(self->___mypyc_temp__39.f2);
        Py_CLEAR(self->___mypyc_temp__40);
        Py_CLEAR(self->___mypyc_temp__41.f0);
        Py_CLEAR(self->___mypyc_temp__41.f1);
        Py_CLEAR(self->___mypyc_temp__41.f2);
        return;
    }
    CPy_TRASHCAN_BEGIN(self, brownie___fetchone_AsyncCursor_gen_dealloc)
    brownie___fetchone_AsyncCursor_gen_clear(self);
    Py_TYPE(self)->tp_free((PyObject *)self);
    CPy_TRASHCAN_END(self)
    done: ;
}

static CPyVTableItem brownie___fetchone_AsyncCursor_gen_vtable[7];
static bool
CPyDef_brownie___fetchone_AsyncCursor_gen_trait_vtable_setup(void)
{
    CPyVTableItem brownie___fetchone_AsyncCursor_gen_vtable_scratch[] = {
        (CPyVTableItem)CPyDef_brownie___fetchone_AsyncCursor_gen_____mypyc_generator_helper__,
        (CPyVTableItem)CPyDef_brownie___fetchone_AsyncCursor_gen_____next__,
        (CPyVTableItem)CPyDef_brownie___fetchone_AsyncCursor_gen___send,
        (CPyVTableItem)CPyDef_brownie___fetchone_AsyncCursor_gen_____iter__,
        (CPyVTableItem)CPyDef_brownie___fetchone_AsyncCursor_gen___throw,
        (CPyVTableItem)CPyDef_brownie___fetchone_AsyncCursor_gen___close,
        (CPyVTableItem)CPyDef_brownie___fetchone_AsyncCursor_gen_____await__,
    };
    memcpy(brownie___fetchone_AsyncCursor_gen_vtable, brownie___fetchone_AsyncCursor_gen_vtable_scratch, sizeof(brownie___fetchone_AsyncCursor_gen_vtable));
    return 1;
}

static PyMethodDef brownie___fetchone_AsyncCursor_gen_methods[] = {
    {"__internal_mypyc_setup", (PyCFunction)CPyDef_brownie_____mypyc__fetchone_AsyncCursor_gen_setup, METH_O, NULL},
    {"__next__",
     (PyCFunction)CPyPy_brownie___fetchone_AsyncCursor_gen_____next__,
     METH_FASTCALL | METH_KEYWORDS, PyDoc_STR("__next__()\n--\n\n")},
    {"send",
     (PyCFunction)CPyPy_brownie___fetchone_AsyncCursor_gen___send,
     METH_FASTCALL | METH_KEYWORDS, PyDoc_STR("send($arg)\n--\n\n")},
    {"__iter__",
     (PyCFunction)CPyPy_brownie___fetchone_AsyncCursor_gen_____iter__,
     METH_FASTCALL | METH_KEYWORDS, PyDoc_STR("__iter__()\n--\n\n")},
    {"throw",
     (PyCFunction)CPyPy_brownie___fetchone_AsyncCursor_gen___throw,
     METH_FASTCALL | METH_KEYWORDS, PyDoc_STR(NULL)},
    {"close",
     (PyCFunction)CPyPy_brownie___fetchone_AsyncCursor_gen___close,
     METH_FASTCALL | METH_KEYWORDS, PyDoc_STR("close()\n--\n\n")},
    {"__await__",
     (PyCFunction)CPyPy_brownie___fetchone_AsyncCursor_gen_____await__,
     METH_FASTCALL | METH_KEYWORDS, PyDoc_STR("__await__()\n--\n\n")},
    {"__setstate__", (PyCFunction)CPyPickle_SetState, METH_O, NULL},
    {"__getstate__", (PyCFunction)CPyPickle_GetState, METH_NOARGS, NULL},
    {NULL}  /* Sentinel */
};

static PyTypeObject CPyType_brownie___fetchone_AsyncCursor_gen_template_ = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "fetchone_AsyncCursor_gen",
    .tp_new = brownie___fetchone_AsyncCursor_gen_new,
    .tp_dealloc = (destructor)brownie___fetchone_AsyncCursor_gen_dealloc,
    .tp_traverse = (traverseproc)brownie___fetchone_AsyncCursor_gen_traverse,
    .tp_clear = (inquiry)brownie___fetchone_AsyncCursor_gen_clear,
    .tp_methods = brownie___fetchone_AsyncCursor_gen_methods,
    .tp_iter = CPyDef_brownie___fetchone_AsyncCursor_gen_____iter__,
    .tp_iternext = CPyDef_brownie___fetchone_AsyncCursor_gen_____next__,
    .tp_as_async = &brownie___fetchone_AsyncCursor_gen_as_async,
    .tp_basicsize = sizeof(y____db___brownie___fetchone_AsyncCursor_genObject),
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HEAPTYPE | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_HAVE_GC,
    .tp_doc = PyDoc_STR("fetchone_AsyncCursor_gen()\n--\n\n"),
};
static PyTypeObject *CPyType_brownie___fetchone_AsyncCursor_gen_template = &CPyType_brownie___fetchone_AsyncCursor_gen_template_;

PyObject *CPyDef_brownie_____mypyc__fetchone_AsyncCursor_gen_setup(PyObject *cpy_r_type)
{
    PyTypeObject *type = (PyTypeObject*)cpy_r_type;
    y____db___brownie___fetchone_AsyncCursor_genObject *self;
    if (brownie___fetchone_AsyncCursor_gen_free_instance != NULL) {
        self = brownie___fetchone_AsyncCursor_gen_free_instance;
        brownie___fetchone_AsyncCursor_gen_free_instance = NULL;
        Py_SET_REFCNT(self, 1);
        PyObject_GC_Track(self);
        return (PyObject *)self;
    }
    self = (y____db___brownie___fetchone_AsyncCursor_genObject *)type->tp_alloc(type, 0);
    if (self == NULL)
        return NULL;
    self->vtable = brownie___fetchone_AsyncCursor_gen_vtable;
    self->___mypyc_next_label__ = -113;
    self->___mypyc_temp__14 = (tuple_T3OOO) { NULL, NULL, NULL };
    self->___mypyc_temp__17 = 2;
    self->___mypyc_temp__19 = (tuple_T3OOO) { NULL, NULL, NULL };
    self->___mypyc_temp__22 = 2;
    self->___mypyc_temp__24 = (tuple_T3OOO) { NULL, NULL, NULL };
    self->___mypyc_temp__26 = (tuple_T3OOO) { NULL, NULL, NULL };
    self->___mypyc_temp__31 = (tuple_T3OOO) { NULL, NULL, NULL };
    self->___mypyc_temp__33 = (tuple_T3OOO) { NULL, NULL, NULL };
    self->___mypyc_temp__35 = (tuple_T3OOO) { NULL, NULL, NULL };
    self->___mypyc_temp__37 = (tuple_T3OOO) { NULL, NULL, NULL };
    self->___mypyc_temp__39 = (tuple_T3OOO) { NULL, NULL, NULL };
    self->___mypyc_temp__41 = (tuple_T3OOO) { NULL, NULL, NULL };
    return (PyObject *)self;
}

PyObject *CPyDef_brownie___fetchone_AsyncCursor_gen(void)
{
    PyObject *self = CPyDef_brownie_____mypyc__fetchone_AsyncCursor_gen_setup((PyObject *)CPyType_brownie___fetchone_AsyncCursor_gen);
    if (self == NULL)
        return NULL;
    return self;
}


static PyAsyncMethods brownie____get_deployment_gen_as_async = {
    .am_await = CPyDef_brownie____get_deployment_gen_____await__,
};
PyObject *CPyDef_brownie_____mypyc___3_get_deployment_gen_setup(PyObject *cpy_r_type);
PyObject *CPyDef_brownie____get_deployment_gen(void);

static PyObject *
brownie____get_deployment_gen_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    if (type != CPyType_brownie____get_deployment_gen) {
        PyErr_SetString(PyExc_TypeError, "interpreted classes cannot inherit from compiled");
        return NULL;
    }
    PyObject *self = CPyDef_brownie_____mypyc___3_get_deployment_gen_setup((PyObject*)type);
    if (self == NULL)
        return NULL;
    return self;
}

static int
brownie____get_deployment_gen_traverse(y____db___brownie____get_deployment_genObject *self, visitproc visit, void *arg)
{
    Py_VISIT(self->___mypyc_generator_attribute__address);
    Py_VISIT(self->___mypyc_generator_attribute__alias);
    Py_VISIT(self->___mypyc_generator_attribute__skip_source_keys);
    Py_VISIT(self->___mypyc_generator_attribute__where_clause);
    Py_VISIT(self->___mypyc_temp__42);
    Py_VISIT(self->___mypyc_temp__43.f0);
    Py_VISIT(self->___mypyc_temp__43.f1);
    Py_VISIT(self->___mypyc_temp__43.f2);
    Py_VISIT(self->___mypyc_generator_attribute__row);
    Py_VISIT(self->___mypyc_temp__44.f0);
    Py_VISIT(self->___mypyc_temp__44.f1);
    Py_VISIT(self->___mypyc_temp__44.f2);
    Py_VISIT(self->___mypyc_generator_attribute__build_json);
    Py_VISIT(self->___mypyc_generator_attribute__path_map);
    Py_VISIT(self->___mypyc_temp__45);
    Py_VISIT(self->___mypyc_temp__46);
    Py_VISIT(self->___mypyc_temp__49);
    Py_VISIT(self->___mypyc_generator_attribute__val);
    Py_VISIT(self->___mypyc_generator_attribute__source_key);
    Py_VISIT(self->___mypyc_temp__50);
    Py_VISIT(self->___mypyc_temp__51.f0);
    Py_VISIT(self->___mypyc_temp__51.f1);
    Py_VISIT(self->___mypyc_temp__51.f2);
    Py_VISIT(self->___mypyc_generator_attribute__sources);
    Py_VISIT(self->___mypyc_temp__52);
    Py_VISIT(self->___mypyc_temp__53);
    Py_VISIT(self->___mypyc_temp__56);
    Py_VISIT(self->___mypyc_generator_attribute__k);
    Py_VISIT(self->___mypyc_generator_attribute__v);
    Py_VISIT(self->___mypyc_generator_attribute__pc_map);
    Py_VISIT(self->___mypyc_temp__57);
    Py_VISIT(self->___mypyc_temp__58);
    Py_VISIT(self->___mypyc_temp__61);
    Py_VISIT(self->___mypyc_generator_attribute__key);
    Py_VISIT(self->___mypyc_temp__2_0);
    return 0;
}

static int
brownie____get_deployment_gen_clear(y____db___brownie____get_deployment_genObject *self)
{
    Py_CLEAR(self->___mypyc_generator_attribute__address);
    Py_CLEAR(self->___mypyc_generator_attribute__alias);
    Py_CLEAR(self->___mypyc_generator_attribute__skip_source_keys);
    Py_CLEAR(self->___mypyc_generator_attribute__where_clause);
    Py_CLEAR(self->___mypyc_temp__42);
    Py_CLEAR(self->___mypyc_temp__43.f0);
    Py_CLEAR(self->___mypyc_temp__43.f1);
    Py_CLEAR(self->___mypyc_temp__43.f2);
    Py_CLEAR(self->___mypyc_generator_attribute__row);
    Py_CLEAR(self->___mypyc_temp__44.f0);
    Py_CLEAR(self->___mypyc_temp__44.f1);
    Py_CLEAR(self->___mypyc_temp__44.f2);
    Py_CLEAR(self->___mypyc_generator_attribute__build_json);
    Py_CLEAR(self->___mypyc_generator_attribute__path_map);
    Py_CLEAR(self->___mypyc_temp__45);
    Py_CLEAR(self->___mypyc_temp__46);
    Py_CLEAR(self->___mypyc_temp__49);
    Py_CLEAR(self->___mypyc_generator_attribute__val);
    Py_CLEAR(self->___mypyc_generator_attribute__source_key);
    Py_CLEAR(self->___mypyc_temp__50);
    Py_CLEAR(self->___mypyc_temp__51.f0);
    Py_CLEAR(self->___mypyc_temp__51.f1);
    Py_CLEAR(self->___mypyc_temp__51.f2);
    Py_CLEAR(self->___mypyc_generator_attribute__sources);
    Py_CLEAR(self->___mypyc_temp__52);
    Py_CLEAR(self->___mypyc_temp__53);
    Py_CLEAR(self->___mypyc_temp__56);
    Py_CLEAR(self->___mypyc_generator_attribute__k);
    Py_CLEAR(self->___mypyc_generator_attribute__v);
    Py_CLEAR(self->___mypyc_generator_attribute__pc_map);
    Py_CLEAR(self->___mypyc_temp__57);
    Py_CLEAR(self->___mypyc_temp__58);
    Py_CLEAR(self->___mypyc_temp__61);
    Py_CLEAR(self->___mypyc_generator_attribute__key);
    Py_CLEAR(self->___mypyc_temp__2_0);
    return 0;
}

static void
brownie____get_deployment_gen_dealloc(y____db___brownie____get_deployment_genObject *self)
{
    PyObject_GC_UnTrack(self);
    if (brownie____get_deployment_gen_free_instance == NULL) {
        brownie____get_deployment_gen_free_instance = self;
        Py_CLEAR(self->___mypyc_generator_attribute__address);
        Py_CLEAR(self->___mypyc_generator_attribute__alias);
        Py_CLEAR(self->___mypyc_generator_attribute__skip_source_keys);
        self->___mypyc_next_label__ = -113;
        Py_CLEAR(self->___mypyc_generator_attribute__where_clause);
        Py_CLEAR(self->___mypyc_temp__42);
        Py_CLEAR(self->___mypyc_temp__43.f0);
        Py_CLEAR(self->___mypyc_temp__43.f1);
        Py_CLEAR(self->___mypyc_temp__43.f2);
        Py_CLEAR(self->___mypyc_generator_attribute__row);
        Py_CLEAR(self->___mypyc_temp__44.f0);
        Py_CLEAR(self->___mypyc_temp__44.f1);
        Py_CLEAR(self->___mypyc_temp__44.f2);
        Py_CLEAR(self->___mypyc_generator_attribute__build_json);
        Py_CLEAR(self->___mypyc_generator_attribute__path_map);
        Py_CLEAR(self->___mypyc_temp__45);
        Py_CLEAR(self->___mypyc_temp__46);
        self->___mypyc_temp__47 = CPY_INT_TAG;
        self->___mypyc_temp__48 = -113;
        Py_CLEAR(self->___mypyc_temp__49);
        Py_CLEAR(self->___mypyc_generator_attribute__val);
        Py_CLEAR(self->___mypyc_generator_attribute__source_key);
        Py_CLEAR(self->___mypyc_temp__50);
        Py_CLEAR(self->___mypyc_temp__51.f0);
        Py_CLEAR(self->___mypyc_temp__51.f1);
        Py_CLEAR(self->___mypyc_temp__51.f2);
        Py_CLEAR(self->___mypyc_generator_attribute__sources);
        Py_CLEAR(self->___mypyc_temp__52);
        Py_CLEAR(self->___mypyc_temp__53);
        self->___mypyc_temp__54 = CPY_INT_TAG;
        self->___mypyc_temp__55 = -113;
        Py_CLEAR(self->___mypyc_temp__56);
        Py_CLEAR(self->___mypyc_generator_attribute__k);
        Py_CLEAR(self->___mypyc_generator_attribute__v);
        Py_CLEAR(self->___mypyc_generator_attribute__pc_map);
        Py_CLEAR(self->___mypyc_temp__57);
        Py_CLEAR(self->___mypyc_temp__58);
        self->___mypyc_temp__59 = CPY_INT_TAG;
        self->___mypyc_temp__60 = -113;
        Py_CLEAR(self->___mypyc_temp__61);
        Py_CLEAR(self->___mypyc_generator_attribute__key);
        Py_CLEAR(self->___mypyc_temp__2_0);
        return;
    }
    CPy_TRASHCAN_BEGIN(self, brownie____get_deployment_gen_dealloc)
    brownie____get_deployment_gen_clear(self);
    Py_TYPE(self)->tp_free((PyObject *)self);
    CPy_TRASHCAN_END(self)
    done: ;
}

static CPyVTableItem brownie____get_deployment_gen_vtable[7];
static bool
CPyDef_brownie____get_deployment_gen_trait_vtable_setup(void)
{
    CPyVTableItem brownie____get_deployment_gen_vtable_scratch[] = {
        (CPyVTableItem)CPyDef_brownie____get_deployment_gen_____mypyc_generator_helper__,
        (CPyVTableItem)CPyDef_brownie____get_deployment_gen_____next__,
        (CPyVTableItem)CPyDef_brownie____get_deployment_gen___send,
        (CPyVTableItem)CPyDef_brownie____get_deployment_gen_____iter__,
        (CPyVTableItem)CPyDef_brownie____get_deployment_gen___throw,
        (CPyVTableItem)CPyDef_brownie____get_deployment_gen___close,
        (CPyVTableItem)CPyDef_brownie____get_deployment_gen_____await__,
    };
    memcpy(brownie____get_deployment_gen_vtable, brownie____get_deployment_gen_vtable_scratch, sizeof(brownie____get_deployment_gen_vtable));
    return 1;
}

static PyMethodDef brownie____get_deployment_gen_methods[] = {
    {"__internal_mypyc_setup", (PyCFunction)CPyDef_brownie_____mypyc___3_get_deployment_gen_setup, METH_O, NULL},
    {"__next__",
     (PyCFunction)CPyPy_brownie____get_deployment_gen_____next__,
     METH_FASTCALL | METH_KEYWORDS, PyDoc_STR("__next__()\n--\n\n")},
    {"send",
     (PyCFunction)CPyPy_brownie____get_deployment_gen___send,
     METH_FASTCALL | METH_KEYWORDS, PyDoc_STR("send($arg)\n--\n\n")},
    {"__iter__",
     (PyCFunction)CPyPy_brownie____get_deployment_gen_____iter__,
     METH_FASTCALL | METH_KEYWORDS, PyDoc_STR("__iter__()\n--\n\n")},
    {"throw",
     (PyCFunction)CPyPy_brownie____get_deployment_gen___throw,
     METH_FASTCALL | METH_KEYWORDS, PyDoc_STR(NULL)},
    {"close",
     (PyCFunction)CPyPy_brownie____get_deployment_gen___close,
     METH_FASTCALL | METH_KEYWORDS, PyDoc_STR("close()\n--\n\n")},
    {"__await__",
     (PyCFunction)CPyPy_brownie____get_deployment_gen_____await__,
     METH_FASTCALL | METH_KEYWORDS, PyDoc_STR("__await__()\n--\n\n")},
    {"__setstate__", (PyCFunction)CPyPickle_SetState, METH_O, NULL},
    {"__getstate__", (PyCFunction)CPyPickle_GetState, METH_NOARGS, NULL},
    {NULL}  /* Sentinel */
};

static PyTypeObject CPyType_brownie____get_deployment_gen_template_ = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "_get_deployment_gen",
    .tp_new = brownie____get_deployment_gen_new,
    .tp_dealloc = (destructor)brownie____get_deployment_gen_dealloc,
    .tp_traverse = (traverseproc)brownie____get_deployment_gen_traverse,
    .tp_clear = (inquiry)brownie____get_deployment_gen_clear,
    .tp_methods = brownie____get_deployment_gen_methods,
    .tp_iter = CPyDef_brownie____get_deployment_gen_____iter__,
    .tp_iternext = CPyDef_brownie____get_deployment_gen_____next__,
    .tp_as_async = &brownie____get_deployment_gen_as_async,
    .tp_basicsize = sizeof(y____db___brownie____get_deployment_genObject),
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HEAPTYPE | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_HAVE_GC,
    .tp_doc = PyDoc_STR("_get_deployment_gen()\n--\n\n"),
};
static PyTypeObject *CPyType_brownie____get_deployment_gen_template = &CPyType_brownie____get_deployment_gen_template_;

PyObject *CPyDef_brownie_____mypyc___3_get_deployment_gen_setup(PyObject *cpy_r_type)
{
    PyTypeObject *type = (PyTypeObject*)cpy_r_type;
    y____db___brownie____get_deployment_genObject *self;
    if (brownie____get_deployment_gen_free_instance != NULL) {
        self = brownie____get_deployment_gen_free_instance;
        brownie____get_deployment_gen_free_instance = NULL;
        Py_SET_REFCNT(self, 1);
        PyObject_GC_Track(self);
        return (PyObject *)self;
    }
    self = (y____db___brownie____get_deployment_genObject *)type->tp_alloc(type, 0);
    if (self == NULL)
        return NULL;
    self->vtable = brownie____get_deployment_gen_vtable;
    self->___mypyc_next_label__ = -113;
    self->___mypyc_temp__43 = (tuple_T3OOO) { NULL, NULL, NULL };
    self->___mypyc_temp__44 = (tuple_T3OOO) { NULL, NULL, NULL };
    self->___mypyc_temp__47 = CPY_INT_TAG;
    self->___mypyc_temp__48 = -113;
    self->___mypyc_temp__51 = (tuple_T3OOO) { NULL, NULL, NULL };
    self->___mypyc_temp__54 = CPY_INT_TAG;
    self->___mypyc_temp__55 = -113;
    self->___mypyc_temp__59 = CPY_INT_TAG;
    self->___mypyc_temp__60 = -113;
    return (PyObject *)self;
}

PyObject *CPyDef_brownie____get_deployment_gen(void)
{
    PyObject *self = CPyDef_brownie_____mypyc___3_get_deployment_gen_setup((PyObject *)CPyType_brownie____get_deployment_gen);
    if (self == NULL)
        return NULL;
    return self;
}


static PyAsyncMethods brownie_____fetch_source_for_hash_gen_as_async = {
    .am_await = CPyDef_brownie_____fetch_source_for_hash_gen_____await__,
};
PyObject *CPyDef_brownie_____mypyc___3__fetch_source_for_hash_gen_setup(PyObject *cpy_r_type);
PyObject *CPyDef_brownie_____fetch_source_for_hash_gen(void);

static PyObject *
brownie_____fetch_source_for_hash_gen_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    if (type != CPyType_brownie_____fetch_source_for_hash_gen) {
        PyErr_SetString(PyExc_TypeError, "interpreted classes cannot inherit from compiled");
        return NULL;
    }
    PyObject *self = CPyDef_brownie_____mypyc___3__fetch_source_for_hash_gen_setup((PyObject*)type);
    if (self == NULL)
        return NULL;
    return self;
}

static int
brownie_____fetch_source_for_hash_gen_traverse(y____db___brownie_____fetch_source_for_hash_genObject *self, visitproc visit, void *arg)
{
    Py_VISIT(self->___mypyc_generator_attribute__hashval);
    Py_VISIT(self->___mypyc_temp__62);
    Py_VISIT(self->___mypyc_temp__63.f0);
    Py_VISIT(self->___mypyc_temp__63.f1);
    Py_VISIT(self->___mypyc_temp__63.f2);
    Py_VISIT(self->___mypyc_generator_attribute__row);
    return 0;
}

static int
brownie_____fetch_source_for_hash_gen_clear(y____db___brownie_____fetch_source_for_hash_genObject *self)
{
    Py_CLEAR(self->___mypyc_generator_attribute__hashval);
    Py_CLEAR(self->___mypyc_temp__62);
    Py_CLEAR(self->___mypyc_temp__63.f0);
    Py_CLEAR(self->___mypyc_temp__63.f1);
    Py_CLEAR(self->___mypyc_temp__63.f2);
    Py_CLEAR(self->___mypyc_generator_attribute__row);
    return 0;
}

static void
brownie_____fetch_source_for_hash_gen_dealloc(y____db___brownie_____fetch_source_for_hash_genObject *self)
{
    PyObject_GC_UnTrack(self);
    if (brownie_____fetch_source_for_hash_gen_free_instance == NULL) {
        brownie_____fetch_source_for_hash_gen_free_instance = self;
        Py_CLEAR(self->___mypyc_generator_attribute__hashval);
        self->___mypyc_next_label__ = -113;
        Py_CLEAR(self->___mypyc_temp__62);
        Py_CLEAR(self->___mypyc_temp__63.f0);
        Py_CLEAR(self->___mypyc_temp__63.f1);
        Py_CLEAR(self->___mypyc_temp__63.f2);
        Py_CLEAR(self->___mypyc_generator_attribute__row);
        return;
    }
    CPy_TRASHCAN_BEGIN(self, brownie_____fetch_source_for_hash_gen_dealloc)
    brownie_____fetch_source_for_hash_gen_clear(self);
    Py_TYPE(self)->tp_free((PyObject *)self);
    CPy_TRASHCAN_END(self)
    done: ;
}

static CPyVTableItem brownie_____fetch_source_for_hash_gen_vtable[7];
static bool
CPyDef_brownie_____fetch_source_for_hash_gen_trait_vtable_setup(void)
{
    CPyVTableItem brownie_____fetch_source_for_hash_gen_vtable_scratch[] = {
        (CPyVTableItem)CPyDef_brownie_____fetch_source_for_hash_gen_____mypyc_generator_helper__,
        (CPyVTableItem)CPyDef_brownie_____fetch_source_for_hash_gen_____next__,
        (CPyVTableItem)CPyDef_brownie_____fetch_source_for_hash_gen___send,
        (CPyVTableItem)CPyDef_brownie_____fetch_source_for_hash_gen_____iter__,
        (CPyVTableItem)CPyDef_brownie_____fetch_source_for_hash_gen___throw,
        (CPyVTableItem)CPyDef_brownie_____fetch_source_for_hash_gen___close,
        (CPyVTableItem)CPyDef_brownie_____fetch_source_for_hash_gen_____await__,
    };
    memcpy(brownie_____fetch_source_for_hash_gen_vtable, brownie_____fetch_source_for_hash_gen_vtable_scratch, sizeof(brownie_____fetch_source_for_hash_gen_vtable));
    return 1;
}

static PyMethodDef brownie_____fetch_source_for_hash_gen_methods[] = {
    {"__internal_mypyc_setup", (PyCFunction)CPyDef_brownie_____mypyc___3__fetch_source_for_hash_gen_setup, METH_O, NULL},
    {"__next__",
     (PyCFunction)CPyPy_brownie_____fetch_source_for_hash_gen_____next__,
     METH_FASTCALL | METH_KEYWORDS, PyDoc_STR("__next__()\n--\n\n")},
    {"send",
     (PyCFunction)CPyPy_brownie_____fetch_source_for_hash_gen___send,
     METH_FASTCALL | METH_KEYWORDS, PyDoc_STR("send($arg)\n--\n\n")},
    {"__iter__",
     (PyCFunction)CPyPy_brownie_____fetch_source_for_hash_gen_____iter__,
     METH_FASTCALL | METH_KEYWORDS, PyDoc_STR("__iter__()\n--\n\n")},
    {"throw",
     (PyCFunction)CPyPy_brownie_____fetch_source_for_hash_gen___throw,
     METH_FASTCALL | METH_KEYWORDS, PyDoc_STR(NULL)},
    {"close",
     (PyCFunction)CPyPy_brownie_____fetch_source_for_hash_gen___close,
     METH_FASTCALL | METH_KEYWORDS, PyDoc_STR("close()\n--\n\n")},
    {"__await__",
     (PyCFunction)CPyPy_brownie_____fetch_source_for_hash_gen_____await__,
     METH_FASTCALL | METH_KEYWORDS, PyDoc_STR("__await__()\n--\n\n")},
    {"__setstate__", (PyCFunction)CPyPickle_SetState, METH_O, NULL},
    {"__getstate__", (PyCFunction)CPyPickle_GetState, METH_NOARGS, NULL},
    {NULL}  /* Sentinel */
};

static PyTypeObject CPyType_brownie_____fetch_source_for_hash_gen_template_ = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "__fetch_source_for_hash_gen",
    .tp_new = brownie_____fetch_source_for_hash_gen_new,
    .tp_dealloc = (destructor)brownie_____fetch_source_for_hash_gen_dealloc,
    .tp_traverse = (traverseproc)brownie_____fetch_source_for_hash_gen_traverse,
    .tp_clear = (inquiry)brownie_____fetch_source_for_hash_gen_clear,
    .tp_methods = brownie_____fetch_source_for_hash_gen_methods,
    .tp_iter = CPyDef_brownie_____fetch_source_for_hash_gen_____iter__,
    .tp_iternext = CPyDef_brownie_____fetch_source_for_hash_gen_____next__,
    .tp_as_async = &brownie_____fetch_source_for_hash_gen_as_async,
    .tp_basicsize = sizeof(y____db___brownie_____fetch_source_for_hash_genObject),
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HEAPTYPE | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_HAVE_GC,
    .tp_doc = PyDoc_STR("__fetch_source_for_hash_gen()\n--\n\n"),
};
static PyTypeObject *CPyType_brownie_____fetch_source_for_hash_gen_template = &CPyType_brownie_____fetch_source_for_hash_gen_template_;

PyObject *CPyDef_brownie_____mypyc___3__fetch_source_for_hash_gen_setup(PyObject *cpy_r_type)
{
    PyTypeObject *type = (PyTypeObject*)cpy_r_type;
    y____db___brownie_____fetch_source_for_hash_genObject *self;
    if (brownie_____fetch_source_for_hash_gen_free_instance != NULL) {
        self = brownie_____fetch_source_for_hash_gen_free_instance;
        brownie_____fetch_source_for_hash_gen_free_instance = NULL;
        Py_SET_REFCNT(self, 1);
        PyObject_GC_Track(self);
        return (PyObject *)self;
    }
    self = (y____db___brownie_____fetch_source_for_hash_genObject *)type->tp_alloc(type, 0);
    if (self == NULL)
        return NULL;
    self->vtable = brownie_____fetch_source_for_hash_gen_vtable;
    self->___mypyc_next_label__ = -113;
    self->___mypyc_temp__63 = (tuple_T3OOO) { NULL, NULL, NULL };
    return (PyObject *)self;
}

PyObject *CPyDef_brownie_____fetch_source_for_hash_gen(void)
{
    PyObject *self = CPyDef_brownie_____mypyc___3__fetch_source_for_hash_gen_setup((PyObject *)CPyType_brownie_____fetch_source_for_hash_gen);
    if (self == NULL)
        return NULL;
    return self;
}

static PyMethodDef browniemodule_methods[] = {
    {"_get_select_statement", (PyCFunction)CPyPy_brownie____get_select_statement, METH_FASTCALL | METH_KEYWORDS, PyDoc_STR("_get_select_statement()\n--\n\n") /* docstring */},
    {"_get_deployment", (PyCFunction)CPyPy_brownie____get_deployment, METH_FASTCALL | METH_KEYWORDS, PyDoc_STR(NULL) /* docstring */},
    {"__fetch_source_for_hash", (PyCFunction)CPyPy_brownie_____fetch_source_for_hash, METH_FASTCALL | METH_KEYWORDS, PyDoc_STR("__fetch_source_for_hash(hashval)\n--\n\n") /* docstring */},
    {NULL, NULL, 0, NULL}
};

int CPyExec_y____db___brownie(PyObject *module)
{
    PyObject* modname = NULL;
    modname = PyObject_GetAttrString((PyObject *)CPyModule_y____db___brownie__internal, "__name__");
    CPyStatic_brownie___globals = PyModule_GetDict(CPyModule_y____db___brownie__internal);
    if (unlikely(CPyStatic_brownie___globals == NULL))
        goto fail;
    CPyType_brownie___connect_AsyncCursor_gen = (PyTypeObject *)CPyType_FromTemplate((PyObject *)CPyType_brownie___connect_AsyncCursor_gen_template, NULL, modname);
    if (unlikely(!CPyType_brownie___connect_AsyncCursor_gen))
        goto fail;
    CPyDef_brownie___connect_AsyncCursor_gen_trait_vtable_setup();
    CPyType_brownie___insert_AsyncCursor_gen = (PyTypeObject *)CPyType_FromTemplate((PyObject *)CPyType_brownie___insert_AsyncCursor_gen_template, NULL, modname);
    if (unlikely(!CPyType_brownie___insert_AsyncCursor_gen))
        goto fail;
    CPyDef_brownie___insert_AsyncCursor_gen_trait_vtable_setup();
    CPyType_brownie___fetchone_AsyncCursor_gen = (PyTypeObject *)CPyType_FromTemplate((PyObject *)CPyType_brownie___fetchone_AsyncCursor_gen_template, NULL, modname);
    if (unlikely(!CPyType_brownie___fetchone_AsyncCursor_gen))
        goto fail;
    CPyDef_brownie___fetchone_AsyncCursor_gen_trait_vtable_setup();
    CPyType_brownie____get_deployment_gen = (PyTypeObject *)CPyType_FromTemplate((PyObject *)CPyType_brownie____get_deployment_gen_template, NULL, modname);
    if (unlikely(!CPyType_brownie____get_deployment_gen))
        goto fail;
    CPyDef_brownie____get_deployment_gen_trait_vtable_setup();
    CPyType_brownie_____fetch_source_for_hash_gen = (PyTypeObject *)CPyType_FromTemplate((PyObject *)CPyType_brownie_____fetch_source_for_hash_gen_template, NULL, modname);
    if (unlikely(!CPyType_brownie_____fetch_source_for_hash_gen))
        goto fail;
    CPyDef_brownie_____fetch_source_for_hash_gen_trait_vtable_setup();
    if (CPyGlobalsInit() < 0)
        goto fail;
    char result = CPyDef_brownie_____top_level__();
    if (result == 2)
        goto fail;
    Py_DECREF(modname);
    return 0;
    fail:
    Py_CLEAR(CPyModule_y____db___brownie__internal);
    Py_CLEAR(modname);
    CPy_XDECREF(CPyStatic_brownie___SOURCE_KEYS.f0);
    CPy_XDECREF(CPyStatic_brownie___SOURCE_KEYS.f1);
    CPy_XDECREF(CPyStatic_brownie___SOURCE_KEYS.f2);
    CPy_XDECREF(CPyStatic_brownie___SOURCE_KEYS.f3);
    CPy_XDECREF(CPyStatic_brownie___SOURCE_KEYS.f4);
    CPy_XDECREF(CPyStatic_brownie___SOURCE_KEYS.f5);
    CPy_XDECREF(CPyStatic_brownie___SOURCE_KEYS.f6);
    CPy_XDECREF(CPyStatic_brownie___SOURCE_KEYS.f7);
    CPy_XDECREF(CPyStatic_brownie___SOURCE_KEYS.f8);
    CPy_XDECREF(CPyStatic_brownie___SOURCE_KEYS.f9);
    CPy_XDECREF(CPyStatic_brownie___SOURCE_KEYS.f10);
    CPy_XDECREF(CPyStatic_brownie___SOURCE_KEYS.f11);
    CPy_XDECREF(CPyStatic_brownie___SOURCE_KEYS.f12);
    CPy_XDECREF(CPyStatic_brownie___SOURCE_KEYS.f13);
    CPy_XDECREF(CPyStatic_brownie___SOURCE_KEYS.f14);
    CPy_XDECREF(CPyStatic_brownie___SOURCE_KEYS.f15);
    CPyStatic_brownie___SOURCE_KEYS = (tuple_T16OOOOOOOOOOOOOOOO) { NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL };
    CPy_XDECREF(CPyStatic_brownie___DISCARD_SOURCE_KEYS.f0);
    CPy_XDECREF(CPyStatic_brownie___DISCARD_SOURCE_KEYS.f1);
    CPy_XDECREF(CPyStatic_brownie___DISCARD_SOURCE_KEYS.f2);
    CPy_XDECREF(CPyStatic_brownie___DISCARD_SOURCE_KEYS.f3);
    CPy_XDECREF(CPyStatic_brownie___DISCARD_SOURCE_KEYS.f4);
    CPy_XDECREF(CPyStatic_brownie___DISCARD_SOURCE_KEYS.f5);
    CPy_XDECREF(CPyStatic_brownie___DISCARD_SOURCE_KEYS.f6);
    CPy_XDECREF(CPyStatic_brownie___DISCARD_SOURCE_KEYS.f7);
    CPyStatic_brownie___DISCARD_SOURCE_KEYS = (tuple_T8OOOOOOOO) { NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL };
    CPy_XDECREF(CPyStatic_brownie___sha1);
    CPyStatic_brownie___sha1 = NULL;
    CPy_XDECREF(CPyStatic_brownie___dumps);
    CPyStatic_brownie___dumps = NULL;
    CPy_XDECREF(CPyStatic_brownie___loads);
    CPyStatic_brownie___loads = NULL;
    CPy_XDECREF(CPyStatic_brownie___sqlite_lock);
    CPyStatic_brownie___sqlite_lock = NULL;
    CPy_XDECREF_NO_IMM(CPyStatic_brownie___cur);
    CPyStatic_brownie___cur = NULL;
    CPy_XDECREF(CPyStatic_brownie___fetchone);
    CPyStatic_brownie___fetchone = NULL;
    CPy_XDECREF(CPyStatic_brownie___y____db___brownie____get_deployment___skip_source_keys);
    CPyStatic_brownie___y____db___brownie____get_deployment___skip_source_keys = NULL;
    Py_CLEAR(CPyType_brownie___AsyncCursor);
    Py_CLEAR(CPyType_brownie___connect_AsyncCursor_gen);
    Py_CLEAR(CPyType_brownie___insert_AsyncCursor_gen);
    Py_CLEAR(CPyType_brownie___fetchone_AsyncCursor_gen);
    Py_CLEAR(CPyType_brownie____get_deployment_gen);
    Py_CLEAR(CPyType_brownie_____fetch_source_for_hash_gen);
    return -1;
}
static struct PyModuleDef browniemodule = {
    PyModuleDef_HEAD_INIT,
    "y._db.brownie",
    NULL, /* docstring */
    0,       /* size of per-interpreter state of the module */
    browniemodule_methods,
    NULL,
};

PyObject *CPyInit_y____db___brownie(void)
{
    if (CPyModule_y____db___brownie__internal) {
        Py_INCREF(CPyModule_y____db___brownie__internal);
        return CPyModule_y____db___brownie__internal;
    }
    CPyModule_y____db___brownie__internal = PyModule_Create(&browniemodule);
    if (unlikely(CPyModule_y____db___brownie__internal == NULL))
        goto fail;
    if (CPyExec_y____db___brownie(CPyModule_y____db___brownie__internal) != 0)
        goto fail;
    return CPyModule_y____db___brownie__internal;
    fail:
    return NULL;
}

char CPyDef_brownie___AsyncCursor_____init__(PyObject *cpy_r_self, PyObject *cpy_r_filename) {
    PyObject *cpy_r_r0;
    PyObject *cpy_r_r1;
    CPy_INCREF(cpy_r_filename);
    ((y____db___brownie___AsyncCursorObject *)cpy_r_self)->__filename = cpy_r_filename;
    cpy_r_r0 = Py_None;
    ((y____db___brownie___AsyncCursorObject *)cpy_r_self)->__db = cpy_r_r0;
    ((y____db___brownie___AsyncCursorObject *)cpy_r_self)->__connected = 0;
    cpy_r_r1 = Py_None;
    ((y____db___brownie___AsyncCursorObject *)cpy_r_self)->__execute = cpy_r_r1;
    return 1;
}

PyObject *CPyPy_brownie___AsyncCursor_____init__(PyObject *self, PyObject *args, PyObject *kw) {
    PyObject *obj_self = self;
    static const char * const kwlist[] = {"filename", 0};
    PyObject *obj_filename;
    if (!CPyArg_ParseTupleAndKeywords(args, kw, "O", "__init__", kwlist, &obj_filename)) {
        return NULL;
    }
    PyObject *arg_self;
    if (likely(Py_TYPE(obj_self) == CPyType_brownie___AsyncCursor))
        arg_self = obj_self;
    else {
        CPy_TypeError("y._db.brownie.AsyncCursor", obj_self); 
        goto fail;
    }
    PyObject *arg_filename = obj_filename;
    char retval = CPyDef_brownie___AsyncCursor_____init__(arg_self, arg_filename);
    if (retval == 2) {
        return NULL;
    }
    PyObject *retbox = Py_None;
    CPy_INCREF(retbox);
    return retbox;
fail: ;
    CPy_AddTraceback("y/_db/brownie.py", "__init__", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
    return NULL;
}

PyObject *CPyDef_brownie___connect_AsyncCursor_gen_____mypyc_generator_helper__(PyObject *cpy_r___mypyc_self__, PyObject *cpy_r_type, PyObject *cpy_r_value, PyObject *cpy_r_traceback, PyObject *cpy_r_arg, PyObject **cpy_r_stop_iter_ptr) {
    PyObject *cpy_r_r0;
    PyObject *cpy_r_r1;
    PyObject *cpy_r_r2;
    PyObject *cpy_r_r3;
    PyObject *cpy_r_r4;
    PyObject *cpy_r_r5;
    PyObject *cpy_r_r6;
    PyObject *cpy_r_r7;
    tuple_T3OOO cpy_r_r8;
    tuple_T3OOO cpy_r_r9;
    int32_t cpy_r_r10;
    PyObject *cpy_r_r11;
    char cpy_r_r12;
    PyObject *cpy_r_r13;
    PyObject *cpy_r_r14;
    char cpy_r_r15;
    PyObject *cpy_r_r16;
    PyObject *cpy_r_r17;
    char cpy_r_r18;
    PyObject *cpy_r_r19;
    PyObject *cpy_r_r20;
    PyObject *cpy_r_r21;
    PyObject *cpy_r_r22;
    PyObject **cpy_r_r24;
    PyObject *cpy_r_r25;
    PyObject *cpy_r_r26;
    char cpy_r_r27;
    PyObject *cpy_r_r28;
    PyObject *cpy_r_r29;
    PyObject *cpy_r_r30;
    char cpy_r_r31;
    PyObject *cpy_r_r32;
    PyObject *cpy_r_r33;
    PyObject **cpy_r_r35;
    PyObject *cpy_r_r36;
    char cpy_r_r37;
    char cpy_r_r38;
    PyObject *cpy_r_r39;
    char cpy_r_r40;
    PyObject *cpy_r_r41;
    PyObject *cpy_r_r42;
    PyObject *cpy_r_r43;
    PyObject *cpy_r_r44;
    PyObject *cpy_r_r45;
    char cpy_r_r46;
    PyObject *cpy_r_r47;
    char cpy_r_r48;
    PyObject *cpy_r_r49;
    char cpy_r_r50;
    tuple_T3OOO cpy_r_r51;
    char cpy_r_r52;
    PyObject **cpy_r_r53;
    PyObject *cpy_r_r54;
    char cpy_r_r55;
    tuple_T3OOO cpy_r_r56;
    tuple_T3OOO cpy_r_r57;
    tuple_T3OOO cpy_r_r58;
    char cpy_r_r59;
    PyObject *cpy_r_r60;
    PyObject *cpy_r_r61;
    PyObject *cpy_r_r62;
    PyObject *cpy_r_r63;
    PyObject *cpy_r_r64;
    PyObject *cpy_r_r65;
    char cpy_r_r66;
    PyObject *cpy_r_r67;
    char cpy_r_r68;
    PyObject *cpy_r_r69;
    PyObject *cpy_r_r70;
    PyObject *cpy_r_r71;
    PyObject *cpy_r_r72;
    PyObject *cpy_r_r73;
    PyObject *cpy_r_r74;
    PyObject **cpy_r_r76;
    PyObject *cpy_r_r77;
    PyObject *cpy_r_r78;
    PyObject *cpy_r_r79;
    char cpy_r_r80;
    PyObject *cpy_r_r81;
    PyObject *cpy_r_r82;
    PyObject *cpy_r_r83;
    PyObject *cpy_r_r84;
    PyObject *cpy_r_r85;
    char cpy_r_r86;
    PyObject *cpy_r_r87;
    char cpy_r_r88;
    PyObject *cpy_r_r89;
    char cpy_r_r90;
    tuple_T3OOO cpy_r_r91;
    char cpy_r_r92;
    PyObject **cpy_r_r93;
    PyObject *cpy_r_r94;
    char cpy_r_r95;
    tuple_T3OOO cpy_r_r96;
    tuple_T3OOO cpy_r_r97;
    tuple_T3OOO cpy_r_r98;
    char cpy_r_r99;
    PyObject *cpy_r_r100;
    PyObject *cpy_r_r101;
    PyObject *cpy_r_r102;
    PyObject *cpy_r_r103;
    char cpy_r_r104;
    PyObject *cpy_r_r105;
    PyObject *cpy_r_r106;
    PyObject *cpy_r_r107;
    PyObject *cpy_r_r108;
    PyObject *cpy_r_r109;
    PyObject *cpy_r_r110;
    char cpy_r_r111;
    tuple_T3OOO cpy_r_r112;
    char cpy_r_r113;
    char cpy_r_r114;
    tuple_T3OOO cpy_r_r115;
    PyObject *cpy_r_r116;
    PyObject *cpy_r_r117;
    PyObject *cpy_r_r118;
    PyObject *cpy_r_r119;
    PyObject *cpy_r_r120;
    PyObject **cpy_r_r122;
    PyObject *cpy_r_r123;
    PyObject *cpy_r_r124;
    char cpy_r_r125;
    PyObject *cpy_r_r126;
    PyObject *cpy_r_r127;
    PyObject *cpy_r_r128;
    PyObject *cpy_r_r129;
    PyObject *cpy_r_r130;
    char cpy_r_r131;
    PyObject *cpy_r_r132;
    char cpy_r_r133;
    PyObject *cpy_r_r134;
    char cpy_r_r135;
    tuple_T3OOO cpy_r_r136;
    char cpy_r_r137;
    PyObject **cpy_r_r138;
    PyObject *cpy_r_r139;
    char cpy_r_r140;
    tuple_T3OOO cpy_r_r141;
    tuple_T3OOO cpy_r_r142;
    tuple_T3OOO cpy_r_r143;
    char cpy_r_r144;
    PyObject *cpy_r_r145;
    PyObject *cpy_r_r146;
    PyObject *cpy_r_r147;
    int32_t cpy_r_r148;
    char cpy_r_r149;
    char cpy_r_r150;
    tuple_T3OOO cpy_r_r151;
    tuple_T3OOO cpy_r_r152;
    char cpy_r_r153;
    PyObject *cpy_r_r154;
    char cpy_r_r155;
    tuple_T3OOO cpy_r_r156;
    PyObject *cpy_r_r157;
    char cpy_r_r158;
    tuple_T3OOO cpy_r_r159;
    char cpy_r_r160;
    PyObject *cpy_r_r161;
    PyObject *cpy_r_r162;
    PyObject *cpy_r_r163;
    PyObject **cpy_r_r165;
    PyObject *cpy_r_r166;
    PyObject *cpy_r_r167;
    char cpy_r_r168;
    PyObject *cpy_r_r169;
    PyObject *cpy_r_r170;
    PyObject *cpy_r_r171;
    PyObject *cpy_r_r172;
    PyObject *cpy_r_r173;
    char cpy_r_r174;
    PyObject *cpy_r_r175;
    char cpy_r_r176;
    PyObject *cpy_r_r177;
    char cpy_r_r178;
    tuple_T3OOO cpy_r_r179;
    char cpy_r_r180;
    PyObject **cpy_r_r181;
    PyObject *cpy_r_r182;
    char cpy_r_r183;
    tuple_T3OOO cpy_r_r184;
    tuple_T3OOO cpy_r_r185;
    tuple_T3OOO cpy_r_r186;
    char cpy_r_r187;
    PyObject *cpy_r_r188;
    PyObject *cpy_r_r189;
    PyObject *cpy_r_r190;
    PyObject *cpy_r_r191;
    char cpy_r_r192;
    char cpy_r_r193;
    PyObject *cpy_r_r194;
    char cpy_r_r195;
    char cpy_r_r196;
    char cpy_r_r197;
    char cpy_r_r198;
    char cpy_r_r199;
    char cpy_r_r200;
    char cpy_r_r201;
    PyObject *cpy_r_r202;
    cpy_r_r0 = NULL;
    cpy_r_r1 = cpy_r_r0;
    cpy_r_r2 = NULL;
    cpy_r_r3 = cpy_r_r2;
    cpy_r_r4 = NULL;
    cpy_r_r5 = cpy_r_r4;
    cpy_r_r6 = NULL;
    cpy_r_r7 = cpy_r_r6;
    tuple_T3OOO __tmp3 = { NULL, NULL, NULL };
    cpy_r_r8 = __tmp3;
    cpy_r_r9 = cpy_r_r8;
    cpy_r_r10 = ((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_next_label__;
    goto CPyL186;
CPyL1: ;
    cpy_r_r11 = (PyObject *)&_Py_NoneStruct;
    cpy_r_r12 = cpy_r_type != cpy_r_r11;
    if (!cpy_r_r12) goto CPyL4;
    CPyErr_SetObjectAndTraceback(cpy_r_type, cpy_r_value, cpy_r_traceback);
    if (unlikely(!0)) {
        CPy_AddTraceback("y/_db/brownie.py", "connect", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL193;
    }
    CPy_Unreachable();
CPyL4: ;
    cpy_r_r13 = ((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__self;
    if (unlikely(cpy_r_r13 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "connect", "connect_AsyncCursor_gen", "self", 100, CPyStatic_brownie___globals);
        goto CPyL193;
    }
    CPy_INCREF_NO_IMM(cpy_r_r13);
CPyL5: ;
    cpy_r_r14 = ((y____db___brownie___AsyncCursorObject *)cpy_r_r13)->__db;
    CPy_INCREF(cpy_r_r14);
    CPy_DECREF_NO_IMM(cpy_r_r13);
    if (((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__db != NULL) {
        CPy_DECREF(((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__db);
    }
    ((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__db = cpy_r_r14;
    cpy_r_r15 = 1;
    if (unlikely(!cpy_r_r15)) {
        CPy_AddTraceback("y/_db/brownie.py", "connect", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL193;
    }
    cpy_r_r16 = ((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__db;
    if (unlikely(cpy_r_r16 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "connect", "connect_AsyncCursor_gen", "db", 101, CPyStatic_brownie___globals);
        goto CPyL193;
    }
    CPy_INCREF(cpy_r_r16);
CPyL7: ;
    cpy_r_r17 = (PyObject *)&_Py_NoneStruct;
    cpy_r_r18 = cpy_r_r16 != cpy_r_r17;
    CPy_DECREF(cpy_r_r16);
    if (!cpy_r_r18) goto CPyL12;
    cpy_r_r19 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'already connected' */
    cpy_r_r20 = CPyModule_builtins;
    cpy_r_r21 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'RuntimeError' */
    cpy_r_r22 = CPyObject_GetAttr(cpy_r_r20, cpy_r_r21);
    if (unlikely(cpy_r_r22 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "connect", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL193;
    }
    PyObject *cpy_r_r23[1] = {cpy_r_r19};
    cpy_r_r24 = (PyObject **)&cpy_r_r23;
    cpy_r_r25 = PyObject_Vectorcall(cpy_r_r22, cpy_r_r24, 1, 0);
    CPy_DECREF(cpy_r_r22);
    if (unlikely(cpy_r_r25 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "connect", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL193;
    }
    CPy_Raise(cpy_r_r25);
    CPy_DECREF(cpy_r_r25);
    if (unlikely(!0)) {
        CPy_AddTraceback("y/_db/brownie.py", "connect", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL193;
    }
    CPy_Unreachable();
CPyL12: ;
    cpy_r_r26 = CPyStatic_brownie___sqlite_lock;
    if (likely(cpy_r_r26 != NULL)) goto CPyL15;
    PyErr_SetString(PyExc_NameError, "value for final name \"sqlite_lock\" was not set");
    cpy_r_r27 = 0;
    if (unlikely(!cpy_r_r27)) {
        CPy_AddTraceback("y/_db/brownie.py", "connect", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL193;
    }
    CPy_Unreachable();
CPyL15: ;
    cpy_r_r28 = CPy_TYPE(cpy_r_r26);
    cpy_r_r29 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* '__aexit__' */
    cpy_r_r30 = CPyObject_GetAttr(cpy_r_r28, cpy_r_r29);
    if (unlikely(cpy_r_r30 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "connect", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL194;
    }
    if (((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__0 != NULL) {
        CPy_DECREF(((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__0);
    }
    ((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__0 = cpy_r_r30;
    cpy_r_r31 = 1;
    if (unlikely(!cpy_r_r31)) {
        CPy_AddTraceback("y/_db/brownie.py", "connect", -1, CPyStatic_brownie___globals);
        goto CPyL194;
    }
    cpy_r_r32 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* '__aenter__' */
    cpy_r_r33 = CPyObject_GetAttr(cpy_r_r28, cpy_r_r32);
    CPy_DECREF(cpy_r_r28);
    if (unlikely(cpy_r_r33 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "connect", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL193;
    }
    PyObject *cpy_r_r34[1] = {cpy_r_r26};
    cpy_r_r35 = (PyObject **)&cpy_r_r34;
    cpy_r_r36 = PyObject_Vectorcall(cpy_r_r33, cpy_r_r35, 1, 0);
    CPy_DECREF(cpy_r_r33);
    if (unlikely(cpy_r_r36 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "connect", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL193;
    }
    CPy_INCREF(cpy_r_r26);
    if (((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__1 != NULL) {
        CPy_DECREF(((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__1);
    }
    ((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__1 = cpy_r_r26;
    cpy_r_r37 = 1;
    if (unlikely(!cpy_r_r37)) {
        CPy_AddTraceback("y/_db/brownie.py", "connect", -1, CPyStatic_brownie___globals);
        goto CPyL195;
    }
    ((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__2 = 1;
    cpy_r_r38 = 1;
    if (unlikely(!cpy_r_r38)) {
        CPy_AddTraceback("y/_db/brownie.py", "connect", -1, CPyStatic_brownie___globals);
        goto CPyL195;
    }
    cpy_r_r39 = CPy_GetCoro(cpy_r_r36);
    CPy_DECREF(cpy_r_r36);
    if (unlikely(cpy_r_r39 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "connect", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL193;
    }
    if (((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__3 != NULL) {
        CPy_DECREF(((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__3);
    }
    ((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__3 = cpy_r_r39;
    cpy_r_r40 = 1;
    if (unlikely(!cpy_r_r40)) {
        CPy_AddTraceback("y/_db/brownie.py", "connect", -1, CPyStatic_brownie___globals);
        goto CPyL193;
    }
    cpy_r_r41 = ((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__3;
    if (unlikely(cpy_r_r41 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "connect", "connect_AsyncCursor_gen", "__mypyc_temp__3", -1, CPyStatic_brownie___globals);
        goto CPyL193;
    }
    CPy_INCREF(cpy_r_r41);
CPyL24: ;
    cpy_r_r42 = CPyIter_Next(cpy_r_r41);
    CPy_DECREF(cpy_r_r41);
    if (cpy_r_r42 != NULL) goto CPyL27;
    cpy_r_r43 = CPy_FetchStopIterationValue();
    if (unlikely(cpy_r_r43 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "connect", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL193;
    }
    cpy_r_r44 = cpy_r_r43;
    CPy_DECREF(cpy_r_r44);
    cpy_r_r45 = NULL;
    if (((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__3 != NULL) {
        CPy_DECREF(((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__3);
    }
    ((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__3 = cpy_r_r45;
    cpy_r_r46 = 1;
    if (unlikely(!cpy_r_r46)) {
        CPy_AddTraceback("y/_db/brownie.py", "connect", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL193;
    } else
        goto CPyL49;
CPyL27: ;
    cpy_r_r47 = cpy_r_r42;
CPyL28: ;
    ((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_next_label__ = 1;
    return cpy_r_r47;
CPyL29: ;
    cpy_r_r49 = (PyObject *)&_Py_NoneStruct;
    cpy_r_r50 = cpy_r_type != cpy_r_r49;
    if (!cpy_r_r50) goto CPyL196;
    CPyErr_SetObjectAndTraceback(cpy_r_type, cpy_r_value, cpy_r_traceback);
    if (unlikely(!0)) {
        CPy_AddTraceback("y/_db/brownie.py", "connect", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL33;
    } else
        goto CPyL197;
CPyL31: ;
    CPy_Unreachable();
CPyL32: ;
    CPy_INCREF(cpy_r_arg);
    goto CPyL44;
CPyL33: ;
    cpy_r_r51 = CPy_CatchError();
    if (((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__4.f0 != NULL) {
        CPy_DECREF(((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__4.f0);
        CPy_DECREF(((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__4.f1);
        CPy_DECREF(((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__4.f2);
    }
    ((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__4 = cpy_r_r51;
    cpy_r_r52 = 1;
    if (unlikely(!cpy_r_r52)) {
        CPy_AddTraceback("y/_db/brownie.py", "connect", -1, CPyStatic_brownie___globals);
        goto CPyL198;
    }
    cpy_r_r53 = (PyObject **)&cpy_r_r1;
    cpy_r_r54 = ((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__3;
    if (unlikely(cpy_r_r54 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "connect", "connect_AsyncCursor_gen", "__mypyc_temp__3", -1, CPyStatic_brownie___globals);
        goto CPyL198;
    }
    CPy_INCREF(cpy_r_r54);
CPyL35: ;
    cpy_r_r55 = CPy_YieldFromErrorHandle(cpy_r_r54, cpy_r_r53);
    CPy_DecRef(cpy_r_r54);
    if (unlikely(cpy_r_r55 == 2)) {
        CPy_AddTraceback("y/_db/brownie.py", "connect", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL198;
    }
    if (cpy_r_r55) goto CPyL39;
    cpy_r_r47 = cpy_r_r1;
    cpy_r_r56 = ((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__4;
    if (unlikely(cpy_r_r56.f0 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "connect", "connect_AsyncCursor_gen", "__mypyc_temp__4", -1, CPyStatic_brownie___globals);
        goto CPyL199;
    }
    CPy_INCREF(cpy_r_r56.f0);
    CPy_INCREF(cpy_r_r56.f1);
    CPy_INCREF(cpy_r_r56.f2);
CPyL38: ;
    CPy_RestoreExcInfo(cpy_r_r56);
    CPy_DecRef(cpy_r_r56.f0);
    CPy_DecRef(cpy_r_r56.f1);
    CPy_DecRef(cpy_r_r56.f2);
    goto CPyL28;
CPyL39: ;
    cpy_r_r44 = cpy_r_r1;
    CPy_DecRef(cpy_r_r44);
    cpy_r_r57 = ((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__4;
    if (unlikely(cpy_r_r57.f0 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "connect", "connect_AsyncCursor_gen", "__mypyc_temp__4", -1, CPyStatic_brownie___globals);
        goto CPyL41;
    }
    CPy_INCREF(cpy_r_r57.f0);
    CPy_INCREF(cpy_r_r57.f1);
    CPy_INCREF(cpy_r_r57.f2);
CPyL40: ;
    CPy_RestoreExcInfo(cpy_r_r57);
    CPy_DecRef(cpy_r_r57.f0);
    CPy_DecRef(cpy_r_r57.f1);
    CPy_DecRef(cpy_r_r57.f2);
    goto CPyL49;
CPyL41: ;
    cpy_r_r58 = ((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__4;
    if (unlikely(cpy_r_r58.f0 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "connect", "connect_AsyncCursor_gen", "__mypyc_temp__4", -1, CPyStatic_brownie___globals);
        goto CPyL193;
    }
    CPy_INCREF(cpy_r_r58.f0);
    CPy_INCREF(cpy_r_r58.f1);
    CPy_INCREF(cpy_r_r58.f2);
CPyL42: ;
    CPy_RestoreExcInfo(cpy_r_r58);
    CPy_DecRef(cpy_r_r58.f0);
    CPy_DecRef(cpy_r_r58.f1);
    CPy_DecRef(cpy_r_r58.f2);
    cpy_r_r59 = CPy_KeepPropagating();
    if (!cpy_r_r59) goto CPyL193;
    CPy_Unreachable();
CPyL44: ;
    cpy_r_r60 = ((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__3;
    if (unlikely(cpy_r_r60 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "connect", "connect_AsyncCursor_gen", "__mypyc_temp__3", -1, CPyStatic_brownie___globals);
        goto CPyL200;
    }
    CPy_INCREF(cpy_r_r60);
CPyL45: ;
    cpy_r_r61 = CPyIter_Send(cpy_r_r60, cpy_r_arg);
    CPy_DECREF(cpy_r_r60);
    CPy_DECREF(cpy_r_arg);
    if (cpy_r_r61 == NULL) goto CPyL47;
    cpy_r_r47 = cpy_r_r61;
    goto CPyL28;
CPyL47: ;
    cpy_r_r62 = CPy_FetchStopIterationValue();
    if (unlikely(cpy_r_r62 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "connect", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL193;
    }
    cpy_r_r44 = cpy_r_r62;
    CPy_DECREF(cpy_r_r44);
CPyL49: ;
    cpy_r_r63 = ((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__self;
    if (unlikely(cpy_r_r63 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "connect", "connect_AsyncCursor_gen", "self", 104, CPyStatic_brownie___globals);
        goto CPyL89;
    }
    CPy_INCREF_NO_IMM(cpy_r_r63);
CPyL50: ;
    cpy_r_r64 = ((y____db___brownie___AsyncCursorObject *)cpy_r_r63)->__db;
    cpy_r_r65 = (PyObject *)&_Py_NoneStruct;
    cpy_r_r66 = cpy_r_r64 != cpy_r_r65;
    CPy_DECREF_NO_IMM(cpy_r_r63);
    if (!cpy_r_r66) goto CPyL52;
    cpy_r_r67 = Py_None;
    if (((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__5 != NULL) {
        CPy_DECREF(((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__5);
    }
    ((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__5 = cpy_r_r67;
    cpy_r_r68 = 1;
    if (unlikely(!cpy_r_r68)) {
        CPy_AddTraceback("y/_db/brownie.py", "connect", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL89;
    } else
        goto CPyL132;
CPyL52: ;
    cpy_r_r69 = ((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__self;
    if (unlikely(cpy_r_r69 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "connect", "connect_AsyncCursor_gen", "self", 106, CPyStatic_brownie___globals);
        goto CPyL89;
    }
    CPy_INCREF_NO_IMM(cpy_r_r69);
CPyL53: ;
    cpy_r_r70 = ((y____db___brownie___AsyncCursorObject *)cpy_r_r69)->__filename;
    CPy_INCREF(cpy_r_r70);
    CPy_DECREF_NO_IMM(cpy_r_r69);
    cpy_r_r71 = CPyModule_aiosqlite;
    cpy_r_r72 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'connect' */
    cpy_r_r73 = CPyObject_GetAttr(cpy_r_r71, cpy_r_r72);
    if (unlikely(cpy_r_r73 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "connect", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL201;
    }
    cpy_r_r74 = Py_None;
    PyObject *cpy_r_r75[2] = {cpy_r_r70, cpy_r_r74};
    cpy_r_r76 = (PyObject **)&cpy_r_r75;
    cpy_r_r77 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* ('isolation_level',) */
    cpy_r_r78 = PyObject_Vectorcall(cpy_r_r73, cpy_r_r76, 1, cpy_r_r77);
    CPy_DECREF(cpy_r_r73);
    if (unlikely(cpy_r_r78 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "connect", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL201;
    }
    CPy_DECREF(cpy_r_r70);
    cpy_r_r79 = CPy_GetCoro(cpy_r_r78);
    CPy_DECREF(cpy_r_r78);
    if (unlikely(cpy_r_r79 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "connect", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL89;
    }
    if (((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__6 != NULL) {
        CPy_DECREF(((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__6);
    }
    ((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__6 = cpy_r_r79;
    cpy_r_r80 = 1;
    if (unlikely(!cpy_r_r80)) {
        CPy_AddTraceback("y/_db/brownie.py", "connect", -1, CPyStatic_brownie___globals);
        goto CPyL89;
    }
    cpy_r_r81 = ((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__6;
    if (unlikely(cpy_r_r81 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "connect", "connect_AsyncCursor_gen", "__mypyc_temp__6", -1, CPyStatic_brownie___globals);
        goto CPyL89;
    }
    CPy_INCREF(cpy_r_r81);
CPyL58: ;
    cpy_r_r82 = CPyIter_Next(cpy_r_r81);
    CPy_DECREF(cpy_r_r81);
    if (cpy_r_r82 != NULL) goto CPyL61;
    cpy_r_r83 = CPy_FetchStopIterationValue();
    if (unlikely(cpy_r_r83 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "connect", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL89;
    }
    cpy_r_r84 = cpy_r_r83;
    cpy_r_r85 = NULL;
    if (((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__6 != NULL) {
        CPy_DECREF(((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__6);
    }
    ((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__6 = cpy_r_r85;
    cpy_r_r86 = 1;
    if (unlikely(!cpy_r_r86)) {
        CPy_AddTraceback("y/_db/brownie.py", "connect", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL202;
    } else
        goto CPyL83;
CPyL61: ;
    cpy_r_r87 = cpy_r_r82;
CPyL62: ;
    ((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_next_label__ = 2;
    return cpy_r_r87;
CPyL63: ;
    cpy_r_r89 = (PyObject *)&_Py_NoneStruct;
    cpy_r_r90 = cpy_r_type != cpy_r_r89;
    if (!cpy_r_r90) goto CPyL203;
    CPyErr_SetObjectAndTraceback(cpy_r_type, cpy_r_value, cpy_r_traceback);
    if (unlikely(!0)) {
        CPy_AddTraceback("y/_db/brownie.py", "connect", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL67;
    } else
        goto CPyL204;
CPyL65: ;
    CPy_Unreachable();
CPyL66: ;
    CPy_INCREF(cpy_r_arg);
    goto CPyL78;
CPyL67: ;
    cpy_r_r91 = CPy_CatchError();
    if (((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__7.f0 != NULL) {
        CPy_DECREF(((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__7.f0);
        CPy_DECREF(((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__7.f1);
        CPy_DECREF(((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__7.f2);
    }
    ((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__7 = cpy_r_r91;
    cpy_r_r92 = 1;
    if (unlikely(!cpy_r_r92)) {
        CPy_AddTraceback("y/_db/brownie.py", "connect", -1, CPyStatic_brownie___globals);
        goto CPyL205;
    }
    cpy_r_r93 = (PyObject **)&cpy_r_r3;
    cpy_r_r94 = ((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__6;
    if (unlikely(cpy_r_r94 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "connect", "connect_AsyncCursor_gen", "__mypyc_temp__6", -1, CPyStatic_brownie___globals);
        goto CPyL205;
    }
    CPy_INCREF(cpy_r_r94);
CPyL69: ;
    cpy_r_r95 = CPy_YieldFromErrorHandle(cpy_r_r94, cpy_r_r93);
    CPy_DecRef(cpy_r_r94);
    if (unlikely(cpy_r_r95 == 2)) {
        CPy_AddTraceback("y/_db/brownie.py", "connect", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL205;
    }
    if (cpy_r_r95) goto CPyL73;
    cpy_r_r87 = cpy_r_r3;
    cpy_r_r96 = ((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__7;
    if (unlikely(cpy_r_r96.f0 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "connect", "connect_AsyncCursor_gen", "__mypyc_temp__7", -1, CPyStatic_brownie___globals);
        goto CPyL206;
    }
    CPy_INCREF(cpy_r_r96.f0);
    CPy_INCREF(cpy_r_r96.f1);
    CPy_INCREF(cpy_r_r96.f2);
CPyL72: ;
    CPy_RestoreExcInfo(cpy_r_r96);
    CPy_DecRef(cpy_r_r96.f0);
    CPy_DecRef(cpy_r_r96.f1);
    CPy_DecRef(cpy_r_r96.f2);
    goto CPyL62;
CPyL73: ;
    cpy_r_r84 = cpy_r_r3;
    cpy_r_r97 = ((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__7;
    if (unlikely(cpy_r_r97.f0 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "connect", "connect_AsyncCursor_gen", "__mypyc_temp__7", -1, CPyStatic_brownie___globals);
        goto CPyL207;
    }
    CPy_INCREF(cpy_r_r97.f0);
    CPy_INCREF(cpy_r_r97.f1);
    CPy_INCREF(cpy_r_r97.f2);
CPyL74: ;
    CPy_RestoreExcInfo(cpy_r_r97);
    CPy_DecRef(cpy_r_r97.f0);
    CPy_DecRef(cpy_r_r97.f1);
    CPy_DecRef(cpy_r_r97.f2);
    goto CPyL83;
CPyL75: ;
    cpy_r_r98 = ((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__7;
    if (unlikely(cpy_r_r98.f0 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "connect", "connect_AsyncCursor_gen", "__mypyc_temp__7", -1, CPyStatic_brownie___globals);
        goto CPyL89;
    }
    CPy_INCREF(cpy_r_r98.f0);
    CPy_INCREF(cpy_r_r98.f1);
    CPy_INCREF(cpy_r_r98.f2);
CPyL76: ;
    CPy_RestoreExcInfo(cpy_r_r98);
    CPy_DecRef(cpy_r_r98.f0);
    CPy_DecRef(cpy_r_r98.f1);
    CPy_DecRef(cpy_r_r98.f2);
    cpy_r_r99 = CPy_KeepPropagating();
    if (!cpy_r_r99) goto CPyL89;
    CPy_Unreachable();
CPyL78: ;
    cpy_r_r100 = ((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__6;
    if (unlikely(cpy_r_r100 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "connect", "connect_AsyncCursor_gen", "__mypyc_temp__6", -1, CPyStatic_brownie___globals);
        goto CPyL208;
    }
    CPy_INCREF(cpy_r_r100);
CPyL79: ;
    cpy_r_r101 = CPyIter_Send(cpy_r_r100, cpy_r_arg);
    CPy_DECREF(cpy_r_r100);
    CPy_DECREF(cpy_r_arg);
    if (cpy_r_r101 == NULL) goto CPyL81;
    cpy_r_r87 = cpy_r_r101;
    goto CPyL62;
CPyL81: ;
    cpy_r_r102 = CPy_FetchStopIterationValue();
    if (unlikely(cpy_r_r102 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "connect", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL89;
    }
    cpy_r_r84 = cpy_r_r102;
CPyL83: ;
    cpy_r_r103 = ((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__self;
    if (unlikely(cpy_r_r103 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "connect", "connect_AsyncCursor_gen", "self", 106, CPyStatic_brownie___globals);
        goto CPyL202;
    }
    CPy_INCREF_NO_IMM(cpy_r_r103);
CPyL84: ;
    CPy_DECREF(((y____db___brownie___AsyncCursorObject *)cpy_r_r103)->__db);
    ((y____db___brownie___AsyncCursorObject *)cpy_r_r103)->__db = cpy_r_r84;
    CPy_DECREF_NO_IMM(cpy_r_r103);
    cpy_r_r105 = ((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__self;
    if (unlikely(cpy_r_r105 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "connect", "connect_AsyncCursor_gen", "self", 107, CPyStatic_brownie___globals);
        goto CPyL89;
    }
    CPy_INCREF_NO_IMM(cpy_r_r105);
CPyL85: ;
    cpy_r_r106 = ((y____db___brownie___AsyncCursorObject *)cpy_r_r105)->__db;
    CPy_INCREF(cpy_r_r106);
    CPy_DECREF_NO_IMM(cpy_r_r105);
    cpy_r_r107 = cpy_r_r106;
    cpy_r_r108 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'execute' */
    cpy_r_r109 = CPyObject_GetAttr(cpy_r_r107, cpy_r_r108);
    CPy_DECREF(cpy_r_r107);
    if (unlikely(cpy_r_r109 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "connect", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL89;
    }
    cpy_r_r110 = ((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__self;
    if (unlikely(cpy_r_r110 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "connect", "connect_AsyncCursor_gen", "self", 107, CPyStatic_brownie___globals);
        goto CPyL209;
    }
    CPy_INCREF_NO_IMM(cpy_r_r110);
CPyL88: ;
    CPy_DECREF(((y____db___brownie___AsyncCursorObject *)cpy_r_r110)->__execute);
    ((y____db___brownie___AsyncCursorObject *)cpy_r_r110)->__execute = cpy_r_r109;
    CPy_DECREF_NO_IMM(cpy_r_r110);
    goto CPyL131;
CPyL89: ;
    cpy_r_r112 = CPy_CatchError();
    if (((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__8.f0 != NULL) {
        CPy_DECREF(((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__8.f0);
        CPy_DECREF(((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__8.f1);
        CPy_DECREF(((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__8.f2);
    }
    ((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__8 = cpy_r_r112;
    cpy_r_r113 = 1;
    if (unlikely(!cpy_r_r113)) {
        CPy_AddTraceback("y/_db/brownie.py", "connect", -1, CPyStatic_brownie___globals);
        goto CPyL128;
    }
    ((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__2 = 0;
    cpy_r_r114 = 1;
    if (unlikely(!cpy_r_r114)) {
        CPy_AddTraceback("y/_db/brownie.py", "connect", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL128;
    }
    cpy_r_r115 = CPy_GetExcInfo();
    cpy_r_r116 = cpy_r_r115.f0;
    CPy_INCREF(cpy_r_r116);
    cpy_r_r117 = cpy_r_r115.f1;
    CPy_INCREF(cpy_r_r117);
    cpy_r_r118 = cpy_r_r115.f2;
    CPy_INCREF(cpy_r_r118);
    CPy_DecRef(cpy_r_r115.f0);
    CPy_DecRef(cpy_r_r115.f1);
    CPy_DecRef(cpy_r_r115.f2);
    cpy_r_r119 = ((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__0;
    if (unlikely(cpy_r_r119 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "connect", "connect_AsyncCursor_gen", "__mypyc_temp__0", -1, CPyStatic_brownie___globals);
        goto CPyL210;
    }
    CPy_INCREF(cpy_r_r119);
CPyL92: ;
    cpy_r_r120 = ((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__1;
    if (unlikely(cpy_r_r120 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "connect", "connect_AsyncCursor_gen", "__mypyc_temp__1", -1, CPyStatic_brownie___globals);
        goto CPyL211;
    }
    CPy_INCREF(cpy_r_r120);
CPyL93: ;
    PyObject *cpy_r_r121[4] = {cpy_r_r120, cpy_r_r116, cpy_r_r117, cpy_r_r118};
    cpy_r_r122 = (PyObject **)&cpy_r_r121;
    cpy_r_r123 = PyObject_Vectorcall(cpy_r_r119, cpy_r_r122, 4, 0);
    CPy_DecRef(cpy_r_r119);
    if (unlikely(cpy_r_r123 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "connect", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL212;
    }
    CPy_DecRef(cpy_r_r120);
    CPy_DecRef(cpy_r_r116);
    CPy_DecRef(cpy_r_r117);
    CPy_DecRef(cpy_r_r118);
    cpy_r_r124 = CPy_GetCoro(cpy_r_r123);
    CPy_DecRef(cpy_r_r123);
    if (unlikely(cpy_r_r124 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "connect", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL128;
    }
    if (((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__9 != NULL) {
        CPy_DECREF(((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__9);
    }
    ((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__9 = cpy_r_r124;
    cpy_r_r125 = 1;
    if (unlikely(!cpy_r_r125)) {
        CPy_AddTraceback("y/_db/brownie.py", "connect", -1, CPyStatic_brownie___globals);
        goto CPyL128;
    }
    cpy_r_r126 = ((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__9;
    if (unlikely(cpy_r_r126 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "connect", "connect_AsyncCursor_gen", "__mypyc_temp__9", -1, CPyStatic_brownie___globals);
        goto CPyL128;
    }
    CPy_INCREF(cpy_r_r126);
CPyL97: ;
    cpy_r_r127 = CPyIter_Next(cpy_r_r126);
    CPy_DecRef(cpy_r_r126);
    if (cpy_r_r127 != NULL) goto CPyL100;
    cpy_r_r128 = CPy_FetchStopIterationValue();
    if (unlikely(cpy_r_r128 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "connect", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL128;
    }
    cpy_r_r129 = cpy_r_r128;
    cpy_r_r130 = NULL;
    if (((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__9 != NULL) {
        CPy_DECREF(((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__9);
    }
    ((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__9 = cpy_r_r130;
    cpy_r_r131 = 1;
    if (unlikely(!cpy_r_r131)) {
        CPy_AddTraceback("y/_db/brownie.py", "connect", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL213;
    } else
        goto CPyL122;
CPyL100: ;
    cpy_r_r132 = cpy_r_r127;
CPyL101: ;
    ((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_next_label__ = 3;
    return cpy_r_r132;
CPyL102: ;
    cpy_r_r134 = (PyObject *)&_Py_NoneStruct;
    cpy_r_r135 = cpy_r_type != cpy_r_r134;
    if (!cpy_r_r135) goto CPyL214;
    CPyErr_SetObjectAndTraceback(cpy_r_type, cpy_r_value, cpy_r_traceback);
    if (unlikely(!0)) {
        CPy_AddTraceback("y/_db/brownie.py", "connect", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL106;
    } else
        goto CPyL215;
CPyL104: ;
    CPy_Unreachable();
CPyL105: ;
    CPy_INCREF(cpy_r_arg);
    goto CPyL117;
CPyL106: ;
    cpy_r_r136 = CPy_CatchError();
    if (((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__10.f0 != NULL) {
        CPy_DECREF(((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__10.f0);
        CPy_DECREF(((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__10.f1);
        CPy_DECREF(((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__10.f2);
    }
    ((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__10 = cpy_r_r136;
    cpy_r_r137 = 1;
    if (unlikely(!cpy_r_r137)) {
        CPy_AddTraceback("y/_db/brownie.py", "connect", -1, CPyStatic_brownie___globals);
        goto CPyL216;
    }
    cpy_r_r138 = (PyObject **)&cpy_r_r5;
    cpy_r_r139 = ((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__9;
    if (unlikely(cpy_r_r139 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "connect", "connect_AsyncCursor_gen", "__mypyc_temp__9", -1, CPyStatic_brownie___globals);
        goto CPyL216;
    }
    CPy_INCREF(cpy_r_r139);
CPyL108: ;
    cpy_r_r140 = CPy_YieldFromErrorHandle(cpy_r_r139, cpy_r_r138);
    CPy_DecRef(cpy_r_r139);
    if (unlikely(cpy_r_r140 == 2)) {
        CPy_AddTraceback("y/_db/brownie.py", "connect", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL216;
    }
    if (cpy_r_r140) goto CPyL112;
    cpy_r_r132 = cpy_r_r5;
    cpy_r_r141 = ((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__10;
    if (unlikely(cpy_r_r141.f0 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "connect", "connect_AsyncCursor_gen", "__mypyc_temp__10", -1, CPyStatic_brownie___globals);
        goto CPyL217;
    }
    CPy_INCREF(cpy_r_r141.f0);
    CPy_INCREF(cpy_r_r141.f1);
    CPy_INCREF(cpy_r_r141.f2);
CPyL111: ;
    CPy_RestoreExcInfo(cpy_r_r141);
    CPy_DecRef(cpy_r_r141.f0);
    CPy_DecRef(cpy_r_r141.f1);
    CPy_DecRef(cpy_r_r141.f2);
    goto CPyL101;
CPyL112: ;
    cpy_r_r129 = cpy_r_r5;
    cpy_r_r142 = ((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__10;
    if (unlikely(cpy_r_r142.f0 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "connect", "connect_AsyncCursor_gen", "__mypyc_temp__10", -1, CPyStatic_brownie___globals);
        goto CPyL218;
    }
    CPy_INCREF(cpy_r_r142.f0);
    CPy_INCREF(cpy_r_r142.f1);
    CPy_INCREF(cpy_r_r142.f2);
CPyL113: ;
    CPy_RestoreExcInfo(cpy_r_r142);
    CPy_DecRef(cpy_r_r142.f0);
    CPy_DecRef(cpy_r_r142.f1);
    CPy_DecRef(cpy_r_r142.f2);
    goto CPyL122;
CPyL114: ;
    cpy_r_r143 = ((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__10;
    if (unlikely(cpy_r_r143.f0 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "connect", "connect_AsyncCursor_gen", "__mypyc_temp__10", -1, CPyStatic_brownie___globals);
        goto CPyL128;
    }
    CPy_INCREF(cpy_r_r143.f0);
    CPy_INCREF(cpy_r_r143.f1);
    CPy_INCREF(cpy_r_r143.f2);
CPyL115: ;
    CPy_RestoreExcInfo(cpy_r_r143);
    CPy_DecRef(cpy_r_r143.f0);
    CPy_DecRef(cpy_r_r143.f1);
    CPy_DecRef(cpy_r_r143.f2);
    cpy_r_r144 = CPy_KeepPropagating();
    if (!cpy_r_r144) goto CPyL128;
    CPy_Unreachable();
CPyL117: ;
    cpy_r_r145 = ((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__9;
    if (unlikely(cpy_r_r145 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "connect", "connect_AsyncCursor_gen", "__mypyc_temp__9", -1, CPyStatic_brownie___globals);
        goto CPyL219;
    }
    CPy_INCREF(cpy_r_r145);
CPyL118: ;
    cpy_r_r146 = CPyIter_Send(cpy_r_r145, cpy_r_arg);
    CPy_DECREF(cpy_r_r145);
    CPy_DECREF(cpy_r_arg);
    if (cpy_r_r146 == NULL) goto CPyL120;
    cpy_r_r132 = cpy_r_r146;
    goto CPyL101;
CPyL120: ;
    cpy_r_r147 = CPy_FetchStopIterationValue();
    if (unlikely(cpy_r_r147 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "connect", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL128;
    }
    cpy_r_r129 = cpy_r_r147;
CPyL122: ;
    cpy_r_r148 = PyObject_IsTrue(cpy_r_r129);
    CPy_DECREF(cpy_r_r129);
    cpy_r_r149 = cpy_r_r148 >= 0;
    if (unlikely(!cpy_r_r149)) {
        CPy_AddTraceback("y/_db/brownie.py", "connect", -1, CPyStatic_brownie___globals);
        goto CPyL128;
    }
    cpy_r_r150 = cpy_r_r148;
    if (cpy_r_r150) goto CPyL126;
    CPy_Reraise();
    if (!0) goto CPyL128;
    CPy_Unreachable();
CPyL126: ;
    cpy_r_r151 = ((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__8;
    if (unlikely(cpy_r_r151.f0 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "connect", "connect_AsyncCursor_gen", "__mypyc_temp__8", -1, CPyStatic_brownie___globals);
        goto CPyL133;
    }
    CPy_INCREF(cpy_r_r151.f0);
    CPy_INCREF(cpy_r_r151.f1);
    CPy_INCREF(cpy_r_r151.f2);
CPyL127: ;
    CPy_RestoreExcInfo(cpy_r_r151);
    CPy_DECREF(cpy_r_r151.f0);
    CPy_DECREF(cpy_r_r151.f1);
    CPy_DECREF(cpy_r_r151.f2);
    goto CPyL131;
CPyL128: ;
    cpy_r_r152 = ((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__8;
    if (unlikely(cpy_r_r152.f0 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "connect", "connect_AsyncCursor_gen", "__mypyc_temp__8", -1, CPyStatic_brownie___globals);
        goto CPyL133;
    }
    CPy_INCREF(cpy_r_r152.f0);
    CPy_INCREF(cpy_r_r152.f1);
    CPy_INCREF(cpy_r_r152.f2);
CPyL129: ;
    CPy_RestoreExcInfo(cpy_r_r152);
    CPy_DECREF(cpy_r_r152.f0);
    CPy_DECREF(cpy_r_r152.f1);
    CPy_DECREF(cpy_r_r152.f2);
    cpy_r_r153 = CPy_KeepPropagating();
    if (!cpy_r_r153) goto CPyL133;
    CPy_Unreachable();
CPyL131: ;
    cpy_r_r154 = NULL;
    if (((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__5 != NULL) {
        CPy_DECREF(((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__5);
    }
    ((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__5 = cpy_r_r154;
    cpy_r_r155 = 1;
    if (unlikely(!cpy_r_r155)) {
        CPy_AddTraceback("y/_db/brownie.py", "connect", -1, CPyStatic_brownie___globals);
        goto CPyL193;
    }
CPyL132: ;
    tuple_T3OOO __tmp4 = { NULL, NULL, NULL };
    cpy_r_r156 = __tmp4;
    cpy_r_r9 = cpy_r_r156;
    goto CPyL135;
CPyL133: ;
    cpy_r_r157 = NULL;
    if (((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__5 != NULL) {
        CPy_DECREF(((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__5);
    }
    ((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__5 = cpy_r_r157;
    cpy_r_r158 = 1;
    if (unlikely(!cpy_r_r158)) {
        CPy_AddTraceback("y/_db/brownie.py", "connect", -1, CPyStatic_brownie___globals);
        goto CPyL193;
    }
    cpy_r_r159 = CPy_CatchError();
    cpy_r_r9 = cpy_r_r159;
CPyL135: ;
    cpy_r_r160 = ((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__2;
    if (unlikely(cpy_r_r160 == 2)) {
        CPy_AttributeError("y/_db/brownie.py", "connect", "connect_AsyncCursor_gen", "__mypyc_temp__2", -1, CPyStatic_brownie___globals);
        goto CPyL177;
    }
CPyL136: ;
    if (!cpy_r_r160) goto CPyL168;
CPyL137: ;
    cpy_r_r161 = (PyObject *)&_Py_NoneStruct;
    cpy_r_r162 = ((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__0;
    if (unlikely(cpy_r_r162 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "connect", "connect_AsyncCursor_gen", "__mypyc_temp__0", -1, CPyStatic_brownie___globals);
        goto CPyL177;
    }
    CPy_INCREF(cpy_r_r162);
CPyL138: ;
    cpy_r_r163 = ((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__1;
    if (unlikely(cpy_r_r163 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "connect", "connect_AsyncCursor_gen", "__mypyc_temp__1", -1, CPyStatic_brownie___globals);
        goto CPyL220;
    }
    CPy_INCREF(cpy_r_r163);
CPyL139: ;
    PyObject *cpy_r_r164[4] = {cpy_r_r163, cpy_r_r161, cpy_r_r161, cpy_r_r161};
    cpy_r_r165 = (PyObject **)&cpy_r_r164;
    cpy_r_r166 = PyObject_Vectorcall(cpy_r_r162, cpy_r_r165, 4, 0);
    CPy_DECREF(cpy_r_r162);
    if (unlikely(cpy_r_r166 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "connect", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL221;
    }
    CPy_DECREF(cpy_r_r163);
    cpy_r_r167 = CPy_GetCoro(cpy_r_r166);
    CPy_DECREF(cpy_r_r166);
    if (unlikely(cpy_r_r167 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "connect", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL177;
    }
    if (((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__11 != NULL) {
        CPy_DECREF(((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__11);
    }
    ((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__11 = cpy_r_r167;
    cpy_r_r168 = 1;
    if (unlikely(!cpy_r_r168)) {
        CPy_AddTraceback("y/_db/brownie.py", "connect", -1, CPyStatic_brownie___globals);
        goto CPyL177;
    }
    cpy_r_r169 = ((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__11;
    if (unlikely(cpy_r_r169 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "connect", "connect_AsyncCursor_gen", "__mypyc_temp__11", -1, CPyStatic_brownie___globals);
        goto CPyL177;
    }
    CPy_INCREF(cpy_r_r169);
CPyL143: ;
    cpy_r_r170 = CPyIter_Next(cpy_r_r169);
    CPy_DECREF(cpy_r_r169);
    if (cpy_r_r170 != NULL) goto CPyL222;
    cpy_r_r171 = CPy_FetchStopIterationValue();
    if (unlikely(cpy_r_r171 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "connect", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL177;
    }
    cpy_r_r172 = cpy_r_r171;
    CPy_DECREF(cpy_r_r172);
    cpy_r_r173 = NULL;
    if (((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__11 != NULL) {
        CPy_DECREF(((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__11);
    }
    ((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__11 = cpy_r_r173;
    cpy_r_r174 = 1;
    if (unlikely(!cpy_r_r174)) {
        CPy_AddTraceback("y/_db/brownie.py", "connect", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL177;
    } else
        goto CPyL168;
CPyL146: ;
    cpy_r_r175 = cpy_r_r170;
CPyL147: ;
    ((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_next_label__ = 4;
    return cpy_r_r175;
CPyL148: ;
    cpy_r_r177 = (PyObject *)&_Py_NoneStruct;
    cpy_r_r178 = cpy_r_type != cpy_r_r177;
    if (!cpy_r_r178) goto CPyL223;
    CPyErr_SetObjectAndTraceback(cpy_r_type, cpy_r_value, cpy_r_traceback);
    if (unlikely(!0)) {
        CPy_AddTraceback("y/_db/brownie.py", "connect", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL152;
    } else
        goto CPyL224;
CPyL150: ;
    CPy_Unreachable();
CPyL151: ;
    CPy_INCREF(cpy_r_arg);
    goto CPyL163;
CPyL152: ;
    cpy_r_r179 = CPy_CatchError();
    if (((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__12.f0 != NULL) {
        CPy_DECREF(((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__12.f0);
        CPy_DECREF(((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__12.f1);
        CPy_DECREF(((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__12.f2);
    }
    ((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__12 = cpy_r_r179;
    cpy_r_r180 = 1;
    if (unlikely(!cpy_r_r180)) {
        CPy_AddTraceback("y/_db/brownie.py", "connect", -1, CPyStatic_brownie___globals);
        goto CPyL225;
    }
    cpy_r_r181 = (PyObject **)&cpy_r_r7;
    cpy_r_r182 = ((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__11;
    if (unlikely(cpy_r_r182 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "connect", "connect_AsyncCursor_gen", "__mypyc_temp__11", -1, CPyStatic_brownie___globals);
        goto CPyL225;
    }
    CPy_INCREF(cpy_r_r182);
CPyL154: ;
    cpy_r_r183 = CPy_YieldFromErrorHandle(cpy_r_r182, cpy_r_r181);
    CPy_DecRef(cpy_r_r182);
    if (unlikely(cpy_r_r183 == 2)) {
        CPy_AddTraceback("y/_db/brownie.py", "connect", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL225;
    }
    if (cpy_r_r183) goto CPyL158;
    cpy_r_r175 = cpy_r_r7;
    cpy_r_r184 = ((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__12;
    if (unlikely(cpy_r_r184.f0 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "connect", "connect_AsyncCursor_gen", "__mypyc_temp__12", -1, CPyStatic_brownie___globals);
        goto CPyL226;
    }
    CPy_INCREF(cpy_r_r184.f0);
    CPy_INCREF(cpy_r_r184.f1);
    CPy_INCREF(cpy_r_r184.f2);
    goto CPyL227;
CPyL157: ;
    CPy_RestoreExcInfo(cpy_r_r184);
    CPy_DecRef(cpy_r_r184.f0);
    CPy_DecRef(cpy_r_r184.f1);
    CPy_DecRef(cpy_r_r184.f2);
    goto CPyL147;
CPyL158: ;
    cpy_r_r172 = cpy_r_r7;
    CPy_DecRef(cpy_r_r172);
    cpy_r_r185 = ((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__12;
    if (unlikely(cpy_r_r185.f0 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "connect", "connect_AsyncCursor_gen", "__mypyc_temp__12", -1, CPyStatic_brownie___globals);
        goto CPyL160;
    }
    CPy_INCREF(cpy_r_r185.f0);
    CPy_INCREF(cpy_r_r185.f1);
    CPy_INCREF(cpy_r_r185.f2);
CPyL159: ;
    CPy_RestoreExcInfo(cpy_r_r185);
    CPy_DecRef(cpy_r_r185.f0);
    CPy_DecRef(cpy_r_r185.f1);
    CPy_DecRef(cpy_r_r185.f2);
    goto CPyL168;
CPyL160: ;
    cpy_r_r186 = ((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__12;
    if (unlikely(cpy_r_r186.f0 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "connect", "connect_AsyncCursor_gen", "__mypyc_temp__12", -1, CPyStatic_brownie___globals);
        goto CPyL177;
    }
    CPy_INCREF(cpy_r_r186.f0);
    CPy_INCREF(cpy_r_r186.f1);
    CPy_INCREF(cpy_r_r186.f2);
CPyL161: ;
    CPy_RestoreExcInfo(cpy_r_r186);
    CPy_DecRef(cpy_r_r186.f0);
    CPy_DecRef(cpy_r_r186.f1);
    CPy_DecRef(cpy_r_r186.f2);
    cpy_r_r187 = CPy_KeepPropagating();
    if (!cpy_r_r187) {
        goto CPyL177;
    } else
        goto CPyL228;
CPyL162: ;
    CPy_Unreachable();
CPyL163: ;
    cpy_r_r188 = ((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__11;
    if (unlikely(cpy_r_r188 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "connect", "connect_AsyncCursor_gen", "__mypyc_temp__11", -1, CPyStatic_brownie___globals);
        goto CPyL229;
    }
    CPy_INCREF(cpy_r_r188);
CPyL164: ;
    cpy_r_r189 = CPyIter_Send(cpy_r_r188, cpy_r_arg);
    CPy_DECREF(cpy_r_r188);
    CPy_DECREF(cpy_r_arg);
    if (cpy_r_r189 == NULL) {
        goto CPyL166;
    } else
        goto CPyL230;
CPyL165: ;
    cpy_r_r175 = cpy_r_r189;
    goto CPyL147;
CPyL166: ;
    cpy_r_r190 = CPy_FetchStopIterationValue();
    if (unlikely(cpy_r_r190 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "connect", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL177;
    }
    cpy_r_r172 = cpy_r_r190;
    CPy_DECREF(cpy_r_r172);
CPyL168: ;
    if (cpy_r_r9.f0 == NULL) goto CPyL171;
    CPy_Reraise();
    if (!0) {
        goto CPyL177;
    } else
        goto CPyL231;
CPyL170: ;
    CPy_Unreachable();
CPyL171: ;
    cpy_r_r191 = ((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__5;
    if (cpy_r_r191 != NULL) {
        CPy_INCREF(cpy_r_r191);
    }
    if (cpy_r_r191 == NULL) goto CPyL181;
CPyL172: ;
    ((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_next_label__ = -1;
    if (cpy_r_stop_iter_ptr != NULL) goto CPyL176;
    CPyGen_SetStopIterationValue(cpy_r_r191);
    CPy_DECREF(cpy_r_r191);
    if (!0) goto CPyL193;
    CPy_Unreachable();
CPyL176: ;
    *(PyObject * *)cpy_r_stop_iter_ptr = cpy_r_r191;
    return 0;
CPyL177: ;
    if (cpy_r_r9.f0 == NULL) goto CPyL179;
    CPy_RestoreExcInfo(cpy_r_r9);
    CPy_XDECREF(cpy_r_r9.f0);
    CPy_XDECREF(cpy_r_r9.f1);
    CPy_XDECREF(cpy_r_r9.f2);
CPyL179: ;
    cpy_r_r193 = CPy_KeepPropagating();
    if (!cpy_r_r193) goto CPyL193;
    CPy_Unreachable();
CPyL181: ;
    cpy_r_r194 = Py_None;
    ((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_next_label__ = -1;
    if (cpy_r_stop_iter_ptr != NULL) goto CPyL185;
    CPyGen_SetStopIterationValue(cpy_r_r194);
    if (!0) goto CPyL193;
    CPy_Unreachable();
CPyL185: ;
    *(PyObject * *)cpy_r_stop_iter_ptr = cpy_r_r194;
    return 0;
CPyL186: ;
    cpy_r_r196 = cpy_r_r10 == 0;
    if (cpy_r_r196) goto CPyL232;
    cpy_r_r197 = cpy_r_r10 == 1;
    if (cpy_r_r197) {
        goto CPyL233;
    } else
        goto CPyL234;
CPyL188: ;
    cpy_r_r198 = cpy_r_r10 == 2;
    if (cpy_r_r198) {
        goto CPyL235;
    } else
        goto CPyL236;
CPyL189: ;
    cpy_r_r199 = cpy_r_r10 == 3;
    if (cpy_r_r199) {
        goto CPyL237;
    } else
        goto CPyL238;
CPyL190: ;
    cpy_r_r200 = cpy_r_r10 == 4;
    if (cpy_r_r200) {
        goto CPyL148;
    } else
        goto CPyL239;
CPyL191: ;
    PyErr_SetNone(PyExc_StopIteration);
    cpy_r_r201 = 0;
    if (unlikely(!cpy_r_r201)) {
        CPy_AddTraceback("y/_db/brownie.py", "connect", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL193;
    }
    CPy_Unreachable();
CPyL193: ;
    cpy_r_r202 = NULL;
    return cpy_r_r202;
CPyL194: ;
    CPy_DecRef(cpy_r_r28);
    goto CPyL193;
CPyL195: ;
    CPy_DecRef(cpy_r_r36);
    goto CPyL193;
CPyL196: ;
    CPy_XDECREF(cpy_r_r1);
    goto CPyL32;
CPyL197: ;
    CPy_XDECREF(cpy_r_r1);
    goto CPyL31;
CPyL198: ;
    CPy_XDecRef(cpy_r_r1);
    goto CPyL41;
CPyL199: ;
    CPy_DecRef(cpy_r_r47);
    goto CPyL41;
CPyL200: ;
    CPy_DecRef(cpy_r_arg);
    goto CPyL193;
CPyL201: ;
    CPy_DecRef(cpy_r_r70);
    goto CPyL89;
CPyL202: ;
    CPy_DecRef(cpy_r_r84);
    goto CPyL89;
CPyL203: ;
    CPy_XDECREF(cpy_r_r3);
    goto CPyL66;
CPyL204: ;
    CPy_XDECREF(cpy_r_r3);
    goto CPyL65;
CPyL205: ;
    CPy_XDecRef(cpy_r_r3);
    goto CPyL75;
CPyL206: ;
    CPy_DecRef(cpy_r_r87);
    goto CPyL75;
CPyL207: ;
    CPy_DecRef(cpy_r_r84);
    goto CPyL75;
CPyL208: ;
    CPy_DecRef(cpy_r_arg);
    goto CPyL89;
CPyL209: ;
    CPy_DecRef(cpy_r_r109);
    goto CPyL89;
CPyL210: ;
    CPy_DecRef(cpy_r_r116);
    CPy_DecRef(cpy_r_r117);
    CPy_DecRef(cpy_r_r118);
    goto CPyL128;
CPyL211: ;
    CPy_DecRef(cpy_r_r116);
    CPy_DecRef(cpy_r_r117);
    CPy_DecRef(cpy_r_r118);
    CPy_DecRef(cpy_r_r119);
    goto CPyL128;
CPyL212: ;
    CPy_DecRef(cpy_r_r116);
    CPy_DecRef(cpy_r_r117);
    CPy_DecRef(cpy_r_r118);
    CPy_DecRef(cpy_r_r120);
    goto CPyL128;
CPyL213: ;
    CPy_DecRef(cpy_r_r129);
    goto CPyL128;
CPyL214: ;
    CPy_XDECREF(cpy_r_r5);
    goto CPyL105;
CPyL215: ;
    CPy_XDECREF(cpy_r_r5);
    goto CPyL104;
CPyL216: ;
    CPy_XDecRef(cpy_r_r5);
    goto CPyL114;
CPyL217: ;
    CPy_DecRef(cpy_r_r132);
    goto CPyL114;
CPyL218: ;
    CPy_DecRef(cpy_r_r129);
    goto CPyL114;
CPyL219: ;
    CPy_DecRef(cpy_r_arg);
    goto CPyL128;
CPyL220: ;
    CPy_DecRef(cpy_r_r162);
    goto CPyL177;
CPyL221: ;
    CPy_DecRef(cpy_r_r163);
    goto CPyL177;
CPyL222: ;
    CPy_XDECREF(cpy_r_r9.f0);
    CPy_XDECREF(cpy_r_r9.f1);
    CPy_XDECREF(cpy_r_r9.f2);
    goto CPyL146;
CPyL223: ;
    CPy_XDECREF(cpy_r_r7);
    goto CPyL151;
CPyL224: ;
    CPy_XDECREF(cpy_r_r7);
    CPy_XDECREF(cpy_r_r9.f0);
    CPy_XDECREF(cpy_r_r9.f1);
    CPy_XDECREF(cpy_r_r9.f2);
    goto CPyL150;
CPyL225: ;
    CPy_XDecRef(cpy_r_r7);
    goto CPyL160;
CPyL226: ;
    CPy_DecRef(cpy_r_r175);
    goto CPyL160;
CPyL227: ;
    CPy_XDecRef(cpy_r_r9.f0);
    CPy_XDecRef(cpy_r_r9.f1);
    CPy_XDecRef(cpy_r_r9.f2);
    goto CPyL157;
CPyL228: ;
    CPy_XDecRef(cpy_r_r9.f0);
    CPy_XDecRef(cpy_r_r9.f1);
    CPy_XDecRef(cpy_r_r9.f2);
    goto CPyL162;
CPyL229: ;
    CPy_DecRef(cpy_r_arg);
    goto CPyL177;
CPyL230: ;
    CPy_XDECREF(cpy_r_r9.f0);
    CPy_XDECREF(cpy_r_r9.f1);
    CPy_XDECREF(cpy_r_r9.f2);
    goto CPyL165;
CPyL231: ;
    CPy_XDECREF(cpy_r_r9.f0);
    CPy_XDECREF(cpy_r_r9.f1);
    CPy_XDECREF(cpy_r_r9.f2);
    goto CPyL170;
CPyL232: ;
    CPy_XDECREF(cpy_r_r1);
    CPy_XDECREF(cpy_r_r3);
    CPy_XDECREF(cpy_r_r5);
    CPy_XDECREF(cpy_r_r7);
    CPy_XDECREF(cpy_r_r9.f0);
    CPy_XDECREF(cpy_r_r9.f1);
    CPy_XDECREF(cpy_r_r9.f2);
    goto CPyL1;
CPyL233: ;
    CPy_XDECREF(cpy_r_r3);
    CPy_XDECREF(cpy_r_r5);
    CPy_XDECREF(cpy_r_r7);
    CPy_XDECREF(cpy_r_r9.f0);
    CPy_XDECREF(cpy_r_r9.f1);
    CPy_XDECREF(cpy_r_r9.f2);
    goto CPyL29;
CPyL234: ;
    CPy_XDECREF(cpy_r_r1);
    goto CPyL188;
CPyL235: ;
    CPy_XDECREF(cpy_r_r5);
    CPy_XDECREF(cpy_r_r7);
    CPy_XDECREF(cpy_r_r9.f0);
    CPy_XDECREF(cpy_r_r9.f1);
    CPy_XDECREF(cpy_r_r9.f2);
    goto CPyL63;
CPyL236: ;
    CPy_XDECREF(cpy_r_r3);
    goto CPyL189;
CPyL237: ;
    CPy_XDECREF(cpy_r_r7);
    CPy_XDECREF(cpy_r_r9.f0);
    CPy_XDECREF(cpy_r_r9.f1);
    CPy_XDECREF(cpy_r_r9.f2);
    goto CPyL102;
CPyL238: ;
    CPy_XDECREF(cpy_r_r5);
    goto CPyL190;
CPyL239: ;
    CPy_XDECREF(cpy_r_r7);
    CPy_XDECREF(cpy_r_r9.f0);
    CPy_XDECREF(cpy_r_r9.f1);
    CPy_XDECREF(cpy_r_r9.f2);
    goto CPyL191;
}

PyObject *CPyDef_brownie___connect_AsyncCursor_gen_____next__(PyObject *cpy_r___mypyc_self__) {
    PyObject *cpy_r_r0;
    PyObject *cpy_r_r1;
    PyObject *cpy_r_r2;
    cpy_r_r0 = (PyObject *)&_Py_NoneStruct;
    cpy_r_r1 = CPyDef_brownie___connect_AsyncCursor_gen_____mypyc_generator_helper__(cpy_r___mypyc_self__, cpy_r_r0, cpy_r_r0, cpy_r_r0, cpy_r_r0, 0);
    if (cpy_r_r1 == NULL) goto CPyL2;
    return cpy_r_r1;
CPyL2: ;
    cpy_r_r2 = NULL;
    return cpy_r_r2;
}

PyObject *CPyPy_brownie___connect_AsyncCursor_gen_____next__(PyObject *self, PyObject *const *args, size_t nargs, PyObject *kwnames) {
    PyObject *obj___mypyc_self__ = self;
    static const char * const kwlist[] = {0};
    static CPyArg_Parser parser = {":__next__", kwlist, 0};
    if (!CPyArg_ParseStackAndKeywordsNoArgs(args, nargs, kwnames, &parser)) {
        return NULL;
    }
    PyObject *arg___mypyc_self__;
    if (likely(Py_TYPE(obj___mypyc_self__) == CPyType_brownie___connect_AsyncCursor_gen))
        arg___mypyc_self__ = obj___mypyc_self__;
    else {
        CPy_TypeError("y._db.brownie.connect_AsyncCursor_gen", obj___mypyc_self__); 
        goto fail;
    }
    PyObject *retval = CPyDef_brownie___connect_AsyncCursor_gen_____next__(arg___mypyc_self__);
    return retval;
fail: ;
    CPy_AddTraceback("y/_db/brownie.py", "__next__", -1, CPyStatic_brownie___globals);
    return NULL;
}

PyObject *CPyDef_brownie___connect_AsyncCursor_gen___send(PyObject *cpy_r___mypyc_self__, PyObject *cpy_r_arg) {
    PyObject *cpy_r_r0;
    PyObject *cpy_r_r1;
    PyObject *cpy_r_r2;
    cpy_r_r0 = (PyObject *)&_Py_NoneStruct;
    cpy_r_r1 = CPyDef_brownie___connect_AsyncCursor_gen_____mypyc_generator_helper__(cpy_r___mypyc_self__, cpy_r_r0, cpy_r_r0, cpy_r_r0, cpy_r_arg, 0);
    if (cpy_r_r1 == NULL) goto CPyL2;
    return cpy_r_r1;
CPyL2: ;
    cpy_r_r2 = NULL;
    return cpy_r_r2;
}

PyObject *CPyPy_brownie___connect_AsyncCursor_gen___send(PyObject *self, PyObject *const *args, size_t nargs, PyObject *kwnames) {
    PyObject *obj___mypyc_self__ = self;
    static const char * const kwlist[] = {"arg", 0};
    static CPyArg_Parser parser = {"O:send", kwlist, 0};
    PyObject *obj_arg;
    if (!CPyArg_ParseStackAndKeywordsOneArg(args, nargs, kwnames, &parser, &obj_arg)) {
        return NULL;
    }
    PyObject *arg___mypyc_self__;
    if (likely(Py_TYPE(obj___mypyc_self__) == CPyType_brownie___connect_AsyncCursor_gen))
        arg___mypyc_self__ = obj___mypyc_self__;
    else {
        CPy_TypeError("y._db.brownie.connect_AsyncCursor_gen", obj___mypyc_self__); 
        goto fail;
    }
    PyObject *arg_arg = obj_arg;
    PyObject *retval = CPyDef_brownie___connect_AsyncCursor_gen___send(arg___mypyc_self__, arg_arg);
    return retval;
fail: ;
    CPy_AddTraceback("y/_db/brownie.py", "send", -1, CPyStatic_brownie___globals);
    return NULL;
}

PyObject *CPyDef_brownie___connect_AsyncCursor_gen_____iter__(PyObject *cpy_r___mypyc_self__) {
    CPy_INCREF_NO_IMM(cpy_r___mypyc_self__);
    return cpy_r___mypyc_self__;
}

PyObject *CPyPy_brownie___connect_AsyncCursor_gen_____iter__(PyObject *self, PyObject *const *args, size_t nargs, PyObject *kwnames) {
    PyObject *obj___mypyc_self__ = self;
    static const char * const kwlist[] = {0};
    static CPyArg_Parser parser = {":__iter__", kwlist, 0};
    if (!CPyArg_ParseStackAndKeywordsNoArgs(args, nargs, kwnames, &parser)) {
        return NULL;
    }
    PyObject *arg___mypyc_self__;
    if (likely(Py_TYPE(obj___mypyc_self__) == CPyType_brownie___connect_AsyncCursor_gen))
        arg___mypyc_self__ = obj___mypyc_self__;
    else {
        CPy_TypeError("y._db.brownie.connect_AsyncCursor_gen", obj___mypyc_self__); 
        goto fail;
    }
    PyObject *retval = CPyDef_brownie___connect_AsyncCursor_gen_____iter__(arg___mypyc_self__);
    return retval;
fail: ;
    CPy_AddTraceback("y/_db/brownie.py", "__iter__", -1, CPyStatic_brownie___globals);
    return NULL;
}

PyObject *CPyDef_brownie___connect_AsyncCursor_gen___throw(PyObject *cpy_r___mypyc_self__, PyObject *cpy_r_type, PyObject *cpy_r_value, PyObject *cpy_r_traceback) {
    PyObject *cpy_r_r0;
    PyObject *cpy_r_r1;
    PyObject *cpy_r_r2;
    cpy_r_r0 = (PyObject *)&_Py_NoneStruct;
    if (cpy_r_value != NULL) goto CPyL7;
    CPy_INCREF(cpy_r_r0);
    cpy_r_value = cpy_r_r0;
CPyL2: ;
    if (cpy_r_traceback != NULL) goto CPyL8;
    CPy_INCREF(cpy_r_r0);
    cpy_r_traceback = cpy_r_r0;
CPyL4: ;
    cpy_r_r1 = CPyDef_brownie___connect_AsyncCursor_gen_____mypyc_generator_helper__(cpy_r___mypyc_self__, cpy_r_type, cpy_r_value, cpy_r_traceback, cpy_r_r0, 0);
    CPy_DECREF(cpy_r_value);
    CPy_DECREF(cpy_r_traceback);
    if (cpy_r_r1 == NULL) goto CPyL6;
    return cpy_r_r1;
CPyL6: ;
    cpy_r_r2 = NULL;
    return cpy_r_r2;
CPyL7: ;
    CPy_INCREF(cpy_r_value);
    goto CPyL2;
CPyL8: ;
    CPy_INCREF(cpy_r_traceback);
    goto CPyL4;
}

PyObject *CPyPy_brownie___connect_AsyncCursor_gen___throw(PyObject *self, PyObject *const *args, size_t nargs, PyObject *kwnames) {
    PyObject *obj___mypyc_self__ = self;
    static const char * const kwlist[] = {"type", "value", "traceback", 0};
    static CPyArg_Parser parser = {"O|OO:throw", kwlist, 0};
    PyObject *obj_type;
    PyObject *obj_value = NULL;
    PyObject *obj_traceback = NULL;
    if (!CPyArg_ParseStackAndKeywordsSimple(args, nargs, kwnames, &parser, &obj_type, &obj_value, &obj_traceback)) {
        return NULL;
    }
    PyObject *arg___mypyc_self__;
    if (likely(Py_TYPE(obj___mypyc_self__) == CPyType_brownie___connect_AsyncCursor_gen))
        arg___mypyc_self__ = obj___mypyc_self__;
    else {
        CPy_TypeError("y._db.brownie.connect_AsyncCursor_gen", obj___mypyc_self__); 
        goto fail;
    }
    PyObject *arg_type = obj_type;
    PyObject *arg_value;
    if (obj_value == NULL) {
        arg_value = NULL;
    } else {
        arg_value = obj_value; 
    }
    PyObject *arg_traceback;
    if (obj_traceback == NULL) {
        arg_traceback = NULL;
    } else {
        arg_traceback = obj_traceback; 
    }
    PyObject *retval = CPyDef_brownie___connect_AsyncCursor_gen___throw(arg___mypyc_self__, arg_type, arg_value, arg_traceback);
    return retval;
fail: ;
    CPy_AddTraceback("y/_db/brownie.py", "throw", -1, CPyStatic_brownie___globals);
    return NULL;
}

PyObject *CPyDef_brownie___connect_AsyncCursor_gen___close(PyObject *cpy_r___mypyc_self__) {
    PyObject *cpy_r_r0;
    PyObject *cpy_r_r1;
    PyObject *cpy_r_r2;
    PyObject *cpy_r_r3;
    PyObject *cpy_r_r4;
    PyObject *cpy_r_r5;
    tuple_T3OOO cpy_r_r6;
    PyObject *cpy_r_r7;
    PyObject *cpy_r_r8;
    PyObject *cpy_r_r9;
    tuple_T2OO cpy_r_r10;
    PyObject *cpy_r_r11;
    char cpy_r_r12;
    PyObject *cpy_r_r13;
    char cpy_r_r14;
    PyObject *cpy_r_r15;
    cpy_r_r0 = CPyModule_builtins;
    cpy_r_r1 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'GeneratorExit' */
    cpy_r_r2 = CPyObject_GetAttr(cpy_r_r0, cpy_r_r1);
    if (cpy_r_r2 == NULL) goto CPyL3;
    cpy_r_r3 = (PyObject *)&_Py_NoneStruct;
    cpy_r_r4 = (PyObject *)&_Py_NoneStruct;
    cpy_r_r5 = CPyDef_brownie___connect_AsyncCursor_gen___throw(cpy_r___mypyc_self__, cpy_r_r2, cpy_r_r3, cpy_r_r4);
    if (cpy_r_r5 != NULL) goto CPyL11;
CPyL3: ;
    cpy_r_r6 = CPy_CatchError();
    cpy_r_r7 = CPyModule_builtins;
    cpy_r_r8 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'StopIteration' */
    cpy_r_r9 = CPyObject_GetAttr(cpy_r_r7, cpy_r_r8);
    if (cpy_r_r9 == NULL) goto CPyL12;
    cpy_r_r10.f0 = cpy_r_r2;
    cpy_r_r10.f1 = cpy_r_r9;
    cpy_r_r11 = PyTuple_New(2);
    if (unlikely(cpy_r_r11 == NULL))
        CPyError_OutOfMemory();
    PyObject *__tmp5 = cpy_r_r10.f0;
    PyTuple_SET_ITEM(cpy_r_r11, 0, __tmp5);
    PyObject *__tmp6 = cpy_r_r10.f1;
    PyTuple_SET_ITEM(cpy_r_r11, 1, __tmp6);
    cpy_r_r12 = CPy_ExceptionMatches(cpy_r_r11);
    CPy_DECREF(cpy_r_r11);
    if (!cpy_r_r12) goto CPyL13;
    CPy_RestoreExcInfo(cpy_r_r6);
    CPy_DECREF(cpy_r_r6.f0);
    CPy_DECREF(cpy_r_r6.f1);
    CPy_DECREF(cpy_r_r6.f2);
    cpy_r_r13 = (PyObject *)&_Py_NoneStruct;
    CPy_INCREF(cpy_r_r13);
    return cpy_r_r13;
CPyL6: ;
    CPy_Reraise();
    if (!0) goto CPyL10;
    CPy_Unreachable();
CPyL8: ;
    PyErr_SetString(PyExc_RuntimeError, "generator ignored GeneratorExit");
    cpy_r_r14 = 0;
    if (!cpy_r_r14) goto CPyL10;
    CPy_Unreachable();
CPyL10: ;
    cpy_r_r15 = NULL;
    return cpy_r_r15;
CPyL11: ;
    CPy_DECREF(cpy_r_r2);
    CPy_DECREF(cpy_r_r5);
    goto CPyL8;
CPyL12: ;
    CPy_DECREF(cpy_r_r2);
    CPy_DECREF(cpy_r_r6.f0);
    CPy_DECREF(cpy_r_r6.f1);
    CPy_DECREF(cpy_r_r6.f2);
    goto CPyL10;
CPyL13: ;
    CPy_DECREF(cpy_r_r6.f0);
    CPy_DECREF(cpy_r_r6.f1);
    CPy_DECREF(cpy_r_r6.f2);
    goto CPyL6;
}

PyObject *CPyPy_brownie___connect_AsyncCursor_gen___close(PyObject *self, PyObject *const *args, size_t nargs, PyObject *kwnames) {
    PyObject *obj___mypyc_self__ = self;
    static const char * const kwlist[] = {0};
    static CPyArg_Parser parser = {":close", kwlist, 0};
    if (!CPyArg_ParseStackAndKeywordsNoArgs(args, nargs, kwnames, &parser)) {
        return NULL;
    }
    PyObject *arg___mypyc_self__;
    if (likely(Py_TYPE(obj___mypyc_self__) == CPyType_brownie___connect_AsyncCursor_gen))
        arg___mypyc_self__ = obj___mypyc_self__;
    else {
        CPy_TypeError("y._db.brownie.connect_AsyncCursor_gen", obj___mypyc_self__); 
        goto fail;
    }
    PyObject *retval = CPyDef_brownie___connect_AsyncCursor_gen___close(arg___mypyc_self__);
    return retval;
fail: ;
    CPy_AddTraceback("y/_db/brownie.py", "close", -1, CPyStatic_brownie___globals);
    return NULL;
}

PyObject *CPyDef_brownie___connect_AsyncCursor_gen_____await__(PyObject *cpy_r___mypyc_self__) {
    CPy_INCREF_NO_IMM(cpy_r___mypyc_self__);
    return cpy_r___mypyc_self__;
}

PyObject *CPyPy_brownie___connect_AsyncCursor_gen_____await__(PyObject *self, PyObject *const *args, size_t nargs, PyObject *kwnames) {
    PyObject *obj___mypyc_self__ = self;
    static const char * const kwlist[] = {0};
    static CPyArg_Parser parser = {":__await__", kwlist, 0};
    if (!CPyArg_ParseStackAndKeywordsNoArgs(args, nargs, kwnames, &parser)) {
        return NULL;
    }
    PyObject *arg___mypyc_self__;
    if (likely(Py_TYPE(obj___mypyc_self__) == CPyType_brownie___connect_AsyncCursor_gen))
        arg___mypyc_self__ = obj___mypyc_self__;
    else {
        CPy_TypeError("y._db.brownie.connect_AsyncCursor_gen", obj___mypyc_self__); 
        goto fail;
    }
    PyObject *retval = CPyDef_brownie___connect_AsyncCursor_gen_____await__(arg___mypyc_self__);
    return retval;
fail: ;
    CPy_AddTraceback("y/_db/brownie.py", "__await__", -1, CPyStatic_brownie___globals);
    return NULL;
}

PyObject *CPyDef_brownie___AsyncCursor___connect(PyObject *cpy_r_self) {
    PyObject *cpy_r_r0;
    char cpy_r_r1;
    char cpy_r_r2;
    PyObject *cpy_r_r3;
    cpy_r_r0 = CPyDef_brownie___connect_AsyncCursor_gen();
    if (unlikely(cpy_r_r0 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "connect", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL3;
    }
    ((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r_r0)->___mypyc_next_label__ = 0;
    CPy_INCREF_NO_IMM(cpy_r_self);
    if (((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r_r0)->___mypyc_generator_attribute__self != NULL) {
        CPy_DECREF_NO_IMM(((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r_r0)->___mypyc_generator_attribute__self);
    }
    ((y____db___brownie___connect_AsyncCursor_genObject *)cpy_r_r0)->___mypyc_generator_attribute__self = cpy_r_self;
    cpy_r_r2 = 1;
    if (unlikely(!cpy_r_r2)) {
        CPy_AddTraceback("y/_db/brownie.py", "connect", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL4;
    }
    return cpy_r_r0;
CPyL3: ;
    cpy_r_r3 = NULL;
    return cpy_r_r3;
CPyL4: ;
    CPy_DecRef(cpy_r_r0);
    goto CPyL3;
}

PyObject *CPyPy_brownie___AsyncCursor___connect(PyObject *self, PyObject *const *args, size_t nargs, PyObject *kwnames) {
    PyObject *obj_self = self;
    static const char * const kwlist[] = {0};
    static CPyArg_Parser parser = {":connect", kwlist, 0};
    if (!CPyArg_ParseStackAndKeywordsNoArgs(args, nargs, kwnames, &parser)) {
        return NULL;
    }
    PyObject *arg_self;
    if (likely(Py_TYPE(obj_self) == CPyType_brownie___AsyncCursor))
        arg_self = obj_self;
    else {
        CPy_TypeError("y._db.brownie.AsyncCursor", obj_self); 
        goto fail;
    }
    PyObject *retval = CPyDef_brownie___AsyncCursor___connect(arg_self);
    return retval;
fail: ;
    CPy_AddTraceback("y/_db/brownie.py", "connect", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
    return NULL;
}

PyObject *CPyDef_brownie___insert_AsyncCursor_gen_____mypyc_generator_helper__(PyObject *cpy_r___mypyc_self__, PyObject *cpy_r_type, PyObject *cpy_r_value, PyObject *cpy_r_traceback, PyObject *cpy_r_arg, PyObject **cpy_r_stop_iter_ptr) {
    int32_t cpy_r_r0;
    PyObject *cpy_r_r1;
    char cpy_r_r2;
    PyObject *cpy_r_r3;
    PyObject *cpy_r_r4;
    PyObject *cpy_r_r5;
    char cpy_r_r6;
    char cpy_r_r7;
    PyObject *cpy_r_r8;
    cpy_r_r0 = ((y____db___brownie___insert_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_next_label__;
    goto CPyL7;
CPyL1: ;
    cpy_r_r1 = (PyObject *)&_Py_NoneStruct;
    cpy_r_r2 = cpy_r_type != cpy_r_r1;
    if (!cpy_r_r2) goto CPyL4;
    CPyErr_SetObjectAndTraceback(cpy_r_type, cpy_r_value, cpy_r_traceback);
    if (unlikely(!0)) {
        CPy_AddTraceback("y/_db/brownie.py", "insert", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL10;
    }
    CPy_Unreachable();
CPyL4: ;
    cpy_r_r3 = CPyModule_builtins;
    cpy_r_r4 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'NotImplementedError' */
    cpy_r_r5 = CPyObject_GetAttr(cpy_r_r3, cpy_r_r4);
    if (unlikely(cpy_r_r5 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "insert", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL10;
    }
    CPy_Raise(cpy_r_r5);
    CPy_DECREF(cpy_r_r5);
    if (unlikely(!0)) {
        CPy_AddTraceback("y/_db/brownie.py", "insert", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL10;
    }
    CPy_Unreachable();
CPyL7: ;
    cpy_r_r6 = cpy_r_r0 == 0;
    if (cpy_r_r6) goto CPyL1;
    PyErr_SetNone(PyExc_StopIteration);
    cpy_r_r7 = 0;
    if (unlikely(!cpy_r_r7)) {
        CPy_AddTraceback("y/_db/brownie.py", "insert", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL10;
    }
    CPy_Unreachable();
CPyL10: ;
    cpy_r_r8 = NULL;
    return cpy_r_r8;
}

PyObject *CPyDef_brownie___insert_AsyncCursor_gen_____next__(PyObject *cpy_r___mypyc_self__) {
    PyObject *cpy_r_r0;
    PyObject *cpy_r_r1;
    PyObject *cpy_r_r2;
    cpy_r_r0 = (PyObject *)&_Py_NoneStruct;
    cpy_r_r1 = CPyDef_brownie___insert_AsyncCursor_gen_____mypyc_generator_helper__(cpy_r___mypyc_self__, cpy_r_r0, cpy_r_r0, cpy_r_r0, cpy_r_r0, 0);
    if (cpy_r_r1 == NULL) goto CPyL2;
    return cpy_r_r1;
CPyL2: ;
    cpy_r_r2 = NULL;
    return cpy_r_r2;
}

PyObject *CPyPy_brownie___insert_AsyncCursor_gen_____next__(PyObject *self, PyObject *const *args, size_t nargs, PyObject *kwnames) {
    PyObject *obj___mypyc_self__ = self;
    static const char * const kwlist[] = {0};
    static CPyArg_Parser parser = {":__next__", kwlist, 0};
    if (!CPyArg_ParseStackAndKeywordsNoArgs(args, nargs, kwnames, &parser)) {
        return NULL;
    }
    PyObject *arg___mypyc_self__;
    if (likely(Py_TYPE(obj___mypyc_self__) == CPyType_brownie___insert_AsyncCursor_gen))
        arg___mypyc_self__ = obj___mypyc_self__;
    else {
        CPy_TypeError("y._db.brownie.insert_AsyncCursor_gen", obj___mypyc_self__); 
        goto fail;
    }
    PyObject *retval = CPyDef_brownie___insert_AsyncCursor_gen_____next__(arg___mypyc_self__);
    return retval;
fail: ;
    CPy_AddTraceback("y/_db/brownie.py", "__next__", -1, CPyStatic_brownie___globals);
    return NULL;
}

PyObject *CPyDef_brownie___insert_AsyncCursor_gen___send(PyObject *cpy_r___mypyc_self__, PyObject *cpy_r_arg) {
    PyObject *cpy_r_r0;
    PyObject *cpy_r_r1;
    PyObject *cpy_r_r2;
    cpy_r_r0 = (PyObject *)&_Py_NoneStruct;
    cpy_r_r1 = CPyDef_brownie___insert_AsyncCursor_gen_____mypyc_generator_helper__(cpy_r___mypyc_self__, cpy_r_r0, cpy_r_r0, cpy_r_r0, cpy_r_arg, 0);
    if (cpy_r_r1 == NULL) goto CPyL2;
    return cpy_r_r1;
CPyL2: ;
    cpy_r_r2 = NULL;
    return cpy_r_r2;
}

PyObject *CPyPy_brownie___insert_AsyncCursor_gen___send(PyObject *self, PyObject *const *args, size_t nargs, PyObject *kwnames) {
    PyObject *obj___mypyc_self__ = self;
    static const char * const kwlist[] = {"arg", 0};
    static CPyArg_Parser parser = {"O:send", kwlist, 0};
    PyObject *obj_arg;
    if (!CPyArg_ParseStackAndKeywordsOneArg(args, nargs, kwnames, &parser, &obj_arg)) {
        return NULL;
    }
    PyObject *arg___mypyc_self__;
    if (likely(Py_TYPE(obj___mypyc_self__) == CPyType_brownie___insert_AsyncCursor_gen))
        arg___mypyc_self__ = obj___mypyc_self__;
    else {
        CPy_TypeError("y._db.brownie.insert_AsyncCursor_gen", obj___mypyc_self__); 
        goto fail;
    }
    PyObject *arg_arg = obj_arg;
    PyObject *retval = CPyDef_brownie___insert_AsyncCursor_gen___send(arg___mypyc_self__, arg_arg);
    return retval;
fail: ;
    CPy_AddTraceback("y/_db/brownie.py", "send", -1, CPyStatic_brownie___globals);
    return NULL;
}

PyObject *CPyDef_brownie___insert_AsyncCursor_gen_____iter__(PyObject *cpy_r___mypyc_self__) {
    CPy_INCREF_NO_IMM(cpy_r___mypyc_self__);
    return cpy_r___mypyc_self__;
}

PyObject *CPyPy_brownie___insert_AsyncCursor_gen_____iter__(PyObject *self, PyObject *const *args, size_t nargs, PyObject *kwnames) {
    PyObject *obj___mypyc_self__ = self;
    static const char * const kwlist[] = {0};
    static CPyArg_Parser parser = {":__iter__", kwlist, 0};
    if (!CPyArg_ParseStackAndKeywordsNoArgs(args, nargs, kwnames, &parser)) {
        return NULL;
    }
    PyObject *arg___mypyc_self__;
    if (likely(Py_TYPE(obj___mypyc_self__) == CPyType_brownie___insert_AsyncCursor_gen))
        arg___mypyc_self__ = obj___mypyc_self__;
    else {
        CPy_TypeError("y._db.brownie.insert_AsyncCursor_gen", obj___mypyc_self__); 
        goto fail;
    }
    PyObject *retval = CPyDef_brownie___insert_AsyncCursor_gen_____iter__(arg___mypyc_self__);
    return retval;
fail: ;
    CPy_AddTraceback("y/_db/brownie.py", "__iter__", -1, CPyStatic_brownie___globals);
    return NULL;
}

PyObject *CPyDef_brownie___insert_AsyncCursor_gen___throw(PyObject *cpy_r___mypyc_self__, PyObject *cpy_r_type, PyObject *cpy_r_value, PyObject *cpy_r_traceback) {
    PyObject *cpy_r_r0;
    PyObject *cpy_r_r1;
    PyObject *cpy_r_r2;
    cpy_r_r0 = (PyObject *)&_Py_NoneStruct;
    if (cpy_r_value != NULL) goto CPyL7;
    CPy_INCREF(cpy_r_r0);
    cpy_r_value = cpy_r_r0;
CPyL2: ;
    if (cpy_r_traceback != NULL) goto CPyL8;
    CPy_INCREF(cpy_r_r0);
    cpy_r_traceback = cpy_r_r0;
CPyL4: ;
    cpy_r_r1 = CPyDef_brownie___insert_AsyncCursor_gen_____mypyc_generator_helper__(cpy_r___mypyc_self__, cpy_r_type, cpy_r_value, cpy_r_traceback, cpy_r_r0, 0);
    CPy_DECREF(cpy_r_value);
    CPy_DECREF(cpy_r_traceback);
    if (cpy_r_r1 == NULL) goto CPyL6;
    return cpy_r_r1;
CPyL6: ;
    cpy_r_r2 = NULL;
    return cpy_r_r2;
CPyL7: ;
    CPy_INCREF(cpy_r_value);
    goto CPyL2;
CPyL8: ;
    CPy_INCREF(cpy_r_traceback);
    goto CPyL4;
}

PyObject *CPyPy_brownie___insert_AsyncCursor_gen___throw(PyObject *self, PyObject *const *args, size_t nargs, PyObject *kwnames) {
    PyObject *obj___mypyc_self__ = self;
    static const char * const kwlist[] = {"type", "value", "traceback", 0};
    static CPyArg_Parser parser = {"O|OO:throw", kwlist, 0};
    PyObject *obj_type;
    PyObject *obj_value = NULL;
    PyObject *obj_traceback = NULL;
    if (!CPyArg_ParseStackAndKeywordsSimple(args, nargs, kwnames, &parser, &obj_type, &obj_value, &obj_traceback)) {
        return NULL;
    }
    PyObject *arg___mypyc_self__;
    if (likely(Py_TYPE(obj___mypyc_self__) == CPyType_brownie___insert_AsyncCursor_gen))
        arg___mypyc_self__ = obj___mypyc_self__;
    else {
        CPy_TypeError("y._db.brownie.insert_AsyncCursor_gen", obj___mypyc_self__); 
        goto fail;
    }
    PyObject *arg_type = obj_type;
    PyObject *arg_value;
    if (obj_value == NULL) {
        arg_value = NULL;
    } else {
        arg_value = obj_value; 
    }
    PyObject *arg_traceback;
    if (obj_traceback == NULL) {
        arg_traceback = NULL;
    } else {
        arg_traceback = obj_traceback; 
    }
    PyObject *retval = CPyDef_brownie___insert_AsyncCursor_gen___throw(arg___mypyc_self__, arg_type, arg_value, arg_traceback);
    return retval;
fail: ;
    CPy_AddTraceback("y/_db/brownie.py", "throw", -1, CPyStatic_brownie___globals);
    return NULL;
}

PyObject *CPyDef_brownie___insert_AsyncCursor_gen___close(PyObject *cpy_r___mypyc_self__) {
    PyObject *cpy_r_r0;
    PyObject *cpy_r_r1;
    PyObject *cpy_r_r2;
    PyObject *cpy_r_r3;
    PyObject *cpy_r_r4;
    PyObject *cpy_r_r5;
    tuple_T3OOO cpy_r_r6;
    PyObject *cpy_r_r7;
    PyObject *cpy_r_r8;
    PyObject *cpy_r_r9;
    tuple_T2OO cpy_r_r10;
    PyObject *cpy_r_r11;
    char cpy_r_r12;
    PyObject *cpy_r_r13;
    char cpy_r_r14;
    PyObject *cpy_r_r15;
    cpy_r_r0 = CPyModule_builtins;
    cpy_r_r1 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'GeneratorExit' */
    cpy_r_r2 = CPyObject_GetAttr(cpy_r_r0, cpy_r_r1);
    if (cpy_r_r2 == NULL) goto CPyL3;
    cpy_r_r3 = (PyObject *)&_Py_NoneStruct;
    cpy_r_r4 = (PyObject *)&_Py_NoneStruct;
    cpy_r_r5 = CPyDef_brownie___insert_AsyncCursor_gen___throw(cpy_r___mypyc_self__, cpy_r_r2, cpy_r_r3, cpy_r_r4);
    if (cpy_r_r5 != NULL) goto CPyL11;
CPyL3: ;
    cpy_r_r6 = CPy_CatchError();
    cpy_r_r7 = CPyModule_builtins;
    cpy_r_r8 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'StopIteration' */
    cpy_r_r9 = CPyObject_GetAttr(cpy_r_r7, cpy_r_r8);
    if (cpy_r_r9 == NULL) goto CPyL12;
    cpy_r_r10.f0 = cpy_r_r2;
    cpy_r_r10.f1 = cpy_r_r9;
    cpy_r_r11 = PyTuple_New(2);
    if (unlikely(cpy_r_r11 == NULL))
        CPyError_OutOfMemory();
    PyObject *__tmp7 = cpy_r_r10.f0;
    PyTuple_SET_ITEM(cpy_r_r11, 0, __tmp7);
    PyObject *__tmp8 = cpy_r_r10.f1;
    PyTuple_SET_ITEM(cpy_r_r11, 1, __tmp8);
    cpy_r_r12 = CPy_ExceptionMatches(cpy_r_r11);
    CPy_DECREF(cpy_r_r11);
    if (!cpy_r_r12) goto CPyL13;
    CPy_RestoreExcInfo(cpy_r_r6);
    CPy_DECREF(cpy_r_r6.f0);
    CPy_DECREF(cpy_r_r6.f1);
    CPy_DECREF(cpy_r_r6.f2);
    cpy_r_r13 = (PyObject *)&_Py_NoneStruct;
    CPy_INCREF(cpy_r_r13);
    return cpy_r_r13;
CPyL6: ;
    CPy_Reraise();
    if (!0) goto CPyL10;
    CPy_Unreachable();
CPyL8: ;
    PyErr_SetString(PyExc_RuntimeError, "generator ignored GeneratorExit");
    cpy_r_r14 = 0;
    if (!cpy_r_r14) goto CPyL10;
    CPy_Unreachable();
CPyL10: ;
    cpy_r_r15 = NULL;
    return cpy_r_r15;
CPyL11: ;
    CPy_DECREF(cpy_r_r2);
    CPy_DECREF(cpy_r_r5);
    goto CPyL8;
CPyL12: ;
    CPy_DECREF(cpy_r_r2);
    CPy_DECREF(cpy_r_r6.f0);
    CPy_DECREF(cpy_r_r6.f1);
    CPy_DECREF(cpy_r_r6.f2);
    goto CPyL10;
CPyL13: ;
    CPy_DECREF(cpy_r_r6.f0);
    CPy_DECREF(cpy_r_r6.f1);
    CPy_DECREF(cpy_r_r6.f2);
    goto CPyL6;
}

PyObject *CPyPy_brownie___insert_AsyncCursor_gen___close(PyObject *self, PyObject *const *args, size_t nargs, PyObject *kwnames) {
    PyObject *obj___mypyc_self__ = self;
    static const char * const kwlist[] = {0};
    static CPyArg_Parser parser = {":close", kwlist, 0};
    if (!CPyArg_ParseStackAndKeywordsNoArgs(args, nargs, kwnames, &parser)) {
        return NULL;
    }
    PyObject *arg___mypyc_self__;
    if (likely(Py_TYPE(obj___mypyc_self__) == CPyType_brownie___insert_AsyncCursor_gen))
        arg___mypyc_self__ = obj___mypyc_self__;
    else {
        CPy_TypeError("y._db.brownie.insert_AsyncCursor_gen", obj___mypyc_self__); 
        goto fail;
    }
    PyObject *retval = CPyDef_brownie___insert_AsyncCursor_gen___close(arg___mypyc_self__);
    return retval;
fail: ;
    CPy_AddTraceback("y/_db/brownie.py", "close", -1, CPyStatic_brownie___globals);
    return NULL;
}

PyObject *CPyDef_brownie___insert_AsyncCursor_gen_____await__(PyObject *cpy_r___mypyc_self__) {
    CPy_INCREF_NO_IMM(cpy_r___mypyc_self__);
    return cpy_r___mypyc_self__;
}

PyObject *CPyPy_brownie___insert_AsyncCursor_gen_____await__(PyObject *self, PyObject *const *args, size_t nargs, PyObject *kwnames) {
    PyObject *obj___mypyc_self__ = self;
    static const char * const kwlist[] = {0};
    static CPyArg_Parser parser = {":__await__", kwlist, 0};
    if (!CPyArg_ParseStackAndKeywordsNoArgs(args, nargs, kwnames, &parser)) {
        return NULL;
    }
    PyObject *arg___mypyc_self__;
    if (likely(Py_TYPE(obj___mypyc_self__) == CPyType_brownie___insert_AsyncCursor_gen))
        arg___mypyc_self__ = obj___mypyc_self__;
    else {
        CPy_TypeError("y._db.brownie.insert_AsyncCursor_gen", obj___mypyc_self__); 
        goto fail;
    }
    PyObject *retval = CPyDef_brownie___insert_AsyncCursor_gen_____await__(arg___mypyc_self__);
    return retval;
fail: ;
    CPy_AddTraceback("y/_db/brownie.py", "__await__", -1, CPyStatic_brownie___globals);
    return NULL;
}

PyObject *CPyDef_brownie___AsyncCursor___insert(PyObject *cpy_r_self, PyObject *cpy_r_table, PyObject *cpy_r_values) {
    PyObject *cpy_r_r0;
    char cpy_r_r1;
    char cpy_r_r2;
    char cpy_r_r3;
    char cpy_r_r4;
    PyObject *cpy_r_r5;
    cpy_r_r0 = CPyDef_brownie___insert_AsyncCursor_gen();
    if (unlikely(cpy_r_r0 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "insert", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL5;
    }
    ((y____db___brownie___insert_AsyncCursor_genObject *)cpy_r_r0)->___mypyc_next_label__ = 0;
    CPy_INCREF_NO_IMM(cpy_r_self);
    if (((y____db___brownie___insert_AsyncCursor_genObject *)cpy_r_r0)->___mypyc_generator_attribute__self != NULL) {
        CPy_DECREF_NO_IMM(((y____db___brownie___insert_AsyncCursor_genObject *)cpy_r_r0)->___mypyc_generator_attribute__self);
    }
    ((y____db___brownie___insert_AsyncCursor_genObject *)cpy_r_r0)->___mypyc_generator_attribute__self = cpy_r_self;
    cpy_r_r2 = 1;
    if (unlikely(!cpy_r_r2)) {
        CPy_AddTraceback("y/_db/brownie.py", "insert", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL6;
    }
    CPy_INCREF(cpy_r_table);
    if (((y____db___brownie___insert_AsyncCursor_genObject *)cpy_r_r0)->___mypyc_generator_attribute__table != NULL) {
        CPy_DECREF(((y____db___brownie___insert_AsyncCursor_genObject *)cpy_r_r0)->___mypyc_generator_attribute__table);
    }
    ((y____db___brownie___insert_AsyncCursor_genObject *)cpy_r_r0)->___mypyc_generator_attribute__table = cpy_r_table;
    cpy_r_r3 = 1;
    if (unlikely(!cpy_r_r3)) {
        CPy_AddTraceback("y/_db/brownie.py", "insert", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL6;
    }
    CPy_INCREF(cpy_r_values);
    if (((y____db___brownie___insert_AsyncCursor_genObject *)cpy_r_r0)->___mypyc_generator_attribute__values != NULL) {
        CPy_DECREF(((y____db___brownie___insert_AsyncCursor_genObject *)cpy_r_r0)->___mypyc_generator_attribute__values);
    }
    ((y____db___brownie___insert_AsyncCursor_genObject *)cpy_r_r0)->___mypyc_generator_attribute__values = cpy_r_values;
    cpy_r_r4 = 1;
    if (unlikely(!cpy_r_r4)) {
        CPy_AddTraceback("y/_db/brownie.py", "insert", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL6;
    }
    return cpy_r_r0;
CPyL5: ;
    cpy_r_r5 = NULL;
    return cpy_r_r5;
CPyL6: ;
    CPy_DecRef(cpy_r_r0);
    goto CPyL5;
}

PyObject *CPyPy_brownie___AsyncCursor___insert(PyObject *self, PyObject *const *args, size_t nargs, PyObject *kwnames) {
    PyObject *obj_self = self;
    static const char * const kwlist[] = {"table", 0};
    static CPyArg_Parser parser = {"%O:insert", kwlist, 0};
    PyObject *obj_table;
    PyObject *obj_values;
    if (!CPyArg_ParseStackAndKeywords(args, nargs, kwnames, &parser, &obj_values, NULL, &obj_table)) {
        return NULL;
    }
    PyObject *arg_self;
    if (likely(Py_TYPE(obj_self) == CPyType_brownie___AsyncCursor))
        arg_self = obj_self;
    else {
        CPy_TypeError("y._db.brownie.AsyncCursor", obj_self); 
        goto fail;
    }
    PyObject *arg_table;
    if (likely(PyUnicode_Check(obj_table)))
        arg_table = obj_table;
    else {
        CPy_TypeError("str", obj_table); 
        goto fail;
    }
    PyObject *arg_values = obj_values;
    PyObject *retval = CPyDef_brownie___AsyncCursor___insert(arg_self, arg_table, arg_values);
    CPy_DECREF(obj_values);
    return retval;
fail: ;
    CPy_DECREF(obj_values);
    CPy_AddTraceback("y/_db/brownie.py", "insert", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
    return NULL;
}

PyObject *CPyDef_brownie___fetchone_AsyncCursor_gen_____mypyc_generator_helper__(PyObject *cpy_r___mypyc_self__, PyObject *cpy_r_type, PyObject *cpy_r_value, PyObject *cpy_r_traceback, PyObject *cpy_r_arg, PyObject **cpy_r_stop_iter_ptr) {
    PyObject *cpy_r_r0;
    PyObject *cpy_r_r1;
    PyObject *cpy_r_r2;
    PyObject *cpy_r_r3;
    PyObject *cpy_r_r4;
    PyObject *cpy_r_r5;
    PyObject *cpy_r_r6;
    PyObject *cpy_r_r7;
    PyObject *cpy_r_r8;
    PyObject *cpy_r_r9;
    PyObject *cpy_r_r10;
    PyObject *cpy_r_r11;
    PyObject *cpy_r_r12;
    PyObject *cpy_r_r13;
    tuple_T3OOO cpy_r_r14;
    tuple_T3OOO cpy_r_r15;
    PyObject *cpy_r_r16;
    PyObject *cpy_r_r17;
    PyObject *cpy_r_r18;
    PyObject *cpy_r_r19;
    tuple_T3OOO cpy_r_r20;
    tuple_T3OOO cpy_r_r21;
    int32_t cpy_r_r22;
    PyObject *cpy_r_r23;
    char cpy_r_r24;
    PyObject *cpy_r_r25;
    PyObject *cpy_r_r26;
    PyObject *cpy_r_r27;
    char cpy_r_r28;
    PyObject *cpy_r_r29;
    PyObject *cpy_r_r30;
    char cpy_r_r31;
    PyObject *cpy_r_r32;
    PyObject *cpy_r_r33;
    PyObject *cpy_r_r34;
    PyObject **cpy_r_r35;
    PyObject *cpy_r_r36;
    char cpy_r_r37;
    PyObject *cpy_r_r38;
    PyObject *cpy_r_r39;
    char cpy_r_r40;
    PyObject *cpy_r_r41;
    char cpy_r_r42;
    PyObject *cpy_r_r43;
    char cpy_r_r44;
    tuple_T3OOO cpy_r_r45;
    char cpy_r_r46;
    PyObject **cpy_r_r47;
    PyObject *cpy_r_r48;
    char cpy_r_r49;
    tuple_T3OOO cpy_r_r50;
    tuple_T3OOO cpy_r_r51;
    tuple_T3OOO cpy_r_r52;
    char cpy_r_r53;
    PyObject *cpy_r_r54;
    PyObject *cpy_r_r55;
    PyObject *cpy_r_r56;
    PyObject *cpy_r_r57;
    char cpy_r_r58;
    PyObject *cpy_r_r59;
    PyObject *cpy_r_r60;
    PyObject *cpy_r_r61;
    char cpy_r_r62;
    PyObject *cpy_r_r63;
    PyObject *cpy_r_r64;
    PyObject **cpy_r_r66;
    PyObject *cpy_r_r67;
    char cpy_r_r68;
    char cpy_r_r69;
    PyObject *cpy_r_r70;
    char cpy_r_r71;
    PyObject *cpy_r_r72;
    PyObject *cpy_r_r73;
    PyObject *cpy_r_r74;
    PyObject *cpy_r_r75;
    PyObject *cpy_r_r76;
    char cpy_r_r77;
    PyObject *cpy_r_r78;
    char cpy_r_r79;
    PyObject *cpy_r_r80;
    char cpy_r_r81;
    tuple_T3OOO cpy_r_r82;
    char cpy_r_r83;
    PyObject **cpy_r_r84;
    PyObject *cpy_r_r85;
    char cpy_r_r86;
    tuple_T3OOO cpy_r_r87;
    tuple_T3OOO cpy_r_r88;
    tuple_T3OOO cpy_r_r89;
    char cpy_r_r90;
    PyObject *cpy_r_r91;
    PyObject *cpy_r_r92;
    PyObject *cpy_r_r93;
    PyObject *cpy_r_r94;
    PyObject *cpy_r_r95;
    char cpy_r_r96;
    PyObject *cpy_r_r97;
    PyObject *cpy_r_r98;
    PyObject *cpy_r_r99;
    PyObject **cpy_r_r101;
    PyObject *cpy_r_r102;
    PyObject *cpy_r_r103;
    PyObject *cpy_r_r104;
    PyObject *cpy_r_r105;
    char cpy_r_r106;
    PyObject *cpy_r_r107;
    PyObject *cpy_r_r108;
    PyObject **cpy_r_r110;
    PyObject *cpy_r_r111;
    char cpy_r_r112;
    char cpy_r_r113;
    PyObject *cpy_r_r114;
    char cpy_r_r115;
    PyObject *cpy_r_r116;
    PyObject *cpy_r_r117;
    PyObject *cpy_r_r118;
    PyObject *cpy_r_r119;
    PyObject *cpy_r_r120;
    char cpy_r_r121;
    PyObject *cpy_r_r122;
    char cpy_r_r123;
    PyObject *cpy_r_r124;
    char cpy_r_r125;
    tuple_T3OOO cpy_r_r126;
    char cpy_r_r127;
    PyObject **cpy_r_r128;
    PyObject *cpy_r_r129;
    char cpy_r_r130;
    tuple_T3OOO cpy_r_r131;
    tuple_T3OOO cpy_r_r132;
    tuple_T3OOO cpy_r_r133;
    char cpy_r_r134;
    PyObject *cpy_r_r135;
    PyObject *cpy_r_r136;
    PyObject *cpy_r_r137;
    char cpy_r_r138;
    PyObject *cpy_r_r139;
    PyObject *cpy_r_r140;
    PyObject **cpy_r_r142;
    PyObject *cpy_r_r143;
    PyObject *cpy_r_r144;
    char cpy_r_r145;
    PyObject *cpy_r_r146;
    PyObject *cpy_r_r147;
    PyObject *cpy_r_r148;
    PyObject *cpy_r_r149;
    PyObject *cpy_r_r150;
    char cpy_r_r151;
    PyObject *cpy_r_r152;
    char cpy_r_r153;
    PyObject *cpy_r_r154;
    char cpy_r_r155;
    tuple_T3OOO cpy_r_r156;
    char cpy_r_r157;
    PyObject **cpy_r_r158;
    PyObject *cpy_r_r159;
    char cpy_r_r160;
    tuple_T3OOO cpy_r_r161;
    tuple_T3OOO cpy_r_r162;
    tuple_T3OOO cpy_r_r163;
    char cpy_r_r164;
    PyObject *cpy_r_r165;
    PyObject *cpy_r_r166;
    PyObject *cpy_r_r167;
    char cpy_r_r168;
    PyObject *cpy_r_r169;
    PyObject *cpy_r_r170;
    char cpy_r_r171;
    PyObject *cpy_r_r172;
    char cpy_r_r173;
    PyObject *cpy_r_r174;
    char cpy_r_r175;
    PyObject *cpy_r_r176;
    PyObject *cpy_r_r177;
    char cpy_r_r178;
    char cpy_r_r179;
    PyObject *cpy_r_r180;
    PyObject *cpy_r_r181;
    char cpy_r_r182;
    PyObject *cpy_r_r183;
    PyObject *cpy_r_r184;
    PyObject *cpy_r_r185;
    PyObject *cpy_r_r186;
    tuple_T2OO cpy_r_r187;
    PyObject *cpy_r_r188;
    char cpy_r_r189;
    PyObject *cpy_r_r190;
    PyObject *cpy_r_r191;
    char cpy_r_r192;
    PyObject **cpy_r_r194;
    PyObject *cpy_r_r195;
    PyObject *cpy_r_r196;
    PyObject *cpy_r_r197;
    PyObject *cpy_r_r198;
    int32_t cpy_r_r199;
    char cpy_r_r200;
    char cpy_r_r201;
    PyObject *cpy_r_r202;
    PyObject *cpy_r_r203;
    char cpy_r_r204;
    tuple_T3OOO cpy_r_r205;
    char cpy_r_r206;
    char cpy_r_r207;
    tuple_T3OOO cpy_r_r208;
    PyObject *cpy_r_r209;
    PyObject *cpy_r_r210;
    PyObject *cpy_r_r211;
    PyObject *cpy_r_r212;
    PyObject *cpy_r_r213;
    PyObject **cpy_r_r215;
    PyObject *cpy_r_r216;
    PyObject *cpy_r_r217;
    char cpy_r_r218;
    PyObject *cpy_r_r219;
    PyObject *cpy_r_r220;
    PyObject *cpy_r_r221;
    PyObject *cpy_r_r222;
    PyObject *cpy_r_r223;
    char cpy_r_r224;
    PyObject *cpy_r_r225;
    char cpy_r_r226;
    PyObject *cpy_r_r227;
    char cpy_r_r228;
    tuple_T3OOO cpy_r_r229;
    char cpy_r_r230;
    PyObject **cpy_r_r231;
    PyObject *cpy_r_r232;
    char cpy_r_r233;
    tuple_T3OOO cpy_r_r234;
    tuple_T3OOO cpy_r_r235;
    tuple_T3OOO cpy_r_r236;
    char cpy_r_r237;
    PyObject *cpy_r_r238;
    PyObject *cpy_r_r239;
    PyObject *cpy_r_r240;
    int32_t cpy_r_r241;
    char cpy_r_r242;
    char cpy_r_r243;
    tuple_T3OOO cpy_r_r244;
    tuple_T3OOO cpy_r_r245;
    char cpy_r_r246;
    PyObject *cpy_r_r247;
    char cpy_r_r248;
    tuple_T3OOO cpy_r_r249;
    PyObject *cpy_r_r250;
    char cpy_r_r251;
    tuple_T3OOO cpy_r_r252;
    char cpy_r_r253;
    PyObject *cpy_r_r254;
    PyObject *cpy_r_r255;
    PyObject *cpy_r_r256;
    PyObject **cpy_r_r258;
    PyObject *cpy_r_r259;
    PyObject *cpy_r_r260;
    char cpy_r_r261;
    PyObject *cpy_r_r262;
    PyObject *cpy_r_r263;
    PyObject *cpy_r_r264;
    PyObject *cpy_r_r265;
    PyObject *cpy_r_r266;
    char cpy_r_r267;
    PyObject *cpy_r_r268;
    char cpy_r_r269;
    PyObject *cpy_r_r270;
    char cpy_r_r271;
    tuple_T3OOO cpy_r_r272;
    char cpy_r_r273;
    PyObject **cpy_r_r274;
    PyObject *cpy_r_r275;
    char cpy_r_r276;
    tuple_T3OOO cpy_r_r277;
    tuple_T3OOO cpy_r_r278;
    tuple_T3OOO cpy_r_r279;
    char cpy_r_r280;
    PyObject *cpy_r_r281;
    PyObject *cpy_r_r282;
    PyObject *cpy_r_r283;
    PyObject *cpy_r_r284;
    char cpy_r_r285;
    char cpy_r_r286;
    tuple_T3OOO cpy_r_r287;
    char cpy_r_r288;
    char cpy_r_r289;
    tuple_T3OOO cpy_r_r290;
    PyObject *cpy_r_r291;
    PyObject *cpy_r_r292;
    PyObject *cpy_r_r293;
    PyObject *cpy_r_r294;
    PyObject *cpy_r_r295;
    PyObject **cpy_r_r297;
    PyObject *cpy_r_r298;
    PyObject *cpy_r_r299;
    char cpy_r_r300;
    PyObject *cpy_r_r301;
    PyObject *cpy_r_r302;
    PyObject *cpy_r_r303;
    PyObject *cpy_r_r304;
    PyObject *cpy_r_r305;
    char cpy_r_r306;
    PyObject *cpy_r_r307;
    char cpy_r_r308;
    PyObject *cpy_r_r309;
    char cpy_r_r310;
    tuple_T3OOO cpy_r_r311;
    char cpy_r_r312;
    PyObject **cpy_r_r313;
    PyObject *cpy_r_r314;
    char cpy_r_r315;
    tuple_T3OOO cpy_r_r316;
    tuple_T3OOO cpy_r_r317;
    tuple_T3OOO cpy_r_r318;
    char cpy_r_r319;
    PyObject *cpy_r_r320;
    PyObject *cpy_r_r321;
    PyObject *cpy_r_r322;
    int32_t cpy_r_r323;
    char cpy_r_r324;
    char cpy_r_r325;
    tuple_T3OOO cpy_r_r326;
    tuple_T3OOO cpy_r_r327;
    char cpy_r_r328;
    PyObject *cpy_r_r329;
    char cpy_r_r330;
    tuple_T3OOO cpy_r_r331;
    PyObject *cpy_r_r332;
    char cpy_r_r333;
    tuple_T3OOO cpy_r_r334;
    char cpy_r_r335;
    PyObject *cpy_r_r336;
    PyObject *cpy_r_r337;
    PyObject *cpy_r_r338;
    PyObject **cpy_r_r340;
    PyObject *cpy_r_r341;
    PyObject *cpy_r_r342;
    char cpy_r_r343;
    PyObject *cpy_r_r344;
    PyObject *cpy_r_r345;
    PyObject *cpy_r_r346;
    PyObject *cpy_r_r347;
    PyObject *cpy_r_r348;
    char cpy_r_r349;
    PyObject *cpy_r_r350;
    char cpy_r_r351;
    PyObject *cpy_r_r352;
    char cpy_r_r353;
    tuple_T3OOO cpy_r_r354;
    char cpy_r_r355;
    PyObject **cpy_r_r356;
    PyObject *cpy_r_r357;
    char cpy_r_r358;
    tuple_T3OOO cpy_r_r359;
    tuple_T3OOO cpy_r_r360;
    tuple_T3OOO cpy_r_r361;
    char cpy_r_r362;
    PyObject *cpy_r_r363;
    PyObject *cpy_r_r364;
    PyObject *cpy_r_r365;
    PyObject *cpy_r_r366;
    char cpy_r_r367;
    char cpy_r_r368;
    PyObject *cpy_r_r369;
    char cpy_r_r370;
    char cpy_r_r371;
    char cpy_r_r372;
    char cpy_r_r373;
    char cpy_r_r374;
    char cpy_r_r375;
    char cpy_r_r376;
    char cpy_r_r377;
    char cpy_r_r378;
    char cpy_r_r379;
    char cpy_r_r380;
    PyObject *cpy_r_r381;
    cpy_r_r0 = NULL;
    cpy_r_r1 = cpy_r_r0;
    CPy_XDECREF(cpy_r_r1);
    cpy_r_r2 = NULL;
    cpy_r_r3 = cpy_r_r2;
    cpy_r_r4 = NULL;
    cpy_r_r5 = cpy_r_r4;
    cpy_r_r6 = NULL;
    cpy_r_r7 = cpy_r_r6;
    cpy_r_r8 = NULL;
    cpy_r_r9 = cpy_r_r8;
    cpy_r_r10 = NULL;
    cpy_r_r11 = cpy_r_r10;
    cpy_r_r12 = NULL;
    cpy_r_r13 = cpy_r_r12;
    tuple_T3OOO __tmp9 = { NULL, NULL, NULL };
    cpy_r_r14 = __tmp9;
    cpy_r_r15 = cpy_r_r14;
    cpy_r_r16 = NULL;
    cpy_r_r17 = cpy_r_r16;
    cpy_r_r18 = NULL;
    cpy_r_r19 = cpy_r_r18;
    tuple_T3OOO __tmp10 = { NULL, NULL, NULL };
    cpy_r_r20 = __tmp10;
    cpy_r_r21 = cpy_r_r20;
    cpy_r_r22 = ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_next_label__;
    goto CPyL359;
CPyL1: ;
    cpy_r_r23 = (PyObject *)&_Py_NoneStruct;
    cpy_r_r24 = cpy_r_type != cpy_r_r23;
    if (!cpy_r_r24) goto CPyL4;
    CPyErr_SetObjectAndTraceback(cpy_r_type, cpy_r_value, cpy_r_traceback);
    if (unlikely(!0)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL370;
    }
    CPy_Unreachable();
CPyL4: ;
    cpy_r_r25 = ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__self;
    if (unlikely(cpy_r_r25 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "fetchone", "fetchone_AsyncCursor_gen", "self", 126, CPyStatic_brownie___globals);
        goto CPyL370;
    }
    CPy_INCREF_NO_IMM(cpy_r_r25);
CPyL5: ;
    cpy_r_r26 = ((y____db___brownie___AsyncCursorObject *)cpy_r_r25)->__db;
    cpy_r_r27 = (PyObject *)&_Py_NoneStruct;
    cpy_r_r28 = cpy_r_r26 == cpy_r_r27;
    CPy_DECREF_NO_IMM(cpy_r_r25);
    if (!cpy_r_r28) goto CPyL35;
    cpy_r_r29 = ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__self;
    if (unlikely(cpy_r_r29 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "fetchone", "fetchone_AsyncCursor_gen", "self", 127, CPyStatic_brownie___globals);
        goto CPyL370;
    }
    CPy_INCREF_NO_IMM(cpy_r_r29);
CPyL7: ;
    cpy_r_r30 = CPyDef_brownie___AsyncCursor___connect(cpy_r_r29);
    CPy_DECREF_NO_IMM(cpy_r_r29);
    if (unlikely(cpy_r_r30 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL370;
    }
    if (((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__13 != NULL) {
        CPy_DECREF_NO_IMM(((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__13);
    }
    ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__13 = cpy_r_r30;
    cpy_r_r31 = 1;
    if (unlikely(!cpy_r_r31)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", -1, CPyStatic_brownie___globals);
        goto CPyL370;
    }
    cpy_r_r32 = ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__13;
    if (unlikely(cpy_r_r32 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "fetchone", "fetchone_AsyncCursor_gen", "__mypyc_temp__13", -1, CPyStatic_brownie___globals);
        goto CPyL370;
    }
    CPy_INCREF_NO_IMM(cpy_r_r32);
CPyL10: ;
    cpy_r_r33 = (PyObject *)&_Py_NoneStruct;
    cpy_r_r34 = NULL;
    cpy_r_r1 = cpy_r_r34;
    cpy_r_r35 = (PyObject **)&cpy_r_r1;
    cpy_r_r36 = CPyDef_brownie___connect_AsyncCursor_gen_____mypyc_generator_helper__(cpy_r_r32, cpy_r_r33, cpy_r_r33, cpy_r_r33, cpy_r_r33, cpy_r_r35);
    CPy_DECREF_NO_IMM(cpy_r_r32);
    if (cpy_r_r36 != NULL) goto CPyL371;
    cpy_r_r37 = cpy_r_r1 != 0;
    if (unlikely(!cpy_r_r37)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", -1, CPyStatic_brownie___globals);
        goto CPyL372;
    }
    cpy_r_r38 = cpy_r_r1;
    CPy_DECREF(cpy_r_r38);
    cpy_r_r39 = NULL;
    if (((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__13 != NULL) {
        CPy_DECREF_NO_IMM(((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__13);
    }
    ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__13 = cpy_r_r39;
    cpy_r_r40 = 1;
    if (unlikely(!cpy_r_r40)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL370;
    } else
        goto CPyL35;
CPyL13: ;
    cpy_r_r41 = cpy_r_r36;
CPyL14: ;
    ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_next_label__ = 1;
    return cpy_r_r41;
CPyL15: ;
    cpy_r_r43 = (PyObject *)&_Py_NoneStruct;
    cpy_r_r44 = cpy_r_type != cpy_r_r43;
    if (!cpy_r_r44) goto CPyL373;
    CPyErr_SetObjectAndTraceback(cpy_r_type, cpy_r_value, cpy_r_traceback);
    if (unlikely(!0)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL19;
    } else
        goto CPyL374;
CPyL17: ;
    CPy_Unreachable();
CPyL18: ;
    CPy_INCREF(cpy_r_arg);
    goto CPyL30;
CPyL19: ;
    cpy_r_r45 = CPy_CatchError();
    if (((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__14.f0 != NULL) {
        CPy_DECREF(((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__14.f0);
        CPy_DECREF(((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__14.f1);
        CPy_DECREF(((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__14.f2);
    }
    ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__14 = cpy_r_r45;
    cpy_r_r46 = 1;
    if (unlikely(!cpy_r_r46)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", -1, CPyStatic_brownie___globals);
        goto CPyL375;
    }
    cpy_r_r47 = (PyObject **)&cpy_r_r3;
    cpy_r_r48 = ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__13;
    if (unlikely(cpy_r_r48 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "fetchone", "fetchone_AsyncCursor_gen", "__mypyc_temp__13", -1, CPyStatic_brownie___globals);
        goto CPyL375;
    }
    CPy_INCREF_NO_IMM(cpy_r_r48);
CPyL21: ;
    cpy_r_r49 = CPy_YieldFromErrorHandle(cpy_r_r48, cpy_r_r47);
    CPy_DecRef(cpy_r_r48);
    if (unlikely(cpy_r_r49 == 2)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL375;
    }
    if (cpy_r_r49) goto CPyL25;
    cpy_r_r41 = cpy_r_r3;
    cpy_r_r50 = ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__14;
    if (unlikely(cpy_r_r50.f0 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "fetchone", "fetchone_AsyncCursor_gen", "__mypyc_temp__14", -1, CPyStatic_brownie___globals);
        goto CPyL376;
    }
    CPy_INCREF(cpy_r_r50.f0);
    CPy_INCREF(cpy_r_r50.f1);
    CPy_INCREF(cpy_r_r50.f2);
CPyL24: ;
    CPy_RestoreExcInfo(cpy_r_r50);
    CPy_DecRef(cpy_r_r50.f0);
    CPy_DecRef(cpy_r_r50.f1);
    CPy_DecRef(cpy_r_r50.f2);
    goto CPyL14;
CPyL25: ;
    cpy_r_r38 = cpy_r_r3;
    CPy_DecRef(cpy_r_r38);
    cpy_r_r51 = ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__14;
    if (unlikely(cpy_r_r51.f0 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "fetchone", "fetchone_AsyncCursor_gen", "__mypyc_temp__14", -1, CPyStatic_brownie___globals);
        goto CPyL27;
    }
    CPy_INCREF(cpy_r_r51.f0);
    CPy_INCREF(cpy_r_r51.f1);
    CPy_INCREF(cpy_r_r51.f2);
CPyL26: ;
    CPy_RestoreExcInfo(cpy_r_r51);
    CPy_DecRef(cpy_r_r51.f0);
    CPy_DecRef(cpy_r_r51.f1);
    CPy_DecRef(cpy_r_r51.f2);
    goto CPyL35;
CPyL27: ;
    cpy_r_r52 = ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__14;
    if (unlikely(cpy_r_r52.f0 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "fetchone", "fetchone_AsyncCursor_gen", "__mypyc_temp__14", -1, CPyStatic_brownie___globals);
        goto CPyL370;
    }
    CPy_INCREF(cpy_r_r52.f0);
    CPy_INCREF(cpy_r_r52.f1);
    CPy_INCREF(cpy_r_r52.f2);
CPyL28: ;
    CPy_RestoreExcInfo(cpy_r_r52);
    CPy_DecRef(cpy_r_r52.f0);
    CPy_DecRef(cpy_r_r52.f1);
    CPy_DecRef(cpy_r_r52.f2);
    cpy_r_r53 = CPy_KeepPropagating();
    if (!cpy_r_r53) goto CPyL370;
    CPy_Unreachable();
CPyL30: ;
    cpy_r_r54 = ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__13;
    if (unlikely(cpy_r_r54 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "fetchone", "fetchone_AsyncCursor_gen", "__mypyc_temp__13", -1, CPyStatic_brownie___globals);
        goto CPyL377;
    }
    CPy_INCREF_NO_IMM(cpy_r_r54);
CPyL31: ;
    cpy_r_r55 = CPyIter_Send(cpy_r_r54, cpy_r_arg);
    CPy_DECREF_NO_IMM(cpy_r_r54);
    CPy_DECREF(cpy_r_arg);
    if (cpy_r_r55 == NULL) goto CPyL33;
    cpy_r_r41 = cpy_r_r55;
    goto CPyL14;
CPyL33: ;
    cpy_r_r56 = CPy_FetchStopIterationValue();
    if (unlikely(cpy_r_r56 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL370;
    }
    cpy_r_r38 = cpy_r_r56;
    CPy_DECREF(cpy_r_r38);
CPyL35: ;
    cpy_r_r57 = CPyStatic_brownie___sqlite_lock;
    if (likely(cpy_r_r57 != NULL)) goto CPyL38;
    PyErr_SetString(PyExc_NameError, "value for final name \"sqlite_lock\" was not set");
    cpy_r_r58 = 0;
    if (unlikely(!cpy_r_r58)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL370;
    }
    CPy_Unreachable();
CPyL38: ;
    cpy_r_r59 = CPy_TYPE(cpy_r_r57);
    cpy_r_r60 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* '__aexit__' */
    cpy_r_r61 = CPyObject_GetAttr(cpy_r_r59, cpy_r_r60);
    if (unlikely(cpy_r_r61 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL378;
    }
    if (((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__15 != NULL) {
        CPy_DECREF(((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__15);
    }
    ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__15 = cpy_r_r61;
    cpy_r_r62 = 1;
    if (unlikely(!cpy_r_r62)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", -1, CPyStatic_brownie___globals);
        goto CPyL378;
    }
    cpy_r_r63 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* '__aenter__' */
    cpy_r_r64 = CPyObject_GetAttr(cpy_r_r59, cpy_r_r63);
    CPy_DECREF(cpy_r_r59);
    if (unlikely(cpy_r_r64 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL370;
    }
    PyObject *cpy_r_r65[1] = {cpy_r_r57};
    cpy_r_r66 = (PyObject **)&cpy_r_r65;
    cpy_r_r67 = PyObject_Vectorcall(cpy_r_r64, cpy_r_r66, 1, 0);
    CPy_DECREF(cpy_r_r64);
    if (unlikely(cpy_r_r67 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL370;
    }
    CPy_INCREF(cpy_r_r57);
    if (((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__16 != NULL) {
        CPy_DECREF(((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__16);
    }
    ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__16 = cpy_r_r57;
    cpy_r_r68 = 1;
    if (unlikely(!cpy_r_r68)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", -1, CPyStatic_brownie___globals);
        goto CPyL379;
    }
    ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__17 = 1;
    cpy_r_r69 = 1;
    if (unlikely(!cpy_r_r69)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", -1, CPyStatic_brownie___globals);
        goto CPyL379;
    }
    cpy_r_r70 = CPy_GetCoro(cpy_r_r67);
    CPy_DECREF(cpy_r_r67);
    if (unlikely(cpy_r_r70 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL370;
    }
    if (((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__18 != NULL) {
        CPy_DECREF(((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__18);
    }
    ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__18 = cpy_r_r70;
    cpy_r_r71 = 1;
    if (unlikely(!cpy_r_r71)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", -1, CPyStatic_brownie___globals);
        goto CPyL370;
    }
    cpy_r_r72 = ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__18;
    if (unlikely(cpy_r_r72 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "fetchone", "fetchone_AsyncCursor_gen", "__mypyc_temp__18", -1, CPyStatic_brownie___globals);
        goto CPyL370;
    }
    CPy_INCREF(cpy_r_r72);
CPyL47: ;
    cpy_r_r73 = CPyIter_Next(cpy_r_r72);
    CPy_DECREF(cpy_r_r72);
    if (cpy_r_r73 != NULL) goto CPyL50;
    cpy_r_r74 = CPy_FetchStopIterationValue();
    if (unlikely(cpy_r_r74 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL370;
    }
    cpy_r_r75 = cpy_r_r74;
    CPy_DECREF(cpy_r_r75);
    cpy_r_r76 = NULL;
    if (((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__18 != NULL) {
        CPy_DECREF(((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__18);
    }
    ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__18 = cpy_r_r76;
    cpy_r_r77 = 1;
    if (unlikely(!cpy_r_r77)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL370;
    } else
        goto CPyL72;
CPyL50: ;
    cpy_r_r78 = cpy_r_r73;
CPyL51: ;
    ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_next_label__ = 2;
    return cpy_r_r78;
CPyL52: ;
    cpy_r_r80 = (PyObject *)&_Py_NoneStruct;
    cpy_r_r81 = cpy_r_type != cpy_r_r80;
    if (!cpy_r_r81) goto CPyL380;
    CPyErr_SetObjectAndTraceback(cpy_r_type, cpy_r_value, cpy_r_traceback);
    if (unlikely(!0)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL56;
    } else
        goto CPyL381;
CPyL54: ;
    CPy_Unreachable();
CPyL55: ;
    CPy_INCREF(cpy_r_arg);
    goto CPyL67;
CPyL56: ;
    cpy_r_r82 = CPy_CatchError();
    if (((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__19.f0 != NULL) {
        CPy_DECREF(((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__19.f0);
        CPy_DECREF(((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__19.f1);
        CPy_DECREF(((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__19.f2);
    }
    ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__19 = cpy_r_r82;
    cpy_r_r83 = 1;
    if (unlikely(!cpy_r_r83)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", -1, CPyStatic_brownie___globals);
        goto CPyL382;
    }
    cpy_r_r84 = (PyObject **)&cpy_r_r5;
    cpy_r_r85 = ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__18;
    if (unlikely(cpy_r_r85 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "fetchone", "fetchone_AsyncCursor_gen", "__mypyc_temp__18", -1, CPyStatic_brownie___globals);
        goto CPyL382;
    }
    CPy_INCREF(cpy_r_r85);
CPyL58: ;
    cpy_r_r86 = CPy_YieldFromErrorHandle(cpy_r_r85, cpy_r_r84);
    CPy_DecRef(cpy_r_r85);
    if (unlikely(cpy_r_r86 == 2)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL382;
    }
    if (cpy_r_r86) goto CPyL62;
    cpy_r_r78 = cpy_r_r5;
    cpy_r_r87 = ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__19;
    if (unlikely(cpy_r_r87.f0 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "fetchone", "fetchone_AsyncCursor_gen", "__mypyc_temp__19", -1, CPyStatic_brownie___globals);
        goto CPyL383;
    }
    CPy_INCREF(cpy_r_r87.f0);
    CPy_INCREF(cpy_r_r87.f1);
    CPy_INCREF(cpy_r_r87.f2);
CPyL61: ;
    CPy_RestoreExcInfo(cpy_r_r87);
    CPy_DecRef(cpy_r_r87.f0);
    CPy_DecRef(cpy_r_r87.f1);
    CPy_DecRef(cpy_r_r87.f2);
    goto CPyL51;
CPyL62: ;
    cpy_r_r75 = cpy_r_r5;
    CPy_DecRef(cpy_r_r75);
    cpy_r_r88 = ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__19;
    if (unlikely(cpy_r_r88.f0 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "fetchone", "fetchone_AsyncCursor_gen", "__mypyc_temp__19", -1, CPyStatic_brownie___globals);
        goto CPyL64;
    }
    CPy_INCREF(cpy_r_r88.f0);
    CPy_INCREF(cpy_r_r88.f1);
    CPy_INCREF(cpy_r_r88.f2);
CPyL63: ;
    CPy_RestoreExcInfo(cpy_r_r88);
    CPy_DecRef(cpy_r_r88.f0);
    CPy_DecRef(cpy_r_r88.f1);
    CPy_DecRef(cpy_r_r88.f2);
    goto CPyL72;
CPyL64: ;
    cpy_r_r89 = ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__19;
    if (unlikely(cpy_r_r89.f0 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "fetchone", "fetchone_AsyncCursor_gen", "__mypyc_temp__19", -1, CPyStatic_brownie___globals);
        goto CPyL370;
    }
    CPy_INCREF(cpy_r_r89.f0);
    CPy_INCREF(cpy_r_r89.f1);
    CPy_INCREF(cpy_r_r89.f2);
CPyL65: ;
    CPy_RestoreExcInfo(cpy_r_r89);
    CPy_DecRef(cpy_r_r89.f0);
    CPy_DecRef(cpy_r_r89.f1);
    CPy_DecRef(cpy_r_r89.f2);
    cpy_r_r90 = CPy_KeepPropagating();
    if (!cpy_r_r90) goto CPyL370;
    CPy_Unreachable();
CPyL67: ;
    cpy_r_r91 = ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__18;
    if (unlikely(cpy_r_r91 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "fetchone", "fetchone_AsyncCursor_gen", "__mypyc_temp__18", -1, CPyStatic_brownie___globals);
        goto CPyL384;
    }
    CPy_INCREF(cpy_r_r91);
CPyL68: ;
    cpy_r_r92 = CPyIter_Send(cpy_r_r91, cpy_r_arg);
    CPy_DECREF(cpy_r_r91);
    CPy_DECREF(cpy_r_arg);
    if (cpy_r_r92 == NULL) goto CPyL70;
    cpy_r_r78 = cpy_r_r92;
    goto CPyL51;
CPyL70: ;
    cpy_r_r93 = CPy_FetchStopIterationValue();
    if (unlikely(cpy_r_r93 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL370;
    }
    cpy_r_r75 = cpy_r_r93;
    CPy_DECREF(cpy_r_r75);
CPyL72: ;
    cpy_r_r94 = ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__self;
    if (unlikely(cpy_r_r94 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "fetchone", "fetchone_AsyncCursor_gen", "self", 129, CPyStatic_brownie___globals);
        goto CPyL262;
    }
    CPy_INCREF_NO_IMM(cpy_r_r94);
CPyL73: ;
    cpy_r_r95 = ((y____db___brownie___AsyncCursorObject *)cpy_r_r94)->__execute;
    CPy_INCREF(cpy_r_r95);
    CPy_DECREF_NO_IMM(cpy_r_r94);
    if (((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__execute != NULL) {
        CPy_DECREF(((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__execute);
    }
    ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__execute = cpy_r_r95;
    cpy_r_r96 = 1;
    if (unlikely(!cpy_r_r96)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL262;
    }
    cpy_r_r97 = ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__cmd;
    if (unlikely(cpy_r_r97 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "fetchone", "fetchone_AsyncCursor_gen", "cmd", 130, CPyStatic_brownie___globals);
        goto CPyL262;
    }
    CPy_INCREF(cpy_r_r97);
CPyL75: ;
    cpy_r_r98 = ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__args;
    if (unlikely(cpy_r_r98 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "fetchone", "fetchone_AsyncCursor_gen", "args", 130, CPyStatic_brownie___globals);
        goto CPyL385;
    }
    CPy_INCREF(cpy_r_r98);
CPyL76: ;
    cpy_r_r99 = ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__execute;
    if (unlikely(cpy_r_r99 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "fetchone", "fetchone_AsyncCursor_gen", "execute", 130, CPyStatic_brownie___globals);
        goto CPyL386;
    }
    CPy_INCREF(cpy_r_r99);
CPyL77: ;
    PyObject *cpy_r_r100[2] = {cpy_r_r97, cpy_r_r98};
    cpy_r_r101 = (PyObject **)&cpy_r_r100;
    cpy_r_r102 = PyObject_Vectorcall(cpy_r_r99, cpy_r_r101, 2, 0);
    CPy_DECREF(cpy_r_r99);
    if (unlikely(cpy_r_r102 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL386;
    }
    CPy_DECREF(cpy_r_r97);
    CPy_DECREF(cpy_r_r98);
    cpy_r_r103 = CPy_TYPE(cpy_r_r102);
    cpy_r_r104 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* '__aexit__' */
    cpy_r_r105 = CPyObject_GetAttr(cpy_r_r103, cpy_r_r104);
    if (unlikely(cpy_r_r105 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL387;
    }
    if (((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__20 != NULL) {
        CPy_DECREF(((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__20);
    }
    ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__20 = cpy_r_r105;
    cpy_r_r106 = 1;
    if (unlikely(!cpy_r_r106)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", -1, CPyStatic_brownie___globals);
        goto CPyL387;
    }
    cpy_r_r107 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* '__aenter__' */
    cpy_r_r108 = CPyObject_GetAttr(cpy_r_r103, cpy_r_r107);
    CPy_DECREF(cpy_r_r103);
    if (unlikely(cpy_r_r108 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL388;
    }
    PyObject *cpy_r_r109[1] = {cpy_r_r102};
    cpy_r_r110 = (PyObject **)&cpy_r_r109;
    cpy_r_r111 = PyObject_Vectorcall(cpy_r_r108, cpy_r_r110, 1, 0);
    CPy_DECREF(cpy_r_r108);
    if (unlikely(cpy_r_r111 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL388;
    }
    if (((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__21 != NULL) {
        CPy_DECREF(((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__21);
    }
    ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__21 = cpy_r_r102;
    cpy_r_r112 = 1;
    if (unlikely(!cpy_r_r112)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", -1, CPyStatic_brownie___globals);
        goto CPyL389;
    }
    ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__22 = 1;
    cpy_r_r113 = 1;
    if (unlikely(!cpy_r_r113)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", -1, CPyStatic_brownie___globals);
        goto CPyL389;
    }
    cpy_r_r114 = CPy_GetCoro(cpy_r_r111);
    CPy_DECREF(cpy_r_r111);
    if (unlikely(cpy_r_r114 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL262;
    }
    if (((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__23 != NULL) {
        CPy_DECREF(((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__23);
    }
    ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__23 = cpy_r_r114;
    cpy_r_r115 = 1;
    if (unlikely(!cpy_r_r115)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", -1, CPyStatic_brownie___globals);
        goto CPyL262;
    }
    cpy_r_r116 = ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__23;
    if (unlikely(cpy_r_r116 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "fetchone", "fetchone_AsyncCursor_gen", "__mypyc_temp__23", -1, CPyStatic_brownie___globals);
        goto CPyL262;
    }
    CPy_INCREF(cpy_r_r116);
CPyL87: ;
    cpy_r_r117 = CPyIter_Next(cpy_r_r116);
    CPy_DECREF(cpy_r_r116);
    if (cpy_r_r117 != NULL) goto CPyL90;
    cpy_r_r118 = CPy_FetchStopIterationValue();
    if (unlikely(cpy_r_r118 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL262;
    }
    cpy_r_r119 = cpy_r_r118;
    cpy_r_r120 = NULL;
    if (((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__23 != NULL) {
        CPy_DECREF(((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__23);
    }
    ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__23 = cpy_r_r120;
    cpy_r_r121 = 1;
    if (unlikely(!cpy_r_r121)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL390;
    } else
        goto CPyL112;
CPyL90: ;
    cpy_r_r122 = cpy_r_r117;
CPyL91: ;
    ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_next_label__ = 3;
    return cpy_r_r122;
CPyL92: ;
    cpy_r_r124 = (PyObject *)&_Py_NoneStruct;
    cpy_r_r125 = cpy_r_type != cpy_r_r124;
    if (!cpy_r_r125) goto CPyL391;
    CPyErr_SetObjectAndTraceback(cpy_r_type, cpy_r_value, cpy_r_traceback);
    if (unlikely(!0)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL96;
    } else
        goto CPyL392;
CPyL94: ;
    CPy_Unreachable();
CPyL95: ;
    CPy_INCREF(cpy_r_arg);
    goto CPyL107;
CPyL96: ;
    cpy_r_r126 = CPy_CatchError();
    if (((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__24.f0 != NULL) {
        CPy_DECREF(((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__24.f0);
        CPy_DECREF(((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__24.f1);
        CPy_DECREF(((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__24.f2);
    }
    ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__24 = cpy_r_r126;
    cpy_r_r127 = 1;
    if (unlikely(!cpy_r_r127)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", -1, CPyStatic_brownie___globals);
        goto CPyL393;
    }
    cpy_r_r128 = (PyObject **)&cpy_r_r7;
    cpy_r_r129 = ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__23;
    if (unlikely(cpy_r_r129 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "fetchone", "fetchone_AsyncCursor_gen", "__mypyc_temp__23", -1, CPyStatic_brownie___globals);
        goto CPyL393;
    }
    CPy_INCREF(cpy_r_r129);
CPyL98: ;
    cpy_r_r130 = CPy_YieldFromErrorHandle(cpy_r_r129, cpy_r_r128);
    CPy_DecRef(cpy_r_r129);
    if (unlikely(cpy_r_r130 == 2)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL393;
    }
    if (cpy_r_r130) goto CPyL102;
    cpy_r_r122 = cpy_r_r7;
    cpy_r_r131 = ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__24;
    if (unlikely(cpy_r_r131.f0 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "fetchone", "fetchone_AsyncCursor_gen", "__mypyc_temp__24", -1, CPyStatic_brownie___globals);
        goto CPyL394;
    }
    CPy_INCREF(cpy_r_r131.f0);
    CPy_INCREF(cpy_r_r131.f1);
    CPy_INCREF(cpy_r_r131.f2);
CPyL101: ;
    CPy_RestoreExcInfo(cpy_r_r131);
    CPy_DecRef(cpy_r_r131.f0);
    CPy_DecRef(cpy_r_r131.f1);
    CPy_DecRef(cpy_r_r131.f2);
    goto CPyL91;
CPyL102: ;
    cpy_r_r119 = cpy_r_r7;
    cpy_r_r132 = ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__24;
    if (unlikely(cpy_r_r132.f0 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "fetchone", "fetchone_AsyncCursor_gen", "__mypyc_temp__24", -1, CPyStatic_brownie___globals);
        goto CPyL395;
    }
    CPy_INCREF(cpy_r_r132.f0);
    CPy_INCREF(cpy_r_r132.f1);
    CPy_INCREF(cpy_r_r132.f2);
CPyL103: ;
    CPy_RestoreExcInfo(cpy_r_r132);
    CPy_DecRef(cpy_r_r132.f0);
    CPy_DecRef(cpy_r_r132.f1);
    CPy_DecRef(cpy_r_r132.f2);
    goto CPyL112;
CPyL104: ;
    cpy_r_r133 = ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__24;
    if (unlikely(cpy_r_r133.f0 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "fetchone", "fetchone_AsyncCursor_gen", "__mypyc_temp__24", -1, CPyStatic_brownie___globals);
        goto CPyL262;
    }
    CPy_INCREF(cpy_r_r133.f0);
    CPy_INCREF(cpy_r_r133.f1);
    CPy_INCREF(cpy_r_r133.f2);
CPyL105: ;
    CPy_RestoreExcInfo(cpy_r_r133);
    CPy_DecRef(cpy_r_r133.f0);
    CPy_DecRef(cpy_r_r133.f1);
    CPy_DecRef(cpy_r_r133.f2);
    cpy_r_r134 = CPy_KeepPropagating();
    if (!cpy_r_r134) goto CPyL262;
    CPy_Unreachable();
CPyL107: ;
    cpy_r_r135 = ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__23;
    if (unlikely(cpy_r_r135 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "fetchone", "fetchone_AsyncCursor_gen", "__mypyc_temp__23", -1, CPyStatic_brownie___globals);
        goto CPyL396;
    }
    CPy_INCREF(cpy_r_r135);
CPyL108: ;
    cpy_r_r136 = CPyIter_Send(cpy_r_r135, cpy_r_arg);
    CPy_DECREF(cpy_r_r135);
    CPy_DECREF(cpy_r_arg);
    if (cpy_r_r136 == NULL) goto CPyL110;
    cpy_r_r122 = cpy_r_r136;
    goto CPyL91;
CPyL110: ;
    cpy_r_r137 = CPy_FetchStopIterationValue();
    if (unlikely(cpy_r_r137 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL262;
    }
    cpy_r_r119 = cpy_r_r137;
CPyL112: ;
    if (((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__cursor != NULL) {
        CPy_DECREF(((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__cursor);
    }
    ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__cursor = cpy_r_r119;
    cpy_r_r138 = 1;
    if (unlikely(!cpy_r_r138)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL174;
    }
    cpy_r_r139 = ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__cursor;
    if (unlikely(cpy_r_r139 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "fetchone", "fetchone_AsyncCursor_gen", "cursor", 131, CPyStatic_brownie___globals);
        goto CPyL174;
    }
    CPy_INCREF(cpy_r_r139);
CPyL114: ;
    cpy_r_r140 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'fetchone' */
    PyObject *cpy_r_r141[1] = {cpy_r_r139};
    cpy_r_r142 = (PyObject **)&cpy_r_r141;
    cpy_r_r143 = PyObject_VectorcallMethod(cpy_r_r140, cpy_r_r142, 9223372036854775809ULL, 0);
    if (unlikely(cpy_r_r143 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL397;
    }
    CPy_DECREF(cpy_r_r139);
    cpy_r_r144 = CPy_GetCoro(cpy_r_r143);
    CPy_DECREF(cpy_r_r143);
    if (unlikely(cpy_r_r144 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL174;
    }
    if (((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__25 != NULL) {
        CPy_DECREF(((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__25);
    }
    ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__25 = cpy_r_r144;
    cpy_r_r145 = 1;
    if (unlikely(!cpy_r_r145)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", -1, CPyStatic_brownie___globals);
        goto CPyL174;
    }
    cpy_r_r146 = ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__25;
    if (unlikely(cpy_r_r146 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "fetchone", "fetchone_AsyncCursor_gen", "__mypyc_temp__25", -1, CPyStatic_brownie___globals);
        goto CPyL174;
    }
    CPy_INCREF(cpy_r_r146);
CPyL118: ;
    cpy_r_r147 = CPyIter_Next(cpy_r_r146);
    CPy_DECREF(cpy_r_r146);
    if (cpy_r_r147 != NULL) goto CPyL121;
    cpy_r_r148 = CPy_FetchStopIterationValue();
    if (unlikely(cpy_r_r148 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL174;
    }
    cpy_r_r149 = cpy_r_r148;
    cpy_r_r150 = NULL;
    if (((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__25 != NULL) {
        CPy_DECREF(((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__25);
    }
    ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__25 = cpy_r_r150;
    cpy_r_r151 = 1;
    if (unlikely(!cpy_r_r151)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL398;
    } else
        goto CPyL143;
CPyL121: ;
    cpy_r_r152 = cpy_r_r147;
CPyL122: ;
    ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_next_label__ = 4;
    return cpy_r_r152;
CPyL123: ;
    cpy_r_r154 = (PyObject *)&_Py_NoneStruct;
    cpy_r_r155 = cpy_r_type != cpy_r_r154;
    if (!cpy_r_r155) goto CPyL399;
    CPyErr_SetObjectAndTraceback(cpy_r_type, cpy_r_value, cpy_r_traceback);
    if (unlikely(!0)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL127;
    } else
        goto CPyL400;
CPyL125: ;
    CPy_Unreachable();
CPyL126: ;
    CPy_INCREF(cpy_r_arg);
    goto CPyL138;
CPyL127: ;
    cpy_r_r156 = CPy_CatchError();
    if (((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__26.f0 != NULL) {
        CPy_DECREF(((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__26.f0);
        CPy_DECREF(((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__26.f1);
        CPy_DECREF(((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__26.f2);
    }
    ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__26 = cpy_r_r156;
    cpy_r_r157 = 1;
    if (unlikely(!cpy_r_r157)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", -1, CPyStatic_brownie___globals);
        goto CPyL401;
    }
    cpy_r_r158 = (PyObject **)&cpy_r_r9;
    cpy_r_r159 = ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__25;
    if (unlikely(cpy_r_r159 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "fetchone", "fetchone_AsyncCursor_gen", "__mypyc_temp__25", -1, CPyStatic_brownie___globals);
        goto CPyL401;
    }
    CPy_INCREF(cpy_r_r159);
CPyL129: ;
    cpy_r_r160 = CPy_YieldFromErrorHandle(cpy_r_r159, cpy_r_r158);
    CPy_DecRef(cpy_r_r159);
    if (unlikely(cpy_r_r160 == 2)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL401;
    }
    if (cpy_r_r160) goto CPyL133;
    cpy_r_r152 = cpy_r_r9;
    cpy_r_r161 = ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__26;
    if (unlikely(cpy_r_r161.f0 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "fetchone", "fetchone_AsyncCursor_gen", "__mypyc_temp__26", -1, CPyStatic_brownie___globals);
        goto CPyL402;
    }
    CPy_INCREF(cpy_r_r161.f0);
    CPy_INCREF(cpy_r_r161.f1);
    CPy_INCREF(cpy_r_r161.f2);
CPyL132: ;
    CPy_RestoreExcInfo(cpy_r_r161);
    CPy_DecRef(cpy_r_r161.f0);
    CPy_DecRef(cpy_r_r161.f1);
    CPy_DecRef(cpy_r_r161.f2);
    goto CPyL122;
CPyL133: ;
    cpy_r_r149 = cpy_r_r9;
    cpy_r_r162 = ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__26;
    if (unlikely(cpy_r_r162.f0 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "fetchone", "fetchone_AsyncCursor_gen", "__mypyc_temp__26", -1, CPyStatic_brownie___globals);
        goto CPyL403;
    }
    CPy_INCREF(cpy_r_r162.f0);
    CPy_INCREF(cpy_r_r162.f1);
    CPy_INCREF(cpy_r_r162.f2);
CPyL134: ;
    CPy_RestoreExcInfo(cpy_r_r162);
    CPy_DecRef(cpy_r_r162.f0);
    CPy_DecRef(cpy_r_r162.f1);
    CPy_DecRef(cpy_r_r162.f2);
    goto CPyL143;
CPyL135: ;
    cpy_r_r163 = ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__26;
    if (unlikely(cpy_r_r163.f0 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "fetchone", "fetchone_AsyncCursor_gen", "__mypyc_temp__26", -1, CPyStatic_brownie___globals);
        goto CPyL174;
    }
    CPy_INCREF(cpy_r_r163.f0);
    CPy_INCREF(cpy_r_r163.f1);
    CPy_INCREF(cpy_r_r163.f2);
CPyL136: ;
    CPy_RestoreExcInfo(cpy_r_r163);
    CPy_DecRef(cpy_r_r163.f0);
    CPy_DecRef(cpy_r_r163.f1);
    CPy_DecRef(cpy_r_r163.f2);
    cpy_r_r164 = CPy_KeepPropagating();
    if (!cpy_r_r164) goto CPyL174;
    CPy_Unreachable();
CPyL138: ;
    cpy_r_r165 = ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__25;
    if (unlikely(cpy_r_r165 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "fetchone", "fetchone_AsyncCursor_gen", "__mypyc_temp__25", -1, CPyStatic_brownie___globals);
        goto CPyL404;
    }
    CPy_INCREF(cpy_r_r165);
CPyL139: ;
    cpy_r_r166 = CPyIter_Send(cpy_r_r165, cpy_r_arg);
    CPy_DECREF(cpy_r_r165);
    CPy_DECREF(cpy_r_arg);
    if (cpy_r_r166 == NULL) goto CPyL141;
    cpy_r_r152 = cpy_r_r166;
    goto CPyL122;
CPyL141: ;
    cpy_r_r167 = CPy_FetchStopIterationValue();
    if (unlikely(cpy_r_r167 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL174;
    }
    cpy_r_r149 = cpy_r_r167;
CPyL143: ;
    if (((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__row != NULL) {
        CPy_DECREF(((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__row);
    }
    ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__row = cpy_r_r149;
    cpy_r_r168 = 1;
    if (unlikely(!cpy_r_r168)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL174;
    }
    cpy_r_r169 = ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__row;
    if (unlikely(cpy_r_r169 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "fetchone", "fetchone_AsyncCursor_gen", "row", 132, CPyStatic_brownie___globals);
        goto CPyL174;
    }
    CPy_INCREF(cpy_r_r169);
CPyL145: ;
    cpy_r_r170 = (PyObject *)&_Py_NoneStruct;
    cpy_r_r171 = cpy_r_r169 == cpy_r_r170;
    CPy_DECREF(cpy_r_r169);
    if (!cpy_r_r171) goto CPyL147;
    cpy_r_r172 = Py_None;
    if (((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__27 != NULL) {
        CPy_DECREF(((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__27);
    }
    ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__27 = cpy_r_r172;
    cpy_r_r173 = 1;
    if (unlikely(!cpy_r_r173)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL174;
    } else
        goto CPyL217;
CPyL147: ;
    cpy_r_r174 = PyList_New(0);
    if (unlikely(cpy_r_r174 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL174;
    }
    if (((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__28 != NULL) {
        CPy_DECREF_NO_IMM(((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__28);
    }
    ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__28 = cpy_r_r174;
    cpy_r_r175 = 1;
    if (unlikely(!cpy_r_r175)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", -1, CPyStatic_brownie___globals);
        goto CPyL174;
    }
    cpy_r_r176 = ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__row;
    if (unlikely(cpy_r_r176 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "fetchone", "fetchone_AsyncCursor_gen", "row", 135, CPyStatic_brownie___globals);
        goto CPyL174;
    }
    CPy_INCREF(cpy_r_r176);
CPyL150: ;
    cpy_r_r177 = PyObject_GetIter(cpy_r_r176);
    if (unlikely(cpy_r_r177 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL405;
    }
    if (((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__29 != NULL) {
        CPy_DECREF(((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__29);
    }
    ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__29 = cpy_r_r176;
    cpy_r_r178 = 1;
    if (unlikely(!cpy_r_r178)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", -1, CPyStatic_brownie___globals);
        goto CPyL406;
    }
    if (((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__30 != NULL) {
        CPy_DECREF(((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__30);
    }
    ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__30 = cpy_r_r177;
    cpy_r_r179 = 1;
    if (unlikely(!cpy_r_r179)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", -1, CPyStatic_brownie___globals);
        goto CPyL174;
    }
CPyL153: ;
    cpy_r_r180 = ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__30;
    if (unlikely(cpy_r_r180 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "fetchone", "fetchone_AsyncCursor_gen", "__mypyc_temp__30", 135, CPyStatic_brownie___globals);
        goto CPyL174;
    }
    CPy_INCREF(cpy_r_r180);
CPyL154: ;
    cpy_r_r181 = PyIter_Next(cpy_r_r180);
    CPy_DECREF(cpy_r_r180);
    if (cpy_r_r181 == NULL) goto CPyL170;
    if (((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__i != NULL) {
        CPy_DECREF(((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__i);
    }
    ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__i = cpy_r_r181;
    cpy_r_r182 = 1;
    if (unlikely(!cpy_r_r182)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL174;
    }
    cpy_r_r183 = ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__i;
    if (unlikely(cpy_r_r183 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "fetchone", "fetchone_AsyncCursor_gen", "i", 135, CPyStatic_brownie___globals);
        goto CPyL174;
    }
    CPy_INCREF(cpy_r_r183);
CPyL157: ;
    cpy_r_r184 = PyObject_Str(cpy_r_r183);
    CPy_DECREF(cpy_r_r183);
    if (unlikely(cpy_r_r184 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL174;
    }
    cpy_r_r185 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* '[' */
    cpy_r_r186 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* '{' */
    CPy_INCREF(cpy_r_r185);
    CPy_INCREF(cpy_r_r186);
    cpy_r_r187.f0 = cpy_r_r185;
    cpy_r_r187.f1 = cpy_r_r186;
    cpy_r_r188 = PyTuple_New(2);
    if (unlikely(cpy_r_r188 == NULL))
        CPyError_OutOfMemory();
    PyObject *__tmp11 = cpy_r_r187.f0;
    PyTuple_SET_ITEM(cpy_r_r188, 0, __tmp11);
    PyObject *__tmp12 = cpy_r_r187.f1;
    PyTuple_SET_ITEM(cpy_r_r188, 1, __tmp12);
    cpy_r_r189 = CPyStr_Startswith(cpy_r_r184, cpy_r_r188);
    CPy_DECREF(cpy_r_r184);
    CPy_DECREF(cpy_r_r188);
    if (unlikely(cpy_r_r189 == 2)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL174;
    }
    if (!cpy_r_r189) goto CPyL166;
    cpy_r_r190 = ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__i;
    if (unlikely(cpy_r_r190 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "fetchone", "fetchone_AsyncCursor_gen", "i", 135, CPyStatic_brownie___globals);
        goto CPyL174;
    }
    CPy_INCREF(cpy_r_r190);
CPyL161: ;
    cpy_r_r191 = CPyStatic_brownie___loads;
    if (unlikely(cpy_r_r191 == NULL)) {
        goto CPyL407;
    } else
        goto CPyL164;
CPyL162: ;
    PyErr_SetString(PyExc_NameError, "value for final name \"loads\" was not set");
    cpy_r_r192 = 0;
    if (unlikely(!cpy_r_r192)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL174;
    }
    CPy_Unreachable();
CPyL164: ;
    PyObject *cpy_r_r193[1] = {cpy_r_r190};
    cpy_r_r194 = (PyObject **)&cpy_r_r193;
    cpy_r_r195 = PyObject_Vectorcall(cpy_r_r191, cpy_r_r194, 1, 0);
    if (unlikely(cpy_r_r195 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL408;
    }
    CPy_DECREF(cpy_r_r190);
    cpy_r_r196 = cpy_r_r195;
    goto CPyL168;
CPyL166: ;
    cpy_r_r197 = ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__i;
    if (unlikely(cpy_r_r197 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "fetchone", "fetchone_AsyncCursor_gen", "i", 135, CPyStatic_brownie___globals);
        goto CPyL174;
    }
    CPy_INCREF(cpy_r_r197);
CPyL167: ;
    cpy_r_r196 = cpy_r_r197;
CPyL168: ;
    cpy_r_r198 = ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__28;
    if (unlikely(cpy_r_r198 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "fetchone", "fetchone_AsyncCursor_gen", "__mypyc_temp__28", -1, CPyStatic_brownie___globals);
        goto CPyL409;
    }
    CPy_INCREF_NO_IMM(cpy_r_r198);
CPyL169: ;
    cpy_r_r199 = PyList_Append(cpy_r_r198, cpy_r_r196);
    CPy_DECREF_NO_IMM(cpy_r_r198);
    CPy_DECREF(cpy_r_r196);
    cpy_r_r200 = cpy_r_r199 >= 0;
    if (unlikely(!cpy_r_r200)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL174;
    } else
        goto CPyL153;
CPyL170: ;
    cpy_r_r201 = CPy_NoErrOccurred();
    if (unlikely(!cpy_r_r201)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL174;
    }
    cpy_r_r202 = ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__28;
    if (unlikely(cpy_r_r202 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "fetchone", "fetchone_AsyncCursor_gen", "__mypyc_temp__28", -1, CPyStatic_brownie___globals);
        goto CPyL174;
    }
    CPy_INCREF_NO_IMM(cpy_r_r202);
CPyL172: ;
    cpy_r_r203 = PyList_AsTuple(cpy_r_r202);
    CPy_DECREF_NO_IMM(cpy_r_r202);
    if (unlikely(cpy_r_r203 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL174;
    }
    if (((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__27 != NULL) {
        CPy_DECREF(((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__27);
    }
    ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__27 = cpy_r_r203;
    cpy_r_r204 = 1;
    if (unlikely(!cpy_r_r204)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
    } else
        goto CPyL217;
CPyL174: ;
    cpy_r_r205 = CPy_CatchError();
    if (((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__31.f0 != NULL) {
        CPy_DECREF(((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__31.f0);
        CPy_DECREF(((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__31.f1);
        CPy_DECREF(((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__31.f2);
    }
    ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__31 = cpy_r_r205;
    cpy_r_r206 = 1;
    if (unlikely(!cpy_r_r206)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", -1, CPyStatic_brownie___globals);
        goto CPyL213;
    }
    ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__22 = 0;
    cpy_r_r207 = 1;
    if (unlikely(!cpy_r_r207)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL213;
    }
    cpy_r_r208 = CPy_GetExcInfo();
    cpy_r_r209 = cpy_r_r208.f0;
    CPy_INCREF(cpy_r_r209);
    cpy_r_r210 = cpy_r_r208.f1;
    CPy_INCREF(cpy_r_r210);
    cpy_r_r211 = cpy_r_r208.f2;
    CPy_INCREF(cpy_r_r211);
    CPy_DecRef(cpy_r_r208.f0);
    CPy_DecRef(cpy_r_r208.f1);
    CPy_DecRef(cpy_r_r208.f2);
    cpy_r_r212 = ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__20;
    if (unlikely(cpy_r_r212 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "fetchone", "fetchone_AsyncCursor_gen", "__mypyc_temp__20", -1, CPyStatic_brownie___globals);
        goto CPyL410;
    }
    CPy_INCREF(cpy_r_r212);
CPyL177: ;
    cpy_r_r213 = ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__21;
    if (unlikely(cpy_r_r213 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "fetchone", "fetchone_AsyncCursor_gen", "__mypyc_temp__21", -1, CPyStatic_brownie___globals);
        goto CPyL411;
    }
    CPy_INCREF(cpy_r_r213);
CPyL178: ;
    PyObject *cpy_r_r214[4] = {cpy_r_r213, cpy_r_r209, cpy_r_r210, cpy_r_r211};
    cpy_r_r215 = (PyObject **)&cpy_r_r214;
    cpy_r_r216 = PyObject_Vectorcall(cpy_r_r212, cpy_r_r215, 4, 0);
    CPy_DecRef(cpy_r_r212);
    if (unlikely(cpy_r_r216 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL412;
    }
    CPy_DecRef(cpy_r_r213);
    CPy_DecRef(cpy_r_r209);
    CPy_DecRef(cpy_r_r210);
    CPy_DecRef(cpy_r_r211);
    cpy_r_r217 = CPy_GetCoro(cpy_r_r216);
    CPy_DecRef(cpy_r_r216);
    if (unlikely(cpy_r_r217 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL213;
    }
    if (((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__32 != NULL) {
        CPy_DECREF(((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__32);
    }
    ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__32 = cpy_r_r217;
    cpy_r_r218 = 1;
    if (unlikely(!cpy_r_r218)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", -1, CPyStatic_brownie___globals);
        goto CPyL213;
    }
    cpy_r_r219 = ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__32;
    if (unlikely(cpy_r_r219 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "fetchone", "fetchone_AsyncCursor_gen", "__mypyc_temp__32", -1, CPyStatic_brownie___globals);
        goto CPyL213;
    }
    CPy_INCREF(cpy_r_r219);
CPyL182: ;
    cpy_r_r220 = CPyIter_Next(cpy_r_r219);
    CPy_DecRef(cpy_r_r219);
    if (cpy_r_r220 != NULL) goto CPyL185;
    cpy_r_r221 = CPy_FetchStopIterationValue();
    if (unlikely(cpy_r_r221 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL213;
    }
    cpy_r_r222 = cpy_r_r221;
    cpy_r_r223 = NULL;
    if (((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__32 != NULL) {
        CPy_DECREF(((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__32);
    }
    ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__32 = cpy_r_r223;
    cpy_r_r224 = 1;
    if (unlikely(!cpy_r_r224)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL413;
    } else
        goto CPyL207;
CPyL185: ;
    cpy_r_r225 = cpy_r_r220;
CPyL186: ;
    ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_next_label__ = 5;
    return cpy_r_r225;
CPyL187: ;
    cpy_r_r227 = (PyObject *)&_Py_NoneStruct;
    cpy_r_r228 = cpy_r_type != cpy_r_r227;
    if (!cpy_r_r228) goto CPyL414;
    CPyErr_SetObjectAndTraceback(cpy_r_type, cpy_r_value, cpy_r_traceback);
    if (unlikely(!0)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL191;
    } else
        goto CPyL415;
CPyL189: ;
    CPy_Unreachable();
CPyL190: ;
    CPy_INCREF(cpy_r_arg);
    goto CPyL202;
CPyL191: ;
    cpy_r_r229 = CPy_CatchError();
    if (((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__33.f0 != NULL) {
        CPy_DECREF(((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__33.f0);
        CPy_DECREF(((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__33.f1);
        CPy_DECREF(((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__33.f2);
    }
    ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__33 = cpy_r_r229;
    cpy_r_r230 = 1;
    if (unlikely(!cpy_r_r230)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", -1, CPyStatic_brownie___globals);
        goto CPyL416;
    }
    cpy_r_r231 = (PyObject **)&cpy_r_r11;
    cpy_r_r232 = ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__32;
    if (unlikely(cpy_r_r232 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "fetchone", "fetchone_AsyncCursor_gen", "__mypyc_temp__32", -1, CPyStatic_brownie___globals);
        goto CPyL416;
    }
    CPy_INCREF(cpy_r_r232);
CPyL193: ;
    cpy_r_r233 = CPy_YieldFromErrorHandle(cpy_r_r232, cpy_r_r231);
    CPy_DecRef(cpy_r_r232);
    if (unlikely(cpy_r_r233 == 2)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL416;
    }
    if (cpy_r_r233) goto CPyL197;
    cpy_r_r225 = cpy_r_r11;
    cpy_r_r234 = ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__33;
    if (unlikely(cpy_r_r234.f0 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "fetchone", "fetchone_AsyncCursor_gen", "__mypyc_temp__33", -1, CPyStatic_brownie___globals);
        goto CPyL417;
    }
    CPy_INCREF(cpy_r_r234.f0);
    CPy_INCREF(cpy_r_r234.f1);
    CPy_INCREF(cpy_r_r234.f2);
CPyL196: ;
    CPy_RestoreExcInfo(cpy_r_r234);
    CPy_DecRef(cpy_r_r234.f0);
    CPy_DecRef(cpy_r_r234.f1);
    CPy_DecRef(cpy_r_r234.f2);
    goto CPyL186;
CPyL197: ;
    cpy_r_r222 = cpy_r_r11;
    cpy_r_r235 = ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__33;
    if (unlikely(cpy_r_r235.f0 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "fetchone", "fetchone_AsyncCursor_gen", "__mypyc_temp__33", -1, CPyStatic_brownie___globals);
        goto CPyL418;
    }
    CPy_INCREF(cpy_r_r235.f0);
    CPy_INCREF(cpy_r_r235.f1);
    CPy_INCREF(cpy_r_r235.f2);
CPyL198: ;
    CPy_RestoreExcInfo(cpy_r_r235);
    CPy_DecRef(cpy_r_r235.f0);
    CPy_DecRef(cpy_r_r235.f1);
    CPy_DecRef(cpy_r_r235.f2);
    goto CPyL207;
CPyL199: ;
    cpy_r_r236 = ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__33;
    if (unlikely(cpy_r_r236.f0 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "fetchone", "fetchone_AsyncCursor_gen", "__mypyc_temp__33", -1, CPyStatic_brownie___globals);
        goto CPyL213;
    }
    CPy_INCREF(cpy_r_r236.f0);
    CPy_INCREF(cpy_r_r236.f1);
    CPy_INCREF(cpy_r_r236.f2);
CPyL200: ;
    CPy_RestoreExcInfo(cpy_r_r236);
    CPy_DecRef(cpy_r_r236.f0);
    CPy_DecRef(cpy_r_r236.f1);
    CPy_DecRef(cpy_r_r236.f2);
    cpy_r_r237 = CPy_KeepPropagating();
    if (!cpy_r_r237) goto CPyL213;
    CPy_Unreachable();
CPyL202: ;
    cpy_r_r238 = ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__32;
    if (unlikely(cpy_r_r238 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "fetchone", "fetchone_AsyncCursor_gen", "__mypyc_temp__32", -1, CPyStatic_brownie___globals);
        goto CPyL419;
    }
    CPy_INCREF(cpy_r_r238);
CPyL203: ;
    cpy_r_r239 = CPyIter_Send(cpy_r_r238, cpy_r_arg);
    CPy_DECREF(cpy_r_r238);
    CPy_DECREF(cpy_r_arg);
    if (cpy_r_r239 == NULL) goto CPyL205;
    cpy_r_r225 = cpy_r_r239;
    goto CPyL186;
CPyL205: ;
    cpy_r_r240 = CPy_FetchStopIterationValue();
    if (unlikely(cpy_r_r240 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL213;
    }
    cpy_r_r222 = cpy_r_r240;
CPyL207: ;
    cpy_r_r241 = PyObject_IsTrue(cpy_r_r222);
    CPy_DECREF(cpy_r_r222);
    cpy_r_r242 = cpy_r_r241 >= 0;
    if (unlikely(!cpy_r_r242)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", -1, CPyStatic_brownie___globals);
        goto CPyL213;
    }
    cpy_r_r243 = cpy_r_r241;
    if (cpy_r_r243) goto CPyL211;
    CPy_Reraise();
    if (!0) goto CPyL213;
    CPy_Unreachable();
CPyL211: ;
    cpy_r_r244 = ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__31;
    if (unlikely(cpy_r_r244.f0 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "fetchone", "fetchone_AsyncCursor_gen", "__mypyc_temp__31", -1, CPyStatic_brownie___globals);
        goto CPyL218;
    }
    CPy_INCREF(cpy_r_r244.f0);
    CPy_INCREF(cpy_r_r244.f1);
    CPy_INCREF(cpy_r_r244.f2);
CPyL212: ;
    CPy_RestoreExcInfo(cpy_r_r244);
    CPy_DECREF(cpy_r_r244.f0);
    CPy_DECREF(cpy_r_r244.f1);
    CPy_DECREF(cpy_r_r244.f2);
    goto CPyL216;
CPyL213: ;
    cpy_r_r245 = ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__31;
    if (unlikely(cpy_r_r245.f0 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "fetchone", "fetchone_AsyncCursor_gen", "__mypyc_temp__31", -1, CPyStatic_brownie___globals);
        goto CPyL218;
    }
    CPy_INCREF(cpy_r_r245.f0);
    CPy_INCREF(cpy_r_r245.f1);
    CPy_INCREF(cpy_r_r245.f2);
CPyL214: ;
    CPy_RestoreExcInfo(cpy_r_r245);
    CPy_DECREF(cpy_r_r245.f0);
    CPy_DECREF(cpy_r_r245.f1);
    CPy_DECREF(cpy_r_r245.f2);
    cpy_r_r246 = CPy_KeepPropagating();
    if (!cpy_r_r246) goto CPyL218;
    CPy_Unreachable();
CPyL216: ;
    cpy_r_r247 = NULL;
    if (((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__27 != NULL) {
        CPy_DECREF(((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__27);
    }
    ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__27 = cpy_r_r247;
    cpy_r_r248 = 1;
    if (unlikely(!cpy_r_r248)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", -1, CPyStatic_brownie___globals);
        goto CPyL262;
    }
CPyL217: ;
    tuple_T3OOO __tmp13 = { NULL, NULL, NULL };
    cpy_r_r249 = __tmp13;
    cpy_r_r15 = cpy_r_r249;
    goto CPyL220;
CPyL218: ;
    cpy_r_r250 = NULL;
    if (((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__27 != NULL) {
        CPy_DECREF(((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__27);
    }
    ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__27 = cpy_r_r250;
    cpy_r_r251 = 1;
    if (unlikely(!cpy_r_r251)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", -1, CPyStatic_brownie___globals);
        goto CPyL262;
    }
    cpy_r_r252 = CPy_CatchError();
    cpy_r_r15 = cpy_r_r252;
CPyL220: ;
    cpy_r_r253 = ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__22;
    if (unlikely(cpy_r_r253 == 2)) {
        CPy_AttributeError("y/_db/brownie.py", "fetchone", "fetchone_AsyncCursor_gen", "__mypyc_temp__22", -1, CPyStatic_brownie___globals);
        goto CPyL258;
    }
CPyL221: ;
    if (!cpy_r_r253) goto CPyL253;
CPyL222: ;
    cpy_r_r254 = (PyObject *)&_Py_NoneStruct;
    cpy_r_r255 = ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__20;
    if (unlikely(cpy_r_r255 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "fetchone", "fetchone_AsyncCursor_gen", "__mypyc_temp__20", -1, CPyStatic_brownie___globals);
        goto CPyL258;
    }
    CPy_INCREF(cpy_r_r255);
CPyL223: ;
    cpy_r_r256 = ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__21;
    if (unlikely(cpy_r_r256 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "fetchone", "fetchone_AsyncCursor_gen", "__mypyc_temp__21", -1, CPyStatic_brownie___globals);
        goto CPyL420;
    }
    CPy_INCREF(cpy_r_r256);
CPyL224: ;
    PyObject *cpy_r_r257[4] = {cpy_r_r256, cpy_r_r254, cpy_r_r254, cpy_r_r254};
    cpy_r_r258 = (PyObject **)&cpy_r_r257;
    cpy_r_r259 = PyObject_Vectorcall(cpy_r_r255, cpy_r_r258, 4, 0);
    CPy_DECREF(cpy_r_r255);
    if (unlikely(cpy_r_r259 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL421;
    }
    CPy_DECREF(cpy_r_r256);
    cpy_r_r260 = CPy_GetCoro(cpy_r_r259);
    CPy_DECREF(cpy_r_r259);
    if (unlikely(cpy_r_r260 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL258;
    }
    if (((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__34 != NULL) {
        CPy_DECREF(((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__34);
    }
    ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__34 = cpy_r_r260;
    cpy_r_r261 = 1;
    if (unlikely(!cpy_r_r261)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", -1, CPyStatic_brownie___globals);
        goto CPyL258;
    }
    cpy_r_r262 = ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__34;
    if (unlikely(cpy_r_r262 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "fetchone", "fetchone_AsyncCursor_gen", "__mypyc_temp__34", -1, CPyStatic_brownie___globals);
        goto CPyL258;
    }
    CPy_INCREF(cpy_r_r262);
CPyL228: ;
    cpy_r_r263 = CPyIter_Next(cpy_r_r262);
    CPy_DECREF(cpy_r_r262);
    if (cpy_r_r263 != NULL) goto CPyL422;
    cpy_r_r264 = CPy_FetchStopIterationValue();
    if (unlikely(cpy_r_r264 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL258;
    }
    cpy_r_r265 = cpy_r_r264;
    CPy_DECREF(cpy_r_r265);
    cpy_r_r266 = NULL;
    if (((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__34 != NULL) {
        CPy_DECREF(((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__34);
    }
    ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__34 = cpy_r_r266;
    cpy_r_r267 = 1;
    if (unlikely(!cpy_r_r267)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL258;
    } else
        goto CPyL253;
CPyL231: ;
    cpy_r_r268 = cpy_r_r263;
CPyL232: ;
    ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_next_label__ = 6;
    return cpy_r_r268;
CPyL233: ;
    cpy_r_r270 = (PyObject *)&_Py_NoneStruct;
    cpy_r_r271 = cpy_r_type != cpy_r_r270;
    if (!cpy_r_r271) goto CPyL423;
    CPyErr_SetObjectAndTraceback(cpy_r_type, cpy_r_value, cpy_r_traceback);
    if (unlikely(!0)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL237;
    } else
        goto CPyL424;
CPyL235: ;
    CPy_Unreachable();
CPyL236: ;
    CPy_INCREF(cpy_r_arg);
    goto CPyL248;
CPyL237: ;
    cpy_r_r272 = CPy_CatchError();
    if (((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__35.f0 != NULL) {
        CPy_DECREF(((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__35.f0);
        CPy_DECREF(((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__35.f1);
        CPy_DECREF(((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__35.f2);
    }
    ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__35 = cpy_r_r272;
    cpy_r_r273 = 1;
    if (unlikely(!cpy_r_r273)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", -1, CPyStatic_brownie___globals);
        goto CPyL425;
    }
    cpy_r_r274 = (PyObject **)&cpy_r_r13;
    cpy_r_r275 = ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__34;
    if (unlikely(cpy_r_r275 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "fetchone", "fetchone_AsyncCursor_gen", "__mypyc_temp__34", -1, CPyStatic_brownie___globals);
        goto CPyL425;
    }
    CPy_INCREF(cpy_r_r275);
CPyL239: ;
    cpy_r_r276 = CPy_YieldFromErrorHandle(cpy_r_r275, cpy_r_r274);
    CPy_DecRef(cpy_r_r275);
    if (unlikely(cpy_r_r276 == 2)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL425;
    }
    if (cpy_r_r276) goto CPyL243;
    cpy_r_r268 = cpy_r_r13;
    cpy_r_r277 = ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__35;
    if (unlikely(cpy_r_r277.f0 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "fetchone", "fetchone_AsyncCursor_gen", "__mypyc_temp__35", -1, CPyStatic_brownie___globals);
        goto CPyL426;
    }
    CPy_INCREF(cpy_r_r277.f0);
    CPy_INCREF(cpy_r_r277.f1);
    CPy_INCREF(cpy_r_r277.f2);
    goto CPyL427;
CPyL242: ;
    CPy_RestoreExcInfo(cpy_r_r277);
    CPy_DecRef(cpy_r_r277.f0);
    CPy_DecRef(cpy_r_r277.f1);
    CPy_DecRef(cpy_r_r277.f2);
    goto CPyL232;
CPyL243: ;
    cpy_r_r265 = cpy_r_r13;
    CPy_DecRef(cpy_r_r265);
    cpy_r_r278 = ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__35;
    if (unlikely(cpy_r_r278.f0 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "fetchone", "fetchone_AsyncCursor_gen", "__mypyc_temp__35", -1, CPyStatic_brownie___globals);
        goto CPyL245;
    }
    CPy_INCREF(cpy_r_r278.f0);
    CPy_INCREF(cpy_r_r278.f1);
    CPy_INCREF(cpy_r_r278.f2);
CPyL244: ;
    CPy_RestoreExcInfo(cpy_r_r278);
    CPy_DecRef(cpy_r_r278.f0);
    CPy_DecRef(cpy_r_r278.f1);
    CPy_DecRef(cpy_r_r278.f2);
    goto CPyL253;
CPyL245: ;
    cpy_r_r279 = ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__35;
    if (unlikely(cpy_r_r279.f0 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "fetchone", "fetchone_AsyncCursor_gen", "__mypyc_temp__35", -1, CPyStatic_brownie___globals);
        goto CPyL258;
    }
    CPy_INCREF(cpy_r_r279.f0);
    CPy_INCREF(cpy_r_r279.f1);
    CPy_INCREF(cpy_r_r279.f2);
CPyL246: ;
    CPy_RestoreExcInfo(cpy_r_r279);
    CPy_DecRef(cpy_r_r279.f0);
    CPy_DecRef(cpy_r_r279.f1);
    CPy_DecRef(cpy_r_r279.f2);
    cpy_r_r280 = CPy_KeepPropagating();
    if (!cpy_r_r280) {
        goto CPyL258;
    } else
        goto CPyL428;
CPyL247: ;
    CPy_Unreachable();
CPyL248: ;
    cpy_r_r281 = ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__34;
    if (unlikely(cpy_r_r281 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "fetchone", "fetchone_AsyncCursor_gen", "__mypyc_temp__34", -1, CPyStatic_brownie___globals);
        goto CPyL429;
    }
    CPy_INCREF(cpy_r_r281);
CPyL249: ;
    cpy_r_r282 = CPyIter_Send(cpy_r_r281, cpy_r_arg);
    CPy_DECREF(cpy_r_r281);
    CPy_DECREF(cpy_r_arg);
    if (cpy_r_r282 == NULL) {
        goto CPyL251;
    } else
        goto CPyL430;
CPyL250: ;
    cpy_r_r268 = cpy_r_r282;
    goto CPyL232;
CPyL251: ;
    cpy_r_r283 = CPy_FetchStopIterationValue();
    if (unlikely(cpy_r_r283 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL258;
    }
    cpy_r_r265 = cpy_r_r283;
    CPy_DECREF(cpy_r_r265);
CPyL253: ;
    if (cpy_r_r15.f0 == NULL) goto CPyL256;
    CPy_Reraise();
    if (!0) {
        goto CPyL258;
    } else
        goto CPyL431;
CPyL255: ;
    CPy_Unreachable();
CPyL256: ;
    cpy_r_r284 = ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__27;
    if (cpy_r_r284 != NULL) {
        CPy_INCREF(cpy_r_r284);
    }
    if (cpy_r_r284 == NULL) goto CPyL304;
CPyL257: ;
    if (((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__36 != NULL) {
        CPy_DECREF(((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__36);
    }
    ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__36 = cpy_r_r284;
    cpy_r_r285 = 1;
    if (unlikely(!cpy_r_r285)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", -1, CPyStatic_brownie___globals);
        goto CPyL262;
    } else
        goto CPyL305;
CPyL258: ;
    if (cpy_r_r15.f0 == NULL) goto CPyL260;
    CPy_RestoreExcInfo(cpy_r_r15);
    CPy_XDECREF(cpy_r_r15.f0);
    CPy_XDECREF(cpy_r_r15.f1);
    CPy_XDECREF(cpy_r_r15.f2);
CPyL260: ;
    cpy_r_r286 = CPy_KeepPropagating();
    if (!cpy_r_r286) goto CPyL262;
    CPy_Unreachable();
CPyL262: ;
    cpy_r_r287 = CPy_CatchError();
    if (((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__37.f0 != NULL) {
        CPy_DECREF(((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__37.f0);
        CPy_DECREF(((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__37.f1);
        CPy_DECREF(((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__37.f2);
    }
    ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__37 = cpy_r_r287;
    cpy_r_r288 = 1;
    if (unlikely(!cpy_r_r288)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", -1, CPyStatic_brownie___globals);
        goto CPyL301;
    }
    ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__17 = 0;
    cpy_r_r289 = 1;
    if (unlikely(!cpy_r_r289)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL301;
    }
    cpy_r_r290 = CPy_GetExcInfo();
    cpy_r_r291 = cpy_r_r290.f0;
    CPy_INCREF(cpy_r_r291);
    cpy_r_r292 = cpy_r_r290.f1;
    CPy_INCREF(cpy_r_r292);
    cpy_r_r293 = cpy_r_r290.f2;
    CPy_INCREF(cpy_r_r293);
    CPy_DECREF(cpy_r_r290.f0);
    CPy_DECREF(cpy_r_r290.f1);
    CPy_DECREF(cpy_r_r290.f2);
    cpy_r_r294 = ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__15;
    if (unlikely(cpy_r_r294 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "fetchone", "fetchone_AsyncCursor_gen", "__mypyc_temp__15", -1, CPyStatic_brownie___globals);
        goto CPyL432;
    }
    CPy_INCREF(cpy_r_r294);
CPyL265: ;
    cpy_r_r295 = ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__16;
    if (unlikely(cpy_r_r295 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "fetchone", "fetchone_AsyncCursor_gen", "__mypyc_temp__16", -1, CPyStatic_brownie___globals);
        goto CPyL433;
    }
    CPy_INCREF(cpy_r_r295);
CPyL266: ;
    PyObject *cpy_r_r296[4] = {cpy_r_r295, cpy_r_r291, cpy_r_r292, cpy_r_r293};
    cpy_r_r297 = (PyObject **)&cpy_r_r296;
    cpy_r_r298 = PyObject_Vectorcall(cpy_r_r294, cpy_r_r297, 4, 0);
    CPy_DECREF(cpy_r_r294);
    if (unlikely(cpy_r_r298 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL434;
    }
    CPy_DECREF(cpy_r_r295);
    CPy_DECREF(cpy_r_r291);
    CPy_DECREF(cpy_r_r292);
    CPy_DECREF(cpy_r_r293);
    cpy_r_r299 = CPy_GetCoro(cpy_r_r298);
    CPy_DECREF(cpy_r_r298);
    if (unlikely(cpy_r_r299 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL301;
    }
    if (((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__38 != NULL) {
        CPy_DECREF(((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__38);
    }
    ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__38 = cpy_r_r299;
    cpy_r_r300 = 1;
    if (unlikely(!cpy_r_r300)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", -1, CPyStatic_brownie___globals);
        goto CPyL301;
    }
    cpy_r_r301 = ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__38;
    if (unlikely(cpy_r_r301 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "fetchone", "fetchone_AsyncCursor_gen", "__mypyc_temp__38", -1, CPyStatic_brownie___globals);
        goto CPyL301;
    }
    CPy_INCREF(cpy_r_r301);
CPyL270: ;
    cpy_r_r302 = CPyIter_Next(cpy_r_r301);
    CPy_DECREF(cpy_r_r301);
    if (cpy_r_r302 != NULL) goto CPyL273;
    cpy_r_r303 = CPy_FetchStopIterationValue();
    if (unlikely(cpy_r_r303 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL301;
    }
    cpy_r_r304 = cpy_r_r303;
    cpy_r_r305 = NULL;
    if (((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__38 != NULL) {
        CPy_DECREF(((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__38);
    }
    ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__38 = cpy_r_r305;
    cpy_r_r306 = 1;
    if (unlikely(!cpy_r_r306)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL435;
    } else
        goto CPyL295;
CPyL273: ;
    cpy_r_r307 = cpy_r_r302;
CPyL274: ;
    ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_next_label__ = 7;
    return cpy_r_r307;
CPyL275: ;
    cpy_r_r309 = (PyObject *)&_Py_NoneStruct;
    cpy_r_r310 = cpy_r_type != cpy_r_r309;
    if (!cpy_r_r310) goto CPyL436;
    CPyErr_SetObjectAndTraceback(cpy_r_type, cpy_r_value, cpy_r_traceback);
    if (unlikely(!0)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL279;
    } else
        goto CPyL437;
CPyL277: ;
    CPy_Unreachable();
CPyL278: ;
    CPy_INCREF(cpy_r_arg);
    goto CPyL290;
CPyL279: ;
    cpy_r_r311 = CPy_CatchError();
    if (((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__39.f0 != NULL) {
        CPy_DECREF(((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__39.f0);
        CPy_DECREF(((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__39.f1);
        CPy_DECREF(((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__39.f2);
    }
    ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__39 = cpy_r_r311;
    cpy_r_r312 = 1;
    if (unlikely(!cpy_r_r312)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", -1, CPyStatic_brownie___globals);
        goto CPyL438;
    }
    cpy_r_r313 = (PyObject **)&cpy_r_r17;
    cpy_r_r314 = ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__38;
    if (unlikely(cpy_r_r314 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "fetchone", "fetchone_AsyncCursor_gen", "__mypyc_temp__38", -1, CPyStatic_brownie___globals);
        goto CPyL438;
    }
    CPy_INCREF(cpy_r_r314);
CPyL281: ;
    cpy_r_r315 = CPy_YieldFromErrorHandle(cpy_r_r314, cpy_r_r313);
    CPy_DecRef(cpy_r_r314);
    if (unlikely(cpy_r_r315 == 2)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL438;
    }
    if (cpy_r_r315) goto CPyL285;
    cpy_r_r307 = cpy_r_r17;
    cpy_r_r316 = ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__39;
    if (unlikely(cpy_r_r316.f0 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "fetchone", "fetchone_AsyncCursor_gen", "__mypyc_temp__39", -1, CPyStatic_brownie___globals);
        goto CPyL439;
    }
    CPy_INCREF(cpy_r_r316.f0);
    CPy_INCREF(cpy_r_r316.f1);
    CPy_INCREF(cpy_r_r316.f2);
CPyL284: ;
    CPy_RestoreExcInfo(cpy_r_r316);
    CPy_DecRef(cpy_r_r316.f0);
    CPy_DecRef(cpy_r_r316.f1);
    CPy_DecRef(cpy_r_r316.f2);
    goto CPyL274;
CPyL285: ;
    cpy_r_r304 = cpy_r_r17;
    cpy_r_r317 = ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__39;
    if (unlikely(cpy_r_r317.f0 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "fetchone", "fetchone_AsyncCursor_gen", "__mypyc_temp__39", -1, CPyStatic_brownie___globals);
        goto CPyL440;
    }
    CPy_INCREF(cpy_r_r317.f0);
    CPy_INCREF(cpy_r_r317.f1);
    CPy_INCREF(cpy_r_r317.f2);
CPyL286: ;
    CPy_RestoreExcInfo(cpy_r_r317);
    CPy_DecRef(cpy_r_r317.f0);
    CPy_DecRef(cpy_r_r317.f1);
    CPy_DecRef(cpy_r_r317.f2);
    goto CPyL295;
CPyL287: ;
    cpy_r_r318 = ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__39;
    if (unlikely(cpy_r_r318.f0 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "fetchone", "fetchone_AsyncCursor_gen", "__mypyc_temp__39", -1, CPyStatic_brownie___globals);
        goto CPyL301;
    }
    CPy_INCREF(cpy_r_r318.f0);
    CPy_INCREF(cpy_r_r318.f1);
    CPy_INCREF(cpy_r_r318.f2);
CPyL288: ;
    CPy_RestoreExcInfo(cpy_r_r318);
    CPy_DecRef(cpy_r_r318.f0);
    CPy_DecRef(cpy_r_r318.f1);
    CPy_DecRef(cpy_r_r318.f2);
    cpy_r_r319 = CPy_KeepPropagating();
    if (!cpy_r_r319) goto CPyL301;
    CPy_Unreachable();
CPyL290: ;
    cpy_r_r320 = ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__38;
    if (unlikely(cpy_r_r320 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "fetchone", "fetchone_AsyncCursor_gen", "__mypyc_temp__38", -1, CPyStatic_brownie___globals);
        goto CPyL441;
    }
    CPy_INCREF(cpy_r_r320);
CPyL291: ;
    cpy_r_r321 = CPyIter_Send(cpy_r_r320, cpy_r_arg);
    CPy_DECREF(cpy_r_r320);
    CPy_DECREF(cpy_r_arg);
    if (cpy_r_r321 == NULL) goto CPyL293;
    cpy_r_r307 = cpy_r_r321;
    goto CPyL274;
CPyL293: ;
    cpy_r_r322 = CPy_FetchStopIterationValue();
    if (unlikely(cpy_r_r322 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL301;
    }
    cpy_r_r304 = cpy_r_r322;
CPyL295: ;
    cpy_r_r323 = PyObject_IsTrue(cpy_r_r304);
    CPy_DECREF(cpy_r_r304);
    cpy_r_r324 = cpy_r_r323 >= 0;
    if (unlikely(!cpy_r_r324)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", -1, CPyStatic_brownie___globals);
        goto CPyL301;
    }
    cpy_r_r325 = cpy_r_r323;
    if (cpy_r_r325) goto CPyL299;
    CPy_Reraise();
    if (!0) goto CPyL301;
    CPy_Unreachable();
CPyL299: ;
    cpy_r_r326 = ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__37;
    if (unlikely(cpy_r_r326.f0 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "fetchone", "fetchone_AsyncCursor_gen", "__mypyc_temp__37", -1, CPyStatic_brownie___globals);
        goto CPyL306;
    }
    CPy_INCREF(cpy_r_r326.f0);
    CPy_INCREF(cpy_r_r326.f1);
    CPy_INCREF(cpy_r_r326.f2);
CPyL300: ;
    CPy_RestoreExcInfo(cpy_r_r326);
    CPy_DECREF(cpy_r_r326.f0);
    CPy_DECREF(cpy_r_r326.f1);
    CPy_DECREF(cpy_r_r326.f2);
    goto CPyL304;
CPyL301: ;
    cpy_r_r327 = ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__37;
    if (unlikely(cpy_r_r327.f0 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "fetchone", "fetchone_AsyncCursor_gen", "__mypyc_temp__37", -1, CPyStatic_brownie___globals);
        goto CPyL306;
    }
    CPy_INCREF(cpy_r_r327.f0);
    CPy_INCREF(cpy_r_r327.f1);
    CPy_INCREF(cpy_r_r327.f2);
CPyL302: ;
    CPy_RestoreExcInfo(cpy_r_r327);
    CPy_DECREF(cpy_r_r327.f0);
    CPy_DECREF(cpy_r_r327.f1);
    CPy_DECREF(cpy_r_r327.f2);
    cpy_r_r328 = CPy_KeepPropagating();
    if (!cpy_r_r328) goto CPyL306;
    CPy_Unreachable();
CPyL304: ;
    cpy_r_r329 = NULL;
    if (((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__36 != NULL) {
        CPy_DECREF(((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__36);
    }
    ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__36 = cpy_r_r329;
    cpy_r_r330 = 1;
    if (unlikely(!cpy_r_r330)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", -1, CPyStatic_brownie___globals);
        goto CPyL370;
    }
CPyL305: ;
    tuple_T3OOO __tmp14 = { NULL, NULL, NULL };
    cpy_r_r331 = __tmp14;
    cpy_r_r21 = cpy_r_r331;
    goto CPyL308;
CPyL306: ;
    cpy_r_r332 = NULL;
    if (((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__36 != NULL) {
        CPy_DECREF(((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__36);
    }
    ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__36 = cpy_r_r332;
    cpy_r_r333 = 1;
    if (unlikely(!cpy_r_r333)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", -1, CPyStatic_brownie___globals);
        goto CPyL370;
    }
    cpy_r_r334 = CPy_CatchError();
    cpy_r_r21 = cpy_r_r334;
CPyL308: ;
    cpy_r_r335 = ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__17;
    if (unlikely(cpy_r_r335 == 2)) {
        CPy_AttributeError("y/_db/brownie.py", "fetchone", "fetchone_AsyncCursor_gen", "__mypyc_temp__17", -1, CPyStatic_brownie___globals);
        goto CPyL350;
    }
CPyL309: ;
    if (!cpy_r_r335) goto CPyL341;
CPyL310: ;
    cpy_r_r336 = (PyObject *)&_Py_NoneStruct;
    cpy_r_r337 = ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__15;
    if (unlikely(cpy_r_r337 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "fetchone", "fetchone_AsyncCursor_gen", "__mypyc_temp__15", -1, CPyStatic_brownie___globals);
        goto CPyL350;
    }
    CPy_INCREF(cpy_r_r337);
CPyL311: ;
    cpy_r_r338 = ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__16;
    if (unlikely(cpy_r_r338 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "fetchone", "fetchone_AsyncCursor_gen", "__mypyc_temp__16", -1, CPyStatic_brownie___globals);
        goto CPyL442;
    }
    CPy_INCREF(cpy_r_r338);
CPyL312: ;
    PyObject *cpy_r_r339[4] = {cpy_r_r338, cpy_r_r336, cpy_r_r336, cpy_r_r336};
    cpy_r_r340 = (PyObject **)&cpy_r_r339;
    cpy_r_r341 = PyObject_Vectorcall(cpy_r_r337, cpy_r_r340, 4, 0);
    CPy_DECREF(cpy_r_r337);
    if (unlikely(cpy_r_r341 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL443;
    }
    CPy_DECREF(cpy_r_r338);
    cpy_r_r342 = CPy_GetCoro(cpy_r_r341);
    CPy_DECREF(cpy_r_r341);
    if (unlikely(cpy_r_r342 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL350;
    }
    if (((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__40 != NULL) {
        CPy_DECREF(((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__40);
    }
    ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__40 = cpy_r_r342;
    cpy_r_r343 = 1;
    if (unlikely(!cpy_r_r343)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", -1, CPyStatic_brownie___globals);
        goto CPyL350;
    }
    cpy_r_r344 = ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__40;
    if (unlikely(cpy_r_r344 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "fetchone", "fetchone_AsyncCursor_gen", "__mypyc_temp__40", -1, CPyStatic_brownie___globals);
        goto CPyL350;
    }
    CPy_INCREF(cpy_r_r344);
CPyL316: ;
    cpy_r_r345 = CPyIter_Next(cpy_r_r344);
    CPy_DECREF(cpy_r_r344);
    if (cpy_r_r345 != NULL) goto CPyL444;
    cpy_r_r346 = CPy_FetchStopIterationValue();
    if (unlikely(cpy_r_r346 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL350;
    }
    cpy_r_r347 = cpy_r_r346;
    CPy_DECREF(cpy_r_r347);
    cpy_r_r348 = NULL;
    if (((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__40 != NULL) {
        CPy_DECREF(((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__40);
    }
    ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__40 = cpy_r_r348;
    cpy_r_r349 = 1;
    if (unlikely(!cpy_r_r349)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL350;
    } else
        goto CPyL341;
CPyL319: ;
    cpy_r_r350 = cpy_r_r345;
CPyL320: ;
    ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_next_label__ = 8;
    return cpy_r_r350;
CPyL321: ;
    cpy_r_r352 = (PyObject *)&_Py_NoneStruct;
    cpy_r_r353 = cpy_r_type != cpy_r_r352;
    if (!cpy_r_r353) goto CPyL445;
    CPyErr_SetObjectAndTraceback(cpy_r_type, cpy_r_value, cpy_r_traceback);
    if (unlikely(!0)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL325;
    } else
        goto CPyL446;
CPyL323: ;
    CPy_Unreachable();
CPyL324: ;
    CPy_INCREF(cpy_r_arg);
    goto CPyL336;
CPyL325: ;
    cpy_r_r354 = CPy_CatchError();
    if (((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__41.f0 != NULL) {
        CPy_DECREF(((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__41.f0);
        CPy_DECREF(((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__41.f1);
        CPy_DECREF(((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__41.f2);
    }
    ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__41 = cpy_r_r354;
    cpy_r_r355 = 1;
    if (unlikely(!cpy_r_r355)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", -1, CPyStatic_brownie___globals);
        goto CPyL447;
    }
    cpy_r_r356 = (PyObject **)&cpy_r_r19;
    cpy_r_r357 = ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__40;
    if (unlikely(cpy_r_r357 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "fetchone", "fetchone_AsyncCursor_gen", "__mypyc_temp__40", -1, CPyStatic_brownie___globals);
        goto CPyL447;
    }
    CPy_INCREF(cpy_r_r357);
CPyL327: ;
    cpy_r_r358 = CPy_YieldFromErrorHandle(cpy_r_r357, cpy_r_r356);
    CPy_DecRef(cpy_r_r357);
    if (unlikely(cpy_r_r358 == 2)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL447;
    }
    if (cpy_r_r358) goto CPyL331;
    cpy_r_r350 = cpy_r_r19;
    cpy_r_r359 = ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__41;
    if (unlikely(cpy_r_r359.f0 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "fetchone", "fetchone_AsyncCursor_gen", "__mypyc_temp__41", -1, CPyStatic_brownie___globals);
        goto CPyL448;
    }
    CPy_INCREF(cpy_r_r359.f0);
    CPy_INCREF(cpy_r_r359.f1);
    CPy_INCREF(cpy_r_r359.f2);
    goto CPyL449;
CPyL330: ;
    CPy_RestoreExcInfo(cpy_r_r359);
    CPy_DecRef(cpy_r_r359.f0);
    CPy_DecRef(cpy_r_r359.f1);
    CPy_DecRef(cpy_r_r359.f2);
    goto CPyL320;
CPyL331: ;
    cpy_r_r347 = cpy_r_r19;
    CPy_DecRef(cpy_r_r347);
    cpy_r_r360 = ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__41;
    if (unlikely(cpy_r_r360.f0 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "fetchone", "fetchone_AsyncCursor_gen", "__mypyc_temp__41", -1, CPyStatic_brownie___globals);
        goto CPyL333;
    }
    CPy_INCREF(cpy_r_r360.f0);
    CPy_INCREF(cpy_r_r360.f1);
    CPy_INCREF(cpy_r_r360.f2);
CPyL332: ;
    CPy_RestoreExcInfo(cpy_r_r360);
    CPy_DecRef(cpy_r_r360.f0);
    CPy_DecRef(cpy_r_r360.f1);
    CPy_DecRef(cpy_r_r360.f2);
    goto CPyL341;
CPyL333: ;
    cpy_r_r361 = ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__41;
    if (unlikely(cpy_r_r361.f0 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "fetchone", "fetchone_AsyncCursor_gen", "__mypyc_temp__41", -1, CPyStatic_brownie___globals);
        goto CPyL350;
    }
    CPy_INCREF(cpy_r_r361.f0);
    CPy_INCREF(cpy_r_r361.f1);
    CPy_INCREF(cpy_r_r361.f2);
CPyL334: ;
    CPy_RestoreExcInfo(cpy_r_r361);
    CPy_DecRef(cpy_r_r361.f0);
    CPy_DecRef(cpy_r_r361.f1);
    CPy_DecRef(cpy_r_r361.f2);
    cpy_r_r362 = CPy_KeepPropagating();
    if (!cpy_r_r362) {
        goto CPyL350;
    } else
        goto CPyL450;
CPyL335: ;
    CPy_Unreachable();
CPyL336: ;
    cpy_r_r363 = ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__40;
    if (unlikely(cpy_r_r363 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "fetchone", "fetchone_AsyncCursor_gen", "__mypyc_temp__40", -1, CPyStatic_brownie___globals);
        goto CPyL451;
    }
    CPy_INCREF(cpy_r_r363);
CPyL337: ;
    cpy_r_r364 = CPyIter_Send(cpy_r_r363, cpy_r_arg);
    CPy_DECREF(cpy_r_r363);
    CPy_DECREF(cpy_r_arg);
    if (cpy_r_r364 == NULL) {
        goto CPyL339;
    } else
        goto CPyL452;
CPyL338: ;
    cpy_r_r350 = cpy_r_r364;
    goto CPyL320;
CPyL339: ;
    cpy_r_r365 = CPy_FetchStopIterationValue();
    if (unlikely(cpy_r_r365 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL350;
    }
    cpy_r_r347 = cpy_r_r365;
    CPy_DECREF(cpy_r_r347);
CPyL341: ;
    if (cpy_r_r21.f0 == NULL) goto CPyL344;
    CPy_Reraise();
    if (!0) {
        goto CPyL350;
    } else
        goto CPyL453;
CPyL343: ;
    CPy_Unreachable();
CPyL344: ;
    cpy_r_r366 = ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__36;
    if (cpy_r_r366 != NULL) {
        CPy_INCREF(cpy_r_r366);
    }
    if (cpy_r_r366 == NULL) goto CPyL354;
CPyL345: ;
    ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_next_label__ = -1;
    if (cpy_r_stop_iter_ptr != NULL) goto CPyL349;
    CPyGen_SetStopIterationValue(cpy_r_r366);
    CPy_DECREF(cpy_r_r366);
    if (!0) goto CPyL370;
    CPy_Unreachable();
CPyL349: ;
    *(PyObject * *)cpy_r_stop_iter_ptr = cpy_r_r366;
    return 0;
CPyL350: ;
    if (cpy_r_r21.f0 == NULL) goto CPyL352;
    CPy_RestoreExcInfo(cpy_r_r21);
    CPy_XDECREF(cpy_r_r21.f0);
    CPy_XDECREF(cpy_r_r21.f1);
    CPy_XDECREF(cpy_r_r21.f2);
CPyL352: ;
    cpy_r_r368 = CPy_KeepPropagating();
    if (!cpy_r_r368) goto CPyL370;
    CPy_Unreachable();
CPyL354: ;
    cpy_r_r369 = Py_None;
    ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r___mypyc_self__)->___mypyc_next_label__ = -1;
    if (cpy_r_stop_iter_ptr != NULL) goto CPyL358;
    CPyGen_SetStopIterationValue(cpy_r_r369);
    if (!0) goto CPyL370;
    CPy_Unreachable();
CPyL358: ;
    *(PyObject * *)cpy_r_stop_iter_ptr = cpy_r_r369;
    return 0;
CPyL359: ;
    cpy_r_r371 = cpy_r_r22 == 0;
    if (cpy_r_r371) goto CPyL454;
    cpy_r_r372 = cpy_r_r22 == 1;
    if (cpy_r_r372) {
        goto CPyL455;
    } else
        goto CPyL456;
CPyL361: ;
    cpy_r_r373 = cpy_r_r22 == 2;
    if (cpy_r_r373) {
        goto CPyL457;
    } else
        goto CPyL458;
CPyL362: ;
    cpy_r_r374 = cpy_r_r22 == 3;
    if (cpy_r_r374) {
        goto CPyL459;
    } else
        goto CPyL460;
CPyL363: ;
    cpy_r_r375 = cpy_r_r22 == 4;
    if (cpy_r_r375) {
        goto CPyL461;
    } else
        goto CPyL462;
CPyL364: ;
    cpy_r_r376 = cpy_r_r22 == 5;
    if (cpy_r_r376) {
        goto CPyL463;
    } else
        goto CPyL464;
CPyL365: ;
    cpy_r_r377 = cpy_r_r22 == 6;
    if (cpy_r_r377) {
        goto CPyL465;
    } else
        goto CPyL466;
CPyL366: ;
    cpy_r_r378 = cpy_r_r22 == 7;
    if (cpy_r_r378) {
        goto CPyL467;
    } else
        goto CPyL468;
CPyL367: ;
    cpy_r_r379 = cpy_r_r22 == 8;
    if (cpy_r_r379) {
        goto CPyL321;
    } else
        goto CPyL469;
CPyL368: ;
    PyErr_SetNone(PyExc_StopIteration);
    cpy_r_r380 = 0;
    if (unlikely(!cpy_r_r380)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL370;
    }
    CPy_Unreachable();
CPyL370: ;
    cpy_r_r381 = NULL;
    return cpy_r_r381;
CPyL371: ;
    CPy_XDECREF(cpy_r_r1);
    goto CPyL13;
CPyL372: ;
    CPy_XDecRef(cpy_r_r1);
    goto CPyL370;
CPyL373: ;
    CPy_XDECREF(cpy_r_r3);
    goto CPyL18;
CPyL374: ;
    CPy_XDECREF(cpy_r_r3);
    goto CPyL17;
CPyL375: ;
    CPy_XDecRef(cpy_r_r3);
    goto CPyL27;
CPyL376: ;
    CPy_DecRef(cpy_r_r41);
    goto CPyL27;
CPyL377: ;
    CPy_DecRef(cpy_r_arg);
    goto CPyL370;
CPyL378: ;
    CPy_DecRef(cpy_r_r59);
    goto CPyL370;
CPyL379: ;
    CPy_DecRef(cpy_r_r67);
    goto CPyL370;
CPyL380: ;
    CPy_XDECREF(cpy_r_r5);
    goto CPyL55;
CPyL381: ;
    CPy_XDECREF(cpy_r_r5);
    goto CPyL54;
CPyL382: ;
    CPy_XDecRef(cpy_r_r5);
    goto CPyL64;
CPyL383: ;
    CPy_DecRef(cpy_r_r78);
    goto CPyL64;
CPyL384: ;
    CPy_DecRef(cpy_r_arg);
    goto CPyL370;
CPyL385: ;
    CPy_DecRef(cpy_r_r97);
    goto CPyL262;
CPyL386: ;
    CPy_DecRef(cpy_r_r97);
    CPy_DecRef(cpy_r_r98);
    goto CPyL262;
CPyL387: ;
    CPy_DecRef(cpy_r_r102);
    CPy_DecRef(cpy_r_r103);
    goto CPyL262;
CPyL388: ;
    CPy_DecRef(cpy_r_r102);
    goto CPyL262;
CPyL389: ;
    CPy_DecRef(cpy_r_r111);
    goto CPyL262;
CPyL390: ;
    CPy_DecRef(cpy_r_r119);
    goto CPyL262;
CPyL391: ;
    CPy_XDECREF(cpy_r_r7);
    goto CPyL95;
CPyL392: ;
    CPy_XDECREF(cpy_r_r7);
    goto CPyL94;
CPyL393: ;
    CPy_XDecRef(cpy_r_r7);
    goto CPyL104;
CPyL394: ;
    CPy_DecRef(cpy_r_r122);
    goto CPyL104;
CPyL395: ;
    CPy_DecRef(cpy_r_r119);
    goto CPyL104;
CPyL396: ;
    CPy_DecRef(cpy_r_arg);
    goto CPyL262;
CPyL397: ;
    CPy_DecRef(cpy_r_r139);
    goto CPyL174;
CPyL398: ;
    CPy_DecRef(cpy_r_r149);
    goto CPyL174;
CPyL399: ;
    CPy_XDECREF(cpy_r_r9);
    goto CPyL126;
CPyL400: ;
    CPy_XDECREF(cpy_r_r9);
    goto CPyL125;
CPyL401: ;
    CPy_XDecRef(cpy_r_r9);
    goto CPyL135;
CPyL402: ;
    CPy_DecRef(cpy_r_r152);
    goto CPyL135;
CPyL403: ;
    CPy_DecRef(cpy_r_r149);
    goto CPyL135;
CPyL404: ;
    CPy_DecRef(cpy_r_arg);
    goto CPyL174;
CPyL405: ;
    CPy_DecRef(cpy_r_r176);
    goto CPyL174;
CPyL406: ;
    CPy_DecRef(cpy_r_r177);
    goto CPyL174;
CPyL407: ;
    CPy_DecRef(cpy_r_r190);
    goto CPyL162;
CPyL408: ;
    CPy_DecRef(cpy_r_r190);
    goto CPyL174;
CPyL409: ;
    CPy_DecRef(cpy_r_r196);
    goto CPyL174;
CPyL410: ;
    CPy_DecRef(cpy_r_r209);
    CPy_DecRef(cpy_r_r210);
    CPy_DecRef(cpy_r_r211);
    goto CPyL213;
CPyL411: ;
    CPy_DecRef(cpy_r_r209);
    CPy_DecRef(cpy_r_r210);
    CPy_DecRef(cpy_r_r211);
    CPy_DecRef(cpy_r_r212);
    goto CPyL213;
CPyL412: ;
    CPy_DecRef(cpy_r_r209);
    CPy_DecRef(cpy_r_r210);
    CPy_DecRef(cpy_r_r211);
    CPy_DecRef(cpy_r_r213);
    goto CPyL213;
CPyL413: ;
    CPy_DecRef(cpy_r_r222);
    goto CPyL213;
CPyL414: ;
    CPy_XDECREF(cpy_r_r11);
    goto CPyL190;
CPyL415: ;
    CPy_XDECREF(cpy_r_r11);
    goto CPyL189;
CPyL416: ;
    CPy_XDecRef(cpy_r_r11);
    goto CPyL199;
CPyL417: ;
    CPy_DecRef(cpy_r_r225);
    goto CPyL199;
CPyL418: ;
    CPy_DecRef(cpy_r_r222);
    goto CPyL199;
CPyL419: ;
    CPy_DecRef(cpy_r_arg);
    goto CPyL213;
CPyL420: ;
    CPy_DecRef(cpy_r_r255);
    goto CPyL258;
CPyL421: ;
    CPy_DecRef(cpy_r_r256);
    goto CPyL258;
CPyL422: ;
    CPy_XDECREF(cpy_r_r15.f0);
    CPy_XDECREF(cpy_r_r15.f1);
    CPy_XDECREF(cpy_r_r15.f2);
    goto CPyL231;
CPyL423: ;
    CPy_XDECREF(cpy_r_r13);
    goto CPyL236;
CPyL424: ;
    CPy_XDECREF(cpy_r_r13);
    CPy_XDECREF(cpy_r_r15.f0);
    CPy_XDECREF(cpy_r_r15.f1);
    CPy_XDECREF(cpy_r_r15.f2);
    goto CPyL235;
CPyL425: ;
    CPy_XDecRef(cpy_r_r13);
    goto CPyL245;
CPyL426: ;
    CPy_DecRef(cpy_r_r268);
    goto CPyL245;
CPyL427: ;
    CPy_XDecRef(cpy_r_r15.f0);
    CPy_XDecRef(cpy_r_r15.f1);
    CPy_XDecRef(cpy_r_r15.f2);
    goto CPyL242;
CPyL428: ;
    CPy_XDecRef(cpy_r_r15.f0);
    CPy_XDecRef(cpy_r_r15.f1);
    CPy_XDecRef(cpy_r_r15.f2);
    goto CPyL247;
CPyL429: ;
    CPy_DecRef(cpy_r_arg);
    goto CPyL258;
CPyL430: ;
    CPy_XDECREF(cpy_r_r15.f0);
    CPy_XDECREF(cpy_r_r15.f1);
    CPy_XDECREF(cpy_r_r15.f2);
    goto CPyL250;
CPyL431: ;
    CPy_XDECREF(cpy_r_r15.f0);
    CPy_XDECREF(cpy_r_r15.f1);
    CPy_XDECREF(cpy_r_r15.f2);
    goto CPyL255;
CPyL432: ;
    CPy_DecRef(cpy_r_r291);
    CPy_DecRef(cpy_r_r292);
    CPy_DecRef(cpy_r_r293);
    goto CPyL301;
CPyL433: ;
    CPy_DecRef(cpy_r_r291);
    CPy_DecRef(cpy_r_r292);
    CPy_DecRef(cpy_r_r293);
    CPy_DecRef(cpy_r_r294);
    goto CPyL301;
CPyL434: ;
    CPy_DecRef(cpy_r_r291);
    CPy_DecRef(cpy_r_r292);
    CPy_DecRef(cpy_r_r293);
    CPy_DecRef(cpy_r_r295);
    goto CPyL301;
CPyL435: ;
    CPy_DecRef(cpy_r_r304);
    goto CPyL301;
CPyL436: ;
    CPy_XDECREF(cpy_r_r17);
    goto CPyL278;
CPyL437: ;
    CPy_XDECREF(cpy_r_r17);
    goto CPyL277;
CPyL438: ;
    CPy_XDecRef(cpy_r_r17);
    goto CPyL287;
CPyL439: ;
    CPy_DecRef(cpy_r_r307);
    goto CPyL287;
CPyL440: ;
    CPy_DecRef(cpy_r_r304);
    goto CPyL287;
CPyL441: ;
    CPy_DecRef(cpy_r_arg);
    goto CPyL301;
CPyL442: ;
    CPy_DecRef(cpy_r_r337);
    goto CPyL350;
CPyL443: ;
    CPy_DecRef(cpy_r_r338);
    goto CPyL350;
CPyL444: ;
    CPy_XDECREF(cpy_r_r21.f0);
    CPy_XDECREF(cpy_r_r21.f1);
    CPy_XDECREF(cpy_r_r21.f2);
    goto CPyL319;
CPyL445: ;
    CPy_XDECREF(cpy_r_r19);
    goto CPyL324;
CPyL446: ;
    CPy_XDECREF(cpy_r_r19);
    CPy_XDECREF(cpy_r_r21.f0);
    CPy_XDECREF(cpy_r_r21.f1);
    CPy_XDECREF(cpy_r_r21.f2);
    goto CPyL323;
CPyL447: ;
    CPy_XDecRef(cpy_r_r19);
    goto CPyL333;
CPyL448: ;
    CPy_DecRef(cpy_r_r350);
    goto CPyL333;
CPyL449: ;
    CPy_XDecRef(cpy_r_r21.f0);
    CPy_XDecRef(cpy_r_r21.f1);
    CPy_XDecRef(cpy_r_r21.f2);
    goto CPyL330;
CPyL450: ;
    CPy_XDecRef(cpy_r_r21.f0);
    CPy_XDecRef(cpy_r_r21.f1);
    CPy_XDecRef(cpy_r_r21.f2);
    goto CPyL335;
CPyL451: ;
    CPy_DecRef(cpy_r_arg);
    goto CPyL350;
CPyL452: ;
    CPy_XDECREF(cpy_r_r21.f0);
    CPy_XDECREF(cpy_r_r21.f1);
    CPy_XDECREF(cpy_r_r21.f2);
    goto CPyL338;
CPyL453: ;
    CPy_XDECREF(cpy_r_r21.f0);
    CPy_XDECREF(cpy_r_r21.f1);
    CPy_XDECREF(cpy_r_r21.f2);
    goto CPyL343;
CPyL454: ;
    CPy_XDECREF(cpy_r_r3);
    CPy_XDECREF(cpy_r_r5);
    CPy_XDECREF(cpy_r_r7);
    CPy_XDECREF(cpy_r_r9);
    CPy_XDECREF(cpy_r_r11);
    CPy_XDECREF(cpy_r_r13);
    CPy_XDECREF(cpy_r_r15.f0);
    CPy_XDECREF(cpy_r_r15.f1);
    CPy_XDECREF(cpy_r_r15.f2);
    CPy_XDECREF(cpy_r_r17);
    CPy_XDECREF(cpy_r_r19);
    CPy_XDECREF(cpy_r_r21.f0);
    CPy_XDECREF(cpy_r_r21.f1);
    CPy_XDECREF(cpy_r_r21.f2);
    goto CPyL1;
CPyL455: ;
    CPy_XDECREF(cpy_r_r5);
    CPy_XDECREF(cpy_r_r7);
    CPy_XDECREF(cpy_r_r9);
    CPy_XDECREF(cpy_r_r11);
    CPy_XDECREF(cpy_r_r13);
    CPy_XDECREF(cpy_r_r15.f0);
    CPy_XDECREF(cpy_r_r15.f1);
    CPy_XDECREF(cpy_r_r15.f2);
    CPy_XDECREF(cpy_r_r17);
    CPy_XDECREF(cpy_r_r19);
    CPy_XDECREF(cpy_r_r21.f0);
    CPy_XDECREF(cpy_r_r21.f1);
    CPy_XDECREF(cpy_r_r21.f2);
    goto CPyL15;
CPyL456: ;
    CPy_XDECREF(cpy_r_r3);
    goto CPyL361;
CPyL457: ;
    CPy_XDECREF(cpy_r_r7);
    CPy_XDECREF(cpy_r_r9);
    CPy_XDECREF(cpy_r_r11);
    CPy_XDECREF(cpy_r_r13);
    CPy_XDECREF(cpy_r_r15.f0);
    CPy_XDECREF(cpy_r_r15.f1);
    CPy_XDECREF(cpy_r_r15.f2);
    CPy_XDECREF(cpy_r_r17);
    CPy_XDECREF(cpy_r_r19);
    CPy_XDECREF(cpy_r_r21.f0);
    CPy_XDECREF(cpy_r_r21.f1);
    CPy_XDECREF(cpy_r_r21.f2);
    goto CPyL52;
CPyL458: ;
    CPy_XDECREF(cpy_r_r5);
    goto CPyL362;
CPyL459: ;
    CPy_XDECREF(cpy_r_r9);
    CPy_XDECREF(cpy_r_r11);
    CPy_XDECREF(cpy_r_r13);
    CPy_XDECREF(cpy_r_r15.f0);
    CPy_XDECREF(cpy_r_r15.f1);
    CPy_XDECREF(cpy_r_r15.f2);
    CPy_XDECREF(cpy_r_r17);
    CPy_XDECREF(cpy_r_r19);
    CPy_XDECREF(cpy_r_r21.f0);
    CPy_XDECREF(cpy_r_r21.f1);
    CPy_XDECREF(cpy_r_r21.f2);
    goto CPyL92;
CPyL460: ;
    CPy_XDECREF(cpy_r_r7);
    goto CPyL363;
CPyL461: ;
    CPy_XDECREF(cpy_r_r11);
    CPy_XDECREF(cpy_r_r13);
    CPy_XDECREF(cpy_r_r15.f0);
    CPy_XDECREF(cpy_r_r15.f1);
    CPy_XDECREF(cpy_r_r15.f2);
    CPy_XDECREF(cpy_r_r17);
    CPy_XDECREF(cpy_r_r19);
    CPy_XDECREF(cpy_r_r21.f0);
    CPy_XDECREF(cpy_r_r21.f1);
    CPy_XDECREF(cpy_r_r21.f2);
    goto CPyL123;
CPyL462: ;
    CPy_XDECREF(cpy_r_r9);
    goto CPyL364;
CPyL463: ;
    CPy_XDECREF(cpy_r_r13);
    CPy_XDECREF(cpy_r_r15.f0);
    CPy_XDECREF(cpy_r_r15.f1);
    CPy_XDECREF(cpy_r_r15.f2);
    CPy_XDECREF(cpy_r_r17);
    CPy_XDECREF(cpy_r_r19);
    CPy_XDECREF(cpy_r_r21.f0);
    CPy_XDECREF(cpy_r_r21.f1);
    CPy_XDECREF(cpy_r_r21.f2);
    goto CPyL187;
CPyL464: ;
    CPy_XDECREF(cpy_r_r11);
    goto CPyL365;
CPyL465: ;
    CPy_XDECREF(cpy_r_r17);
    CPy_XDECREF(cpy_r_r19);
    CPy_XDECREF(cpy_r_r21.f0);
    CPy_XDECREF(cpy_r_r21.f1);
    CPy_XDECREF(cpy_r_r21.f2);
    goto CPyL233;
CPyL466: ;
    CPy_XDECREF(cpy_r_r13);
    CPy_XDECREF(cpy_r_r15.f0);
    CPy_XDECREF(cpy_r_r15.f1);
    CPy_XDECREF(cpy_r_r15.f2);
    goto CPyL366;
CPyL467: ;
    CPy_XDECREF(cpy_r_r19);
    CPy_XDECREF(cpy_r_r21.f0);
    CPy_XDECREF(cpy_r_r21.f1);
    CPy_XDECREF(cpy_r_r21.f2);
    goto CPyL275;
CPyL468: ;
    CPy_XDECREF(cpy_r_r17);
    goto CPyL367;
CPyL469: ;
    CPy_XDECREF(cpy_r_r19);
    CPy_XDECREF(cpy_r_r21.f0);
    CPy_XDECREF(cpy_r_r21.f1);
    CPy_XDECREF(cpy_r_r21.f2);
    goto CPyL368;
}

PyObject *CPyDef_brownie___fetchone_AsyncCursor_gen_____next__(PyObject *cpy_r___mypyc_self__) {
    PyObject *cpy_r_r0;
    PyObject *cpy_r_r1;
    PyObject *cpy_r_r2;
    cpy_r_r0 = (PyObject *)&_Py_NoneStruct;
    cpy_r_r1 = CPyDef_brownie___fetchone_AsyncCursor_gen_____mypyc_generator_helper__(cpy_r___mypyc_self__, cpy_r_r0, cpy_r_r0, cpy_r_r0, cpy_r_r0, 0);
    if (cpy_r_r1 == NULL) goto CPyL2;
    return cpy_r_r1;
CPyL2: ;
    cpy_r_r2 = NULL;
    return cpy_r_r2;
}

PyObject *CPyPy_brownie___fetchone_AsyncCursor_gen_____next__(PyObject *self, PyObject *const *args, size_t nargs, PyObject *kwnames) {
    PyObject *obj___mypyc_self__ = self;
    static const char * const kwlist[] = {0};
    static CPyArg_Parser parser = {":__next__", kwlist, 0};
    if (!CPyArg_ParseStackAndKeywordsNoArgs(args, nargs, kwnames, &parser)) {
        return NULL;
    }
    PyObject *arg___mypyc_self__;
    if (likely(Py_TYPE(obj___mypyc_self__) == CPyType_brownie___fetchone_AsyncCursor_gen))
        arg___mypyc_self__ = obj___mypyc_self__;
    else {
        CPy_TypeError("y._db.brownie.fetchone_AsyncCursor_gen", obj___mypyc_self__); 
        goto fail;
    }
    PyObject *retval = CPyDef_brownie___fetchone_AsyncCursor_gen_____next__(arg___mypyc_self__);
    return retval;
fail: ;
    CPy_AddTraceback("y/_db/brownie.py", "__next__", -1, CPyStatic_brownie___globals);
    return NULL;
}

PyObject *CPyDef_brownie___fetchone_AsyncCursor_gen___send(PyObject *cpy_r___mypyc_self__, PyObject *cpy_r_arg) {
    PyObject *cpy_r_r0;
    PyObject *cpy_r_r1;
    PyObject *cpy_r_r2;
    cpy_r_r0 = (PyObject *)&_Py_NoneStruct;
    cpy_r_r1 = CPyDef_brownie___fetchone_AsyncCursor_gen_____mypyc_generator_helper__(cpy_r___mypyc_self__, cpy_r_r0, cpy_r_r0, cpy_r_r0, cpy_r_arg, 0);
    if (cpy_r_r1 == NULL) goto CPyL2;
    return cpy_r_r1;
CPyL2: ;
    cpy_r_r2 = NULL;
    return cpy_r_r2;
}

PyObject *CPyPy_brownie___fetchone_AsyncCursor_gen___send(PyObject *self, PyObject *const *args, size_t nargs, PyObject *kwnames) {
    PyObject *obj___mypyc_self__ = self;
    static const char * const kwlist[] = {"arg", 0};
    static CPyArg_Parser parser = {"O:send", kwlist, 0};
    PyObject *obj_arg;
    if (!CPyArg_ParseStackAndKeywordsOneArg(args, nargs, kwnames, &parser, &obj_arg)) {
        return NULL;
    }
    PyObject *arg___mypyc_self__;
    if (likely(Py_TYPE(obj___mypyc_self__) == CPyType_brownie___fetchone_AsyncCursor_gen))
        arg___mypyc_self__ = obj___mypyc_self__;
    else {
        CPy_TypeError("y._db.brownie.fetchone_AsyncCursor_gen", obj___mypyc_self__); 
        goto fail;
    }
    PyObject *arg_arg = obj_arg;
    PyObject *retval = CPyDef_brownie___fetchone_AsyncCursor_gen___send(arg___mypyc_self__, arg_arg);
    return retval;
fail: ;
    CPy_AddTraceback("y/_db/brownie.py", "send", -1, CPyStatic_brownie___globals);
    return NULL;
}

PyObject *CPyDef_brownie___fetchone_AsyncCursor_gen_____iter__(PyObject *cpy_r___mypyc_self__) {
    CPy_INCREF_NO_IMM(cpy_r___mypyc_self__);
    return cpy_r___mypyc_self__;
}

PyObject *CPyPy_brownie___fetchone_AsyncCursor_gen_____iter__(PyObject *self, PyObject *const *args, size_t nargs, PyObject *kwnames) {
    PyObject *obj___mypyc_self__ = self;
    static const char * const kwlist[] = {0};
    static CPyArg_Parser parser = {":__iter__", kwlist, 0};
    if (!CPyArg_ParseStackAndKeywordsNoArgs(args, nargs, kwnames, &parser)) {
        return NULL;
    }
    PyObject *arg___mypyc_self__;
    if (likely(Py_TYPE(obj___mypyc_self__) == CPyType_brownie___fetchone_AsyncCursor_gen))
        arg___mypyc_self__ = obj___mypyc_self__;
    else {
        CPy_TypeError("y._db.brownie.fetchone_AsyncCursor_gen", obj___mypyc_self__); 
        goto fail;
    }
    PyObject *retval = CPyDef_brownie___fetchone_AsyncCursor_gen_____iter__(arg___mypyc_self__);
    return retval;
fail: ;
    CPy_AddTraceback("y/_db/brownie.py", "__iter__", -1, CPyStatic_brownie___globals);
    return NULL;
}

PyObject *CPyDef_brownie___fetchone_AsyncCursor_gen___throw(PyObject *cpy_r___mypyc_self__, PyObject *cpy_r_type, PyObject *cpy_r_value, PyObject *cpy_r_traceback) {
    PyObject *cpy_r_r0;
    PyObject *cpy_r_r1;
    PyObject *cpy_r_r2;
    cpy_r_r0 = (PyObject *)&_Py_NoneStruct;
    if (cpy_r_value != NULL) goto CPyL7;
    CPy_INCREF(cpy_r_r0);
    cpy_r_value = cpy_r_r0;
CPyL2: ;
    if (cpy_r_traceback != NULL) goto CPyL8;
    CPy_INCREF(cpy_r_r0);
    cpy_r_traceback = cpy_r_r0;
CPyL4: ;
    cpy_r_r1 = CPyDef_brownie___fetchone_AsyncCursor_gen_____mypyc_generator_helper__(cpy_r___mypyc_self__, cpy_r_type, cpy_r_value, cpy_r_traceback, cpy_r_r0, 0);
    CPy_DECREF(cpy_r_value);
    CPy_DECREF(cpy_r_traceback);
    if (cpy_r_r1 == NULL) goto CPyL6;
    return cpy_r_r1;
CPyL6: ;
    cpy_r_r2 = NULL;
    return cpy_r_r2;
CPyL7: ;
    CPy_INCREF(cpy_r_value);
    goto CPyL2;
CPyL8: ;
    CPy_INCREF(cpy_r_traceback);
    goto CPyL4;
}

PyObject *CPyPy_brownie___fetchone_AsyncCursor_gen___throw(PyObject *self, PyObject *const *args, size_t nargs, PyObject *kwnames) {
    PyObject *obj___mypyc_self__ = self;
    static const char * const kwlist[] = {"type", "value", "traceback", 0};
    static CPyArg_Parser parser = {"O|OO:throw", kwlist, 0};
    PyObject *obj_type;
    PyObject *obj_value = NULL;
    PyObject *obj_traceback = NULL;
    if (!CPyArg_ParseStackAndKeywordsSimple(args, nargs, kwnames, &parser, &obj_type, &obj_value, &obj_traceback)) {
        return NULL;
    }
    PyObject *arg___mypyc_self__;
    if (likely(Py_TYPE(obj___mypyc_self__) == CPyType_brownie___fetchone_AsyncCursor_gen))
        arg___mypyc_self__ = obj___mypyc_self__;
    else {
        CPy_TypeError("y._db.brownie.fetchone_AsyncCursor_gen", obj___mypyc_self__); 
        goto fail;
    }
    PyObject *arg_type = obj_type;
    PyObject *arg_value;
    if (obj_value == NULL) {
        arg_value = NULL;
    } else {
        arg_value = obj_value; 
    }
    PyObject *arg_traceback;
    if (obj_traceback == NULL) {
        arg_traceback = NULL;
    } else {
        arg_traceback = obj_traceback; 
    }
    PyObject *retval = CPyDef_brownie___fetchone_AsyncCursor_gen___throw(arg___mypyc_self__, arg_type, arg_value, arg_traceback);
    return retval;
fail: ;
    CPy_AddTraceback("y/_db/brownie.py", "throw", -1, CPyStatic_brownie___globals);
    return NULL;
}

PyObject *CPyDef_brownie___fetchone_AsyncCursor_gen___close(PyObject *cpy_r___mypyc_self__) {
    PyObject *cpy_r_r0;
    PyObject *cpy_r_r1;
    PyObject *cpy_r_r2;
    PyObject *cpy_r_r3;
    PyObject *cpy_r_r4;
    PyObject *cpy_r_r5;
    tuple_T3OOO cpy_r_r6;
    PyObject *cpy_r_r7;
    PyObject *cpy_r_r8;
    PyObject *cpy_r_r9;
    tuple_T2OO cpy_r_r10;
    PyObject *cpy_r_r11;
    char cpy_r_r12;
    PyObject *cpy_r_r13;
    char cpy_r_r14;
    PyObject *cpy_r_r15;
    cpy_r_r0 = CPyModule_builtins;
    cpy_r_r1 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'GeneratorExit' */
    cpy_r_r2 = CPyObject_GetAttr(cpy_r_r0, cpy_r_r1);
    if (cpy_r_r2 == NULL) goto CPyL3;
    cpy_r_r3 = (PyObject *)&_Py_NoneStruct;
    cpy_r_r4 = (PyObject *)&_Py_NoneStruct;
    cpy_r_r5 = CPyDef_brownie___fetchone_AsyncCursor_gen___throw(cpy_r___mypyc_self__, cpy_r_r2, cpy_r_r3, cpy_r_r4);
    if (cpy_r_r5 != NULL) goto CPyL11;
CPyL3: ;
    cpy_r_r6 = CPy_CatchError();
    cpy_r_r7 = CPyModule_builtins;
    cpy_r_r8 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'StopIteration' */
    cpy_r_r9 = CPyObject_GetAttr(cpy_r_r7, cpy_r_r8);
    if (cpy_r_r9 == NULL) goto CPyL12;
    cpy_r_r10.f0 = cpy_r_r2;
    cpy_r_r10.f1 = cpy_r_r9;
    cpy_r_r11 = PyTuple_New(2);
    if (unlikely(cpy_r_r11 == NULL))
        CPyError_OutOfMemory();
    PyObject *__tmp15 = cpy_r_r10.f0;
    PyTuple_SET_ITEM(cpy_r_r11, 0, __tmp15);
    PyObject *__tmp16 = cpy_r_r10.f1;
    PyTuple_SET_ITEM(cpy_r_r11, 1, __tmp16);
    cpy_r_r12 = CPy_ExceptionMatches(cpy_r_r11);
    CPy_DECREF(cpy_r_r11);
    if (!cpy_r_r12) goto CPyL13;
    CPy_RestoreExcInfo(cpy_r_r6);
    CPy_DECREF(cpy_r_r6.f0);
    CPy_DECREF(cpy_r_r6.f1);
    CPy_DECREF(cpy_r_r6.f2);
    cpy_r_r13 = (PyObject *)&_Py_NoneStruct;
    CPy_INCREF(cpy_r_r13);
    return cpy_r_r13;
CPyL6: ;
    CPy_Reraise();
    if (!0) goto CPyL10;
    CPy_Unreachable();
CPyL8: ;
    PyErr_SetString(PyExc_RuntimeError, "generator ignored GeneratorExit");
    cpy_r_r14 = 0;
    if (!cpy_r_r14) goto CPyL10;
    CPy_Unreachable();
CPyL10: ;
    cpy_r_r15 = NULL;
    return cpy_r_r15;
CPyL11: ;
    CPy_DECREF(cpy_r_r2);
    CPy_DECREF(cpy_r_r5);
    goto CPyL8;
CPyL12: ;
    CPy_DECREF(cpy_r_r2);
    CPy_DECREF(cpy_r_r6.f0);
    CPy_DECREF(cpy_r_r6.f1);
    CPy_DECREF(cpy_r_r6.f2);
    goto CPyL10;
CPyL13: ;
    CPy_DECREF(cpy_r_r6.f0);
    CPy_DECREF(cpy_r_r6.f1);
    CPy_DECREF(cpy_r_r6.f2);
    goto CPyL6;
}

PyObject *CPyPy_brownie___fetchone_AsyncCursor_gen___close(PyObject *self, PyObject *const *args, size_t nargs, PyObject *kwnames) {
    PyObject *obj___mypyc_self__ = self;
    static const char * const kwlist[] = {0};
    static CPyArg_Parser parser = {":close", kwlist, 0};
    if (!CPyArg_ParseStackAndKeywordsNoArgs(args, nargs, kwnames, &parser)) {
        return NULL;
    }
    PyObject *arg___mypyc_self__;
    if (likely(Py_TYPE(obj___mypyc_self__) == CPyType_brownie___fetchone_AsyncCursor_gen))
        arg___mypyc_self__ = obj___mypyc_self__;
    else {
        CPy_TypeError("y._db.brownie.fetchone_AsyncCursor_gen", obj___mypyc_self__); 
        goto fail;
    }
    PyObject *retval = CPyDef_brownie___fetchone_AsyncCursor_gen___close(arg___mypyc_self__);
    return retval;
fail: ;
    CPy_AddTraceback("y/_db/brownie.py", "close", -1, CPyStatic_brownie___globals);
    return NULL;
}

PyObject *CPyDef_brownie___fetchone_AsyncCursor_gen_____await__(PyObject *cpy_r___mypyc_self__) {
    CPy_INCREF_NO_IMM(cpy_r___mypyc_self__);
    return cpy_r___mypyc_self__;
}

PyObject *CPyPy_brownie___fetchone_AsyncCursor_gen_____await__(PyObject *self, PyObject *const *args, size_t nargs, PyObject *kwnames) {
    PyObject *obj___mypyc_self__ = self;
    static const char * const kwlist[] = {0};
    static CPyArg_Parser parser = {":__await__", kwlist, 0};
    if (!CPyArg_ParseStackAndKeywordsNoArgs(args, nargs, kwnames, &parser)) {
        return NULL;
    }
    PyObject *arg___mypyc_self__;
    if (likely(Py_TYPE(obj___mypyc_self__) == CPyType_brownie___fetchone_AsyncCursor_gen))
        arg___mypyc_self__ = obj___mypyc_self__;
    else {
        CPy_TypeError("y._db.brownie.fetchone_AsyncCursor_gen", obj___mypyc_self__); 
        goto fail;
    }
    PyObject *retval = CPyDef_brownie___fetchone_AsyncCursor_gen_____await__(arg___mypyc_self__);
    return retval;
fail: ;
    CPy_AddTraceback("y/_db/brownie.py", "__await__", -1, CPyStatic_brownie___globals);
    return NULL;
}

PyObject *CPyDef_brownie___AsyncCursor___fetchone(PyObject *cpy_r_self, PyObject *cpy_r_cmd, PyObject *cpy_r_args) {
    PyObject *cpy_r_r0;
    char cpy_r_r1;
    char cpy_r_r2;
    char cpy_r_r3;
    char cpy_r_r4;
    PyObject *cpy_r_r5;
    cpy_r_r0 = CPyDef_brownie___fetchone_AsyncCursor_gen();
    if (unlikely(cpy_r_r0 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL5;
    }
    ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r_r0)->___mypyc_next_label__ = 0;
    CPy_INCREF_NO_IMM(cpy_r_self);
    if (((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r_r0)->___mypyc_generator_attribute__self != NULL) {
        CPy_DECREF_NO_IMM(((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r_r0)->___mypyc_generator_attribute__self);
    }
    ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r_r0)->___mypyc_generator_attribute__self = cpy_r_self;
    cpy_r_r2 = 1;
    if (unlikely(!cpy_r_r2)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL6;
    }
    CPy_INCREF(cpy_r_cmd);
    if (((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r_r0)->___mypyc_generator_attribute__cmd != NULL) {
        CPy_DECREF(((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r_r0)->___mypyc_generator_attribute__cmd);
    }
    ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r_r0)->___mypyc_generator_attribute__cmd = cpy_r_cmd;
    cpy_r_r3 = 1;
    if (unlikely(!cpy_r_r3)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL6;
    }
    CPy_INCREF(cpy_r_args);
    if (((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r_r0)->___mypyc_generator_attribute__args != NULL) {
        CPy_DECREF(((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r_r0)->___mypyc_generator_attribute__args);
    }
    ((y____db___brownie___fetchone_AsyncCursor_genObject *)cpy_r_r0)->___mypyc_generator_attribute__args = cpy_r_args;
    cpy_r_r4 = 1;
    if (unlikely(!cpy_r_r4)) {
        CPy_AddTraceback("y/_db/brownie.py", "fetchone", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL6;
    }
    return cpy_r_r0;
CPyL5: ;
    cpy_r_r5 = NULL;
    return cpy_r_r5;
CPyL6: ;
    CPy_DecRef(cpy_r_r0);
    goto CPyL5;
}

PyObject *CPyPy_brownie___AsyncCursor___fetchone(PyObject *self, PyObject *const *args, size_t nargs, PyObject *kwnames) {
    PyObject *obj_self = self;
    static const char * const kwlist[] = {"cmd", 0};
    static CPyArg_Parser parser = {"%O:fetchone", kwlist, 0};
    PyObject *obj_cmd;
    PyObject *obj_args;
    if (!CPyArg_ParseStackAndKeywords(args, nargs, kwnames, &parser, &obj_args, NULL, &obj_cmd)) {
        return NULL;
    }
    PyObject *arg_self;
    if (likely(Py_TYPE(obj_self) == CPyType_brownie___AsyncCursor))
        arg_self = obj_self;
    else {
        CPy_TypeError("y._db.brownie.AsyncCursor", obj_self); 
        goto fail;
    }
    PyObject *arg_cmd;
    if (likely(PyUnicode_Check(obj_cmd)))
        arg_cmd = obj_cmd;
    else {
        CPy_TypeError("str", obj_cmd); 
        goto fail;
    }
    PyObject *arg_args = obj_args;
    PyObject *retval = CPyDef_brownie___AsyncCursor___fetchone(arg_self, arg_cmd, arg_args);
    CPy_DECREF(obj_args);
    return retval;
fail: ;
    CPy_DECREF(obj_args);
    CPy_AddTraceback("y/_db/brownie.py", "fetchone", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
    return NULL;
}

PyObject *CPyDef_brownie____get_select_statement(void) {
    PyObject *cpy_r_r0;
    PyObject *cpy_r_r1;
    PyObject *cpy_r_r2;
    PyObject *cpy_r_r3;
    PyObject *cpy_r_r4;
    PyObject *cpy_r_r5;
    PyObject *cpy_r_r6;
    PyObject *cpy_r_r7;
    PyObject *cpy_r_r8;
    PyObject *cpy_r_r9;
    PyObject *cpy_r_r10;
    tuple_T3OOO cpy_r_r11;
    PyObject *cpy_r_r12;
    PyObject *cpy_r_r13;
    PyObject *cpy_r_r14;
    char cpy_r_r15;
    PyObject *cpy_r_r16;
    PyObject *cpy_r_r17;
    PyObject *cpy_r_r18;
    PyObject *cpy_r_r19;
    PyObject **cpy_r_r21;
    PyObject *cpy_r_r22;
    char cpy_r_r23;
    PyObject *cpy_r_r24;
    cpy_r_r0 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'SELECT * FROM chain' */
    cpy_r_r1 = CPyStatic_brownie___globals;
    cpy_r_r2 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'CONFIG' */
    cpy_r_r3 = CPyDict_GetItem(cpy_r_r1, cpy_r_r2);
    if (unlikely(cpy_r_r3 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_select_statement", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL8;
    }
    cpy_r_r4 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'active_network' */
    cpy_r_r5 = CPyObject_GetAttr(cpy_r_r3, cpy_r_r4);
    CPy_DECREF(cpy_r_r3);
    if (unlikely(cpy_r_r5 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_select_statement", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL8;
    }
    if (likely(PyDict_Check(cpy_r_r5)))
        cpy_r_r6 = cpy_r_r5;
    else {
        CPy_TypeErrorTraceback("y/_db/brownie.py", "_get_select_statement", 145, CPyStatic_brownie___globals, "dict", cpy_r_r5);
        goto CPyL8;
    }
    cpy_r_r7 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'chainid' */
    cpy_r_r8 = CPyDict_GetItem(cpy_r_r6, cpy_r_r7);
    CPy_DECREF(cpy_r_r6);
    if (unlikely(cpy_r_r8 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_select_statement", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL8;
    }
    cpy_r_r9 = PyObject_Str(cpy_r_r8);
    CPy_DECREF(cpy_r_r8);
    if (unlikely(cpy_r_r9 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_select_statement", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL8;
    }
    cpy_r_r10 = CPyStr_Build(2, cpy_r_r0, cpy_r_r9);
    CPy_DECREF(cpy_r_r9);
    if (unlikely(cpy_r_r10 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_select_statement", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL8;
    }
    return cpy_r_r10;
CPyL8: ;
    cpy_r_r11 = CPy_CatchError();
    cpy_r_r12 = CPyModule_builtins;
    cpy_r_r13 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'KeyError' */
    cpy_r_r14 = CPyObject_GetAttr(cpy_r_r12, cpy_r_r13);
    if (unlikely(cpy_r_r14 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_select_statement", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL16;
    }
    cpy_r_r15 = CPy_ExceptionMatches(cpy_r_r14);
    CPy_DecRef(cpy_r_r14);
    if (!cpy_r_r15) goto CPyL14;
    cpy_r_r16 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'Functionality not available in local environment' */
    cpy_r_r17 = CPyStatic_brownie___globals;
    cpy_r_r18 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'BrownieEnvironmentError' */
    cpy_r_r19 = CPyDict_GetItem(cpy_r_r17, cpy_r_r18);
    if (unlikely(cpy_r_r19 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_select_statement", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL16;
    }
    PyObject *cpy_r_r20[1] = {cpy_r_r16};
    cpy_r_r21 = (PyObject **)&cpy_r_r20;
    cpy_r_r22 = PyObject_Vectorcall(cpy_r_r19, cpy_r_r21, 1, 0);
    CPy_DecRef(cpy_r_r19);
    if (unlikely(cpy_r_r22 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_select_statement", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL16;
    }
    CPy_Raise(cpy_r_r22);
    CPy_DecRef(cpy_r_r22);
    if (unlikely(!0)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_select_statement", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL16;
    } else
        goto CPyL19;
CPyL13: ;
    CPy_Unreachable();
CPyL14: ;
    CPy_Reraise();
    if (!0) {
        goto CPyL16;
    } else
        goto CPyL20;
CPyL15: ;
    CPy_Unreachable();
CPyL16: ;
    CPy_RestoreExcInfo(cpy_r_r11);
    CPy_DecRef(cpy_r_r11.f0);
    CPy_DecRef(cpy_r_r11.f1);
    CPy_DecRef(cpy_r_r11.f2);
    cpy_r_r23 = CPy_KeepPropagating();
    if (!cpy_r_r23) goto CPyL18;
    CPy_Unreachable();
CPyL18: ;
    cpy_r_r24 = NULL;
    return cpy_r_r24;
CPyL19: ;
    CPy_DecRef(cpy_r_r11.f0);
    CPy_DecRef(cpy_r_r11.f1);
    CPy_DecRef(cpy_r_r11.f2);
    goto CPyL13;
CPyL20: ;
    CPy_DecRef(cpy_r_r11.f0);
    CPy_DecRef(cpy_r_r11.f1);
    CPy_DecRef(cpy_r_r11.f2);
    goto CPyL15;
}

PyObject *CPyPy_brownie____get_select_statement(PyObject *self, PyObject *const *args, size_t nargs, PyObject *kwnames) {
    static const char * const kwlist[] = {0};
    static CPyArg_Parser parser = {":_get_select_statement", kwlist, 0};
    if (!CPyArg_ParseStackAndKeywordsNoArgs(args, nargs, kwnames, &parser)) {
        return NULL;
    }
    PyObject *retval = CPyDef_brownie____get_select_statement();
    return retval;
fail: ;
    CPy_AddTraceback("y/_db/brownie.py", "_get_select_statement", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
    return NULL;
}

PyObject *CPyDef_brownie____get_deployment_gen_____mypyc_generator_helper__(PyObject *cpy_r___mypyc_self__, PyObject *cpy_r_type, PyObject *cpy_r_value, PyObject *cpy_r_traceback, PyObject *cpy_r_arg, PyObject **cpy_r_stop_iter_ptr) {
    PyObject *cpy_r_r0;
    PyObject *cpy_r_r1;
    PyObject *cpy_r_r2;
    PyObject *cpy_r_r3;
    PyObject *cpy_r_r4;
    PyObject *cpy_r_r5;
    int32_t cpy_r_r6;
    PyObject *cpy_r_r7;
    char cpy_r_r8;
    PyObject *cpy_r_r9;
    PyObject *cpy_r_r10;
    char cpy_r_r11;
    PyObject *cpy_r_r12;
    char cpy_r_r13;
    PyObject *cpy_r_r14;
    PyObject *cpy_r_r15;
    char cpy_r_r16;
    PyObject *cpy_r_r17;
    char cpy_r_r18;
    PyObject *cpy_r_r19;
    PyObject *cpy_r_r20;
    PyObject *cpy_r_r21;
    PyObject *cpy_r_r22;
    PyObject **cpy_r_r24;
    PyObject *cpy_r_r25;
    PyObject *cpy_r_r26;
    PyObject *cpy_r_r27;
    char cpy_r_r28;
    PyObject *cpy_r_r29;
    char cpy_r_r30;
    PyObject *cpy_r_r31;
    PyObject *cpy_r_r32;
    PyObject *cpy_r_r33;
    PyObject *cpy_r_r34;
    PyObject *cpy_r_r35;
    PyObject **cpy_r_r37;
    PyObject *cpy_r_r38;
    PyObject *cpy_r_r39;
    char cpy_r_r40;
    PyObject *cpy_r_r41;
    PyObject *cpy_r_r42;
    PyObject *cpy_r_r43;
    PyObject *cpy_r_r44;
    PyObject *cpy_r_r45;
    char cpy_r_r46;
    PyObject *cpy_r_r47;
    PyObject *cpy_r_r48;
    char cpy_r_r49;
    PyObject *cpy_r_r50;
    char cpy_r_r51;
    PyObject *cpy_r_r52;
    PyObject *cpy_r_r53;
    PyObject *cpy_r_r54;
    PyObject *cpy_r_r55;
    PyObject *cpy_r_r56;
    char cpy_r_r57;
    PyObject *cpy_r_r58;
    PyObject *cpy_r_r59;
    PyObject *cpy_r_r60;
    PyObject *cpy_r_r61;
    PyObject *cpy_r_r62;
    PyObject *cpy_r_r63;
    PyObject *cpy_r_r64;
    PyObject *cpy_r_r65;
    char cpy_r_r66;
    PyObject **cpy_r_r68;
    PyObject *cpy_r_r69;
    PyObject *cpy_r_r70;
    char cpy_r_r71;
    PyObject *cpy_r_r72;
    PyObject *cpy_r_r73;
    PyObject *cpy_r_r74;
    PyObject *cpy_r_r75;
    PyObject *cpy_r_r76;
    char cpy_r_r77;
    PyObject *cpy_r_r78;
    char cpy_r_r79;
    PyObject *cpy_r_r80;
    char cpy_r_r81;
    tuple_T3OOO cpy_r_r82;
    char cpy_r_r83;
    PyObject **cpy_r_r84;
    PyObject *cpy_r_r85;
    char cpy_r_r86;
    tuple_T3OOO cpy_r_r87;
    tuple_T3OOO cpy_r_r88;
    tuple_T3OOO cpy_r_r89;
    char cpy_r_r90;
    PyObject *cpy_r_r91;
    PyObject *cpy_r_r92;
    PyObject *cpy_r_r93;
    char cpy_r_r94;
    tuple_T3OOO cpy_r_r95;
    char cpy_r_r96;
    PyObject *cpy_r_r97;
    PyObject *cpy_r_r98;
    PyObject *cpy_r_r99;
    char cpy_r_r100;
    PyObject *cpy_r_r101;
    char cpy_r_r102;
    tuple_T3OOO cpy_r_r103;
    tuple_T3OOO cpy_r_r104;
    char cpy_r_r105;
    PyObject *cpy_r_r106;
    int32_t cpy_r_r107;
    char cpy_r_r108;
    char cpy_r_r109;
    tuple_T2CC cpy_r_r110;
    PyObject *cpy_r_r111;
    char cpy_r_r112;
    tuple_T16OOOOOOOOOOOOOOOO cpy_r_r113;
    char cpy_r_r114;
    PyObject *cpy_r_r115;
    PyObject *cpy_r_r116;
    PyObject *cpy_r_r117;
    PyObject *cpy_r_r118;
    PyObject *cpy_r_r119;
    PyObject **cpy_r_r121;
    PyObject *cpy_r_r122;
    PyObject *cpy_r_r123;
    char cpy_r_r124;
    PyObject *cpy_r_r125;
    PyObject *cpy_r_r126;
    PyObject *cpy_r_r127;
    PyObject **cpy_r_r129;
    PyObject *cpy_r_r130;
    PyObject *cpy_r_r131;
    char cpy_r_r132;
    PyObject *cpy_r_r133;
    char cpy_r_r134;
    PyObject *cpy_r_r135;
    char cpy_r_r136;
    char cpy_r_r137;
    PyObject *cpy_r_r138;
    int64_t cpy_r_r139;
    char cpy_r_r140;
    PyObject *cpy_r_r141;
    char cpy_r_r142;
    PyObject *cpy_r_r143;
    CPyTagged cpy_r_r144;
    tuple_T3CIO cpy_r_r145;
    CPyTagged cpy_r_r146;
    char cpy_r_r147;
    char cpy_r_r148;
    PyObject *cpy_r_r149;
    PyObject *cpy_r_r150;
    PyObject *cpy_r_r151;
    char cpy_r_r152;
    char cpy_r_r153;
    PyObject *cpy_r_r154;
    char cpy_r_r155;
    char cpy_r_r156;
    PyObject *cpy_r_r157;
    char cpy_r_r158;
    PyObject *cpy_r_r159;
    PyObject *cpy_r_r160;
    int32_t cpy_r_r161;
    char cpy_r_r162;
    char cpy_r_r163;
    char cpy_r_r164;
    PyObject *cpy_r_r165;
    char cpy_r_r166;
    PyObject *cpy_r_r167;
    PyObject *cpy_r_r168;
    PyObject *cpy_r_r169;
    char cpy_r_r170;
    PyObject *cpy_r_r171;
    PyObject *cpy_r_r172;
    PyObject *cpy_r_r173;
    PyObject **cpy_r_r174;
    PyObject *cpy_r_r175;
    char cpy_r_r176;
    PyObject *cpy_r_r177;
    PyObject *cpy_r_r178;
    char cpy_r_r179;
    PyObject *cpy_r_r180;
    char cpy_r_r181;
    PyObject *cpy_r_r182;
    char cpy_r_r183;
    tuple_T3OOO cpy_r_r184;
    char cpy_r_r185;
    PyObject **cpy_r_r186;
    PyObject *cpy_r_r187;
    char cpy_r_r188;
    tuple_T3OOO cpy_r_r189;
    tuple_T3OOO cpy_r_r190;
    tuple_T3OOO cpy_r_r191;
    char cpy_r_r192;
    PyObject *cpy_r_r193;
    PyObject *cpy_r_r194;
    PyObject *cpy_r_r195;
    PyObject *cpy_r_r196;
    PyObject *cpy_r_r197;
    int32_t cpy_r_r198;
    PyObject *cpy_r_r199;
    char cpy_r_r200;
    char cpy_r_r201;
    PyObject *cpy_r_r202;
    int64_t cpy_r_r203;
    char cpy_r_r204;
    char cpy_r_r205;
    PyObject *cpy_r_r206;
    char cpy_r_r207;
    PyObject *cpy_r_r208;
    char cpy_r_r209;
    PyObject *cpy_r_r210;
    char cpy_r_r211;
    char cpy_r_r212;
    PyObject *cpy_r_r213;
    int64_t cpy_r_r214;
    char cpy_r_r215;
    PyObject *cpy_r_r216;
    char cpy_r_r217;
    PyObject *cpy_r_r218;
    CPyTagged cpy_r_r219;
    tuple_T4CIOO cpy_r_r220;
    CPyTagged cpy_r_r221;
    char cpy_r_r222;
    char cpy_r_r223;
    PyObject *cpy_r_r224;
    PyObject *cpy_r_r225;
    char cpy_r_r226;
    char cpy_r_r227;
    PyObject *cpy_r_r228;
    PyObject *cpy_r_r229;
    PyObject *cpy_r_r230;
    PyObject *cpy_r_r231;
    PyObject *cpy_r_r232;
    int32_t cpy_r_r233;
    char cpy_r_r234;
    PyObject *cpy_r_r235;
    int64_t cpy_r_r236;
    char cpy_r_r237;
    char cpy_r_r238;
    PyObject *cpy_r_r239;
    PyObject *cpy_r_r240;
    PyObject *cpy_r_r241;
    int32_t cpy_r_r242;
    char cpy_r_r243;
    PyObject *cpy_r_r244;
    PyObject *cpy_r_r245;
    PyObject *cpy_r_r246;
    PyObject *cpy_r_r247;
    char cpy_r_r248;
    PyObject *cpy_r_r249;
    PyObject *cpy_r_r250;
    char cpy_r_r251;
    PyObject *cpy_r_r252;
    char cpy_r_r253;
    PyObject *cpy_r_r254;
    PyObject *cpy_r_r255;
    char cpy_r_r256;
    char cpy_r_r257;
    PyObject *cpy_r_r258;
    int64_t cpy_r_r259;
    char cpy_r_r260;
    PyObject *cpy_r_r261;
    char cpy_r_r262;
    PyObject *cpy_r_r263;
    CPyTagged cpy_r_r264;
    tuple_T3CIO cpy_r_r265;
    CPyTagged cpy_r_r266;
    char cpy_r_r267;
    char cpy_r_r268;
    PyObject *cpy_r_r269;
    char cpy_r_r270;
    PyObject *cpy_r_r271;
    PyObject *cpy_r_r272;
    PyObject **cpy_r_r274;
    PyObject *cpy_r_r275;
    CPyTagged cpy_r_r276;
    PyObject *cpy_r_r277;
    PyObject *cpy_r_r278;
    PyObject *cpy_r_r279;
    PyObject *cpy_r_r280;
    PyObject *cpy_r_r281;
    PyObject *cpy_r_r282;
    int32_t cpy_r_r283;
    char cpy_r_r284;
    PyObject *cpy_r_r285;
    int64_t cpy_r_r286;
    char cpy_r_r287;
    char cpy_r_r288;
    PyObject *cpy_r_r289;
    PyObject *cpy_r_r290;
    PyObject *cpy_r_r291;
    int32_t cpy_r_r292;
    char cpy_r_r293;
    PyObject *cpy_r_r294;
    PyObject *cpy_r_r295;
    tuple_T2OO cpy_r_r296;
    PyObject *cpy_r_r297;
    char cpy_r_r298;
    char cpy_r_r299;
    char cpy_r_r300;
    char cpy_r_r301;
    char cpy_r_r302;
    PyObject *cpy_r_r303;
    PyObject *cpy_r_r304;
    char cpy_r_r305;
    PyObject *cpy_r_r306;
    char cpy_r_r307;
    PyObject *cpy_r_r308;
    char cpy_r_r309;
    PyObject *cpy_r_r310;
    char cpy_r_r311;
    cpy_r_r0 = NULL;
    cpy_r_r1 = cpy_r_r0;
    cpy_r_r2 = NULL;
    cpy_r_r3 = cpy_r_r2;
    CPy_XDECREF(cpy_r_r3);
    cpy_r_r4 = NULL;
    cpy_r_r5 = cpy_r_r4;
    cpy_r_r6 = ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_next_label__;
    goto CPyL246;
CPyL1: ;
    cpy_r_r7 = (PyObject *)&_Py_NoneStruct;
    cpy_r_r8 = cpy_r_type != cpy_r_r7;
    if (!cpy_r_r8) goto CPyL4;
    CPyErr_SetObjectAndTraceback(cpy_r_type, cpy_r_value, cpy_r_traceback);
    if (unlikely(!0)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL251;
    }
    CPy_Unreachable();
CPyL4: ;
    cpy_r_r9 = ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__address;
    if (unlikely(cpy_r_r9 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "_get_deployment", "_get_deployment_gen", "address", 155, CPyStatic_brownie___globals);
        goto CPyL251;
    }
    CPy_INCREF(cpy_r_r9);
CPyL5: ;
    cpy_r_r10 = (PyObject *)&_Py_NoneStruct;
    cpy_r_r11 = cpy_r_r9 != cpy_r_r10;
    if (!cpy_r_r11) goto CPyL252;
    if (likely(cpy_r_r9 != Py_None))
        cpy_r_r12 = cpy_r_r9;
    else {
        CPy_TypeErrorTraceback("y/_db/brownie.py", "_get_deployment", 155, CPyStatic_brownie___globals, "str", cpy_r_r9);
        goto CPyL251;
    }
    cpy_r_r13 = CPyStr_IsTrue(cpy_r_r12);
    CPy_DECREF(cpy_r_r12);
    if (!cpy_r_r13) goto CPyL16;
    cpy_r_r14 = ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__alias;
    if (unlikely(cpy_r_r14 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "_get_deployment", "_get_deployment_gen", "alias", 155, CPyStatic_brownie___globals);
        goto CPyL251;
    }
    CPy_INCREF(cpy_r_r14);
CPyL9: ;
    cpy_r_r15 = (PyObject *)&_Py_NoneStruct;
    cpy_r_r16 = cpy_r_r14 != cpy_r_r15;
    if (!cpy_r_r16) goto CPyL253;
    if (likely(cpy_r_r14 != Py_None))
        cpy_r_r17 = cpy_r_r14;
    else {
        CPy_TypeErrorTraceback("y/_db/brownie.py", "_get_deployment", 155, CPyStatic_brownie___globals, "str", cpy_r_r14);
        goto CPyL251;
    }
    cpy_r_r18 = CPyStr_IsTrue(cpy_r_r17);
    CPy_DECREF(cpy_r_r17);
    if (!cpy_r_r18) goto CPyL16;
    cpy_r_r19 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'Passed both params address and alias, should be only one!' */
    cpy_r_r20 = CPyModule_builtins;
    cpy_r_r21 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'ValueError' */
    cpy_r_r22 = CPyObject_GetAttr(cpy_r_r20, cpy_r_r21);
    if (unlikely(cpy_r_r22 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL251;
    }
    PyObject *cpy_r_r23[1] = {cpy_r_r19};
    cpy_r_r24 = (PyObject **)&cpy_r_r23;
    cpy_r_r25 = PyObject_Vectorcall(cpy_r_r22, cpy_r_r24, 1, 0);
    CPy_DECREF(cpy_r_r22);
    if (unlikely(cpy_r_r25 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL251;
    }
    CPy_Raise(cpy_r_r25);
    CPy_DECREF(cpy_r_r25);
    if (unlikely(!0)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL251;
    }
    CPy_Unreachable();
CPyL16: ;
    cpy_r_r26 = ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__address;
    if (unlikely(cpy_r_r26 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "_get_deployment", "_get_deployment_gen", "address", 157, CPyStatic_brownie___globals);
        goto CPyL251;
    }
    CPy_INCREF(cpy_r_r26);
CPyL17: ;
    cpy_r_r27 = (PyObject *)&_Py_NoneStruct;
    cpy_r_r28 = cpy_r_r26 != cpy_r_r27;
    if (!cpy_r_r28) goto CPyL254;
    if (likely(cpy_r_r26 != Py_None))
        cpy_r_r29 = cpy_r_r26;
    else {
        CPy_TypeErrorTraceback("y/_db/brownie.py", "_get_deployment", 157, CPyStatic_brownie___globals, "str", cpy_r_r26);
        goto CPyL251;
    }
    cpy_r_r30 = CPyStr_IsTrue(cpy_r_r29);
    CPy_DECREF(cpy_r_r29);
    if (!cpy_r_r30) goto CPyL30;
    cpy_r_r31 = ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__address;
    if (unlikely(cpy_r_r31 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "_get_deployment", "_get_deployment_gen", "address", 158, CPyStatic_brownie___globals);
        goto CPyL251;
    }
    CPy_INCREF(cpy_r_r31);
CPyL21: ;
    if (likely(cpy_r_r31 != Py_None))
        cpy_r_r32 = cpy_r_r31;
    else {
        CPy_TypeErrorTraceback("y/_db/brownie.py", "_get_deployment", 158, CPyStatic_brownie___globals, "str", cpy_r_r31);
        goto CPyL251;
    }
    cpy_r_r33 = CPyStatic_brownie___globals;
    cpy_r_r34 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* '_resolve_address' */
    cpy_r_r35 = CPyDict_GetItem(cpy_r_r33, cpy_r_r34);
    if (unlikely(cpy_r_r35 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL255;
    }
    PyObject *cpy_r_r36[1] = {cpy_r_r32};
    cpy_r_r37 = (PyObject **)&cpy_r_r36;
    cpy_r_r38 = PyObject_Vectorcall(cpy_r_r35, cpy_r_r37, 1, 0);
    CPy_DECREF(cpy_r_r35);
    if (unlikely(cpy_r_r38 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL255;
    }
    CPy_DECREF(cpy_r_r32);
    if (likely(PyUnicode_Check(cpy_r_r38)))
        cpy_r_r39 = cpy_r_r38;
    else {
        CPy_TypeErrorTraceback("y/_db/brownie.py", "_get_deployment", 158, CPyStatic_brownie___globals, "str", cpy_r_r38);
        goto CPyL251;
    }
    if (((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__address != NULL) {
        CPy_DECREF(((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__address);
    }
    ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__address = cpy_r_r39;
    cpy_r_r40 = 1;
    if (unlikely(!cpy_r_r40)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL251;
    }
    cpy_r_r41 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* " WHERE address='" */
    cpy_r_r42 = ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__address;
    if (unlikely(cpy_r_r42 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "_get_deployment", "_get_deployment_gen", "address", 159, CPyStatic_brownie___globals);
        goto CPyL251;
    }
    CPy_INCREF(cpy_r_r42);
CPyL27: ;
    if (likely(cpy_r_r42 != Py_None))
        cpy_r_r43 = cpy_r_r42;
    else {
        CPy_TypeErrorTraceback("y/_db/brownie.py", "_get_deployment", 159, CPyStatic_brownie___globals, "str", cpy_r_r42);
        goto CPyL251;
    }
    cpy_r_r44 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* "'" */
    cpy_r_r45 = CPyStr_Build(3, cpy_r_r41, cpy_r_r43, cpy_r_r44);
    CPy_DECREF(cpy_r_r43);
    if (unlikely(cpy_r_r45 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL251;
    }
    if (((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__where_clause != NULL) {
        CPy_DECREF(((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__where_clause);
    }
    ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__where_clause = cpy_r_r45;
    cpy_r_r46 = 1;
    if (unlikely(!cpy_r_r46)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL251;
    } else
        goto CPyL38;
CPyL30: ;
    cpy_r_r47 = ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__alias;
    if (unlikely(cpy_r_r47 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "_get_deployment", "_get_deployment_gen", "alias", 160, CPyStatic_brownie___globals);
        goto CPyL251;
    }
    CPy_INCREF(cpy_r_r47);
CPyL31: ;
    cpy_r_r48 = (PyObject *)&_Py_NoneStruct;
    cpy_r_r49 = cpy_r_r47 != cpy_r_r48;
    if (!cpy_r_r49) goto CPyL256;
    if (likely(cpy_r_r47 != Py_None))
        cpy_r_r50 = cpy_r_r47;
    else {
        CPy_TypeErrorTraceback("y/_db/brownie.py", "_get_deployment", 160, CPyStatic_brownie___globals, "str", cpy_r_r47);
        goto CPyL251;
    }
    cpy_r_r51 = CPyStr_IsTrue(cpy_r_r50);
    CPy_DECREF(cpy_r_r50);
    if (!cpy_r_r51) goto CPyL38;
    cpy_r_r52 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* " WHERE alias='" */
    cpy_r_r53 = ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__alias;
    if (unlikely(cpy_r_r53 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "_get_deployment", "_get_deployment_gen", "alias", 161, CPyStatic_brownie___globals);
        goto CPyL251;
    }
    CPy_INCREF(cpy_r_r53);
CPyL35: ;
    if (likely(cpy_r_r53 != Py_None))
        cpy_r_r54 = cpy_r_r53;
    else {
        CPy_TypeErrorTraceback("y/_db/brownie.py", "_get_deployment", 161, CPyStatic_brownie___globals, "str", cpy_r_r53);
        goto CPyL251;
    }
    cpy_r_r55 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* "'" */
    cpy_r_r56 = CPyStr_Build(3, cpy_r_r52, cpy_r_r54, cpy_r_r55);
    CPy_DECREF(cpy_r_r54);
    if (unlikely(cpy_r_r56 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL251;
    }
    if (((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__where_clause != NULL) {
        CPy_DECREF(((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__where_clause);
    }
    ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__where_clause = cpy_r_r56;
    cpy_r_r57 = 1;
    if (unlikely(!cpy_r_r57)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL251;
    }
CPyL38: ;
    cpy_r_r58 = CPyStatic_brownie___globals;
    cpy_r_r59 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* '_get_select_statement' */
    cpy_r_r60 = CPyDict_GetItem(cpy_r_r58, cpy_r_r59);
    if (unlikely(cpy_r_r60 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL76;
    }
    cpy_r_r61 = PyObject_Vectorcall(cpy_r_r60, 0, 0, 0);
    CPy_DECREF(cpy_r_r60);
    if (unlikely(cpy_r_r61 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL76;
    }
    if (likely(PyUnicode_Check(cpy_r_r61)))
        cpy_r_r62 = cpy_r_r61;
    else {
        CPy_TypeErrorTraceback("y/_db/brownie.py", "_get_deployment", 164, CPyStatic_brownie___globals, "str", cpy_r_r61);
        goto CPyL76;
    }
    cpy_r_r63 = ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__where_clause;
    if (unlikely(cpy_r_r63 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "_get_deployment", "_get_deployment_gen", "where_clause", 164, CPyStatic_brownie___globals);
        goto CPyL257;
    }
    CPy_INCREF(cpy_r_r63);
CPyL42: ;
    cpy_r_r64 = PyUnicode_Concat(cpy_r_r62, cpy_r_r63);
    CPy_DECREF(cpy_r_r62);
    CPy_DECREF(cpy_r_r63);
    if (unlikely(cpy_r_r64 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL76;
    }
    cpy_r_r65 = CPyStatic_brownie___fetchone;
    if (unlikely(cpy_r_r65 == NULL)) {
        goto CPyL258;
    } else
        goto CPyL46;
CPyL44: ;
    PyErr_SetString(PyExc_NameError, "value for final name \"fetchone\" was not set");
    cpy_r_r66 = 0;
    if (unlikely(!cpy_r_r66)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL76;
    }
    CPy_Unreachable();
CPyL46: ;
    PyObject *cpy_r_r67[1] = {cpy_r_r64};
    cpy_r_r68 = (PyObject **)&cpy_r_r67;
    cpy_r_r69 = PyObject_Vectorcall(cpy_r_r65, cpy_r_r68, 1, 0);
    if (unlikely(cpy_r_r69 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL259;
    }
    CPy_DECREF(cpy_r_r64);
    cpy_r_r70 = CPy_GetCoro(cpy_r_r69);
    CPy_DECREF(cpy_r_r69);
    if (unlikely(cpy_r_r70 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL76;
    }
    if (((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__42 != NULL) {
        CPy_DECREF(((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__42);
    }
    ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__42 = cpy_r_r70;
    cpy_r_r71 = 1;
    if (unlikely(!cpy_r_r71)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", -1, CPyStatic_brownie___globals);
        goto CPyL76;
    }
    cpy_r_r72 = ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__42;
    if (unlikely(cpy_r_r72 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "_get_deployment", "_get_deployment_gen", "__mypyc_temp__42", -1, CPyStatic_brownie___globals);
        goto CPyL76;
    }
    CPy_INCREF(cpy_r_r72);
CPyL50: ;
    cpy_r_r73 = CPyIter_Next(cpy_r_r72);
    CPy_DECREF(cpy_r_r72);
    if (cpy_r_r73 != NULL) goto CPyL53;
    cpy_r_r74 = CPy_FetchStopIterationValue();
    if (unlikely(cpy_r_r74 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL76;
    }
    cpy_r_r75 = cpy_r_r74;
    cpy_r_r76 = NULL;
    if (((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__42 != NULL) {
        CPy_DECREF(((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__42);
    }
    ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__42 = cpy_r_r76;
    cpy_r_r77 = 1;
    if (unlikely(!cpy_r_r77)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL260;
    } else
        goto CPyL75;
CPyL53: ;
    cpy_r_r78 = cpy_r_r73;
CPyL54: ;
    ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_next_label__ = 1;
    return cpy_r_r78;
CPyL55: ;
    cpy_r_r80 = (PyObject *)&_Py_NoneStruct;
    cpy_r_r81 = cpy_r_type != cpy_r_r80;
    if (!cpy_r_r81) goto CPyL261;
    CPyErr_SetObjectAndTraceback(cpy_r_type, cpy_r_value, cpy_r_traceback);
    if (unlikely(!0)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL59;
    } else
        goto CPyL262;
CPyL57: ;
    CPy_Unreachable();
CPyL58: ;
    CPy_INCREF(cpy_r_arg);
    goto CPyL70;
CPyL59: ;
    cpy_r_r82 = CPy_CatchError();
    if (((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__43.f0 != NULL) {
        CPy_DECREF(((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__43.f0);
        CPy_DECREF(((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__43.f1);
        CPy_DECREF(((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__43.f2);
    }
    ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__43 = cpy_r_r82;
    cpy_r_r83 = 1;
    if (unlikely(!cpy_r_r83)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", -1, CPyStatic_brownie___globals);
        goto CPyL263;
    }
    cpy_r_r84 = (PyObject **)&cpy_r_r1;
    cpy_r_r85 = ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__42;
    if (unlikely(cpy_r_r85 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "_get_deployment", "_get_deployment_gen", "__mypyc_temp__42", -1, CPyStatic_brownie___globals);
        goto CPyL263;
    }
    CPy_INCREF(cpy_r_r85);
CPyL61: ;
    cpy_r_r86 = CPy_YieldFromErrorHandle(cpy_r_r85, cpy_r_r84);
    CPy_DecRef(cpy_r_r85);
    if (unlikely(cpy_r_r86 == 2)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL263;
    }
    if (cpy_r_r86) goto CPyL65;
    cpy_r_r78 = cpy_r_r1;
    cpy_r_r87 = ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__43;
    if (unlikely(cpy_r_r87.f0 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "_get_deployment", "_get_deployment_gen", "__mypyc_temp__43", -1, CPyStatic_brownie___globals);
        goto CPyL264;
    }
    CPy_INCREF(cpy_r_r87.f0);
    CPy_INCREF(cpy_r_r87.f1);
    CPy_INCREF(cpy_r_r87.f2);
CPyL64: ;
    CPy_RestoreExcInfo(cpy_r_r87);
    CPy_DecRef(cpy_r_r87.f0);
    CPy_DecRef(cpy_r_r87.f1);
    CPy_DecRef(cpy_r_r87.f2);
    goto CPyL54;
CPyL65: ;
    cpy_r_r75 = cpy_r_r1;
    cpy_r_r88 = ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__43;
    if (unlikely(cpy_r_r88.f0 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "_get_deployment", "_get_deployment_gen", "__mypyc_temp__43", -1, CPyStatic_brownie___globals);
        goto CPyL265;
    }
    CPy_INCREF(cpy_r_r88.f0);
    CPy_INCREF(cpy_r_r88.f1);
    CPy_INCREF(cpy_r_r88.f2);
CPyL66: ;
    CPy_RestoreExcInfo(cpy_r_r88);
    CPy_DecRef(cpy_r_r88.f0);
    CPy_DecRef(cpy_r_r88.f1);
    CPy_DecRef(cpy_r_r88.f2);
    goto CPyL75;
CPyL67: ;
    cpy_r_r89 = ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__43;
    if (unlikely(cpy_r_r89.f0 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "_get_deployment", "_get_deployment_gen", "__mypyc_temp__43", -1, CPyStatic_brownie___globals);
        goto CPyL76;
    }
    CPy_INCREF(cpy_r_r89.f0);
    CPy_INCREF(cpy_r_r89.f1);
    CPy_INCREF(cpy_r_r89.f2);
CPyL68: ;
    CPy_RestoreExcInfo(cpy_r_r89);
    CPy_DecRef(cpy_r_r89.f0);
    CPy_DecRef(cpy_r_r89.f1);
    CPy_DecRef(cpy_r_r89.f2);
    cpy_r_r90 = CPy_KeepPropagating();
    if (!cpy_r_r90) goto CPyL76;
    CPy_Unreachable();
CPyL70: ;
    cpy_r_r91 = ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__42;
    if (unlikely(cpy_r_r91 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "_get_deployment", "_get_deployment_gen", "__mypyc_temp__42", -1, CPyStatic_brownie___globals);
        goto CPyL266;
    }
    CPy_INCREF(cpy_r_r91);
CPyL71: ;
    cpy_r_r92 = CPyIter_Send(cpy_r_r91, cpy_r_arg);
    CPy_DECREF(cpy_r_r91);
    CPy_DECREF(cpy_r_arg);
    if (cpy_r_r92 == NULL) goto CPyL73;
    cpy_r_r78 = cpy_r_r92;
    goto CPyL54;
CPyL73: ;
    cpy_r_r93 = CPy_FetchStopIterationValue();
    if (unlikely(cpy_r_r93 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL76;
    }
    cpy_r_r75 = cpy_r_r93;
CPyL75: ;
    if (((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__row != NULL) {
        CPy_DECREF(((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__row);
    }
    ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__row = cpy_r_r75;
    cpy_r_r94 = 1;
    if (unlikely(!cpy_r_r94)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
    } else
        goto CPyL87;
CPyL76: ;
    cpy_r_r95 = CPy_CatchError();
    if (((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__44.f0 != NULL) {
        CPy_DECREF(((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__44.f0);
        CPy_DECREF(((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__44.f1);
        CPy_DECREF(((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__44.f2);
    }
    ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__44 = cpy_r_r95;
    cpy_r_r96 = 1;
    if (unlikely(!cpy_r_r96)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", -1, CPyStatic_brownie___globals);
        goto CPyL84;
    }
    cpy_r_r97 = CPyStatic_brownie___globals;
    cpy_r_r98 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'OperationalError' */
    cpy_r_r99 = CPyDict_GetItem(cpy_r_r97, cpy_r_r98);
    if (unlikely(cpy_r_r99 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL84;
    }
    cpy_r_r100 = CPy_ExceptionMatches(cpy_r_r99);
    CPy_DecRef(cpy_r_r99);
    if (!cpy_r_r100) goto CPyL80;
    cpy_r_r101 = Py_None;
    if (((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__row != NULL) {
        CPy_DECREF(((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__row);
    }
    ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__row = cpy_r_r101;
    cpy_r_r102 = 1;
    if (unlikely(!cpy_r_r102)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL84;
    } else
        goto CPyL82;
CPyL80: ;
    CPy_Reraise();
    if (!0) goto CPyL84;
    CPy_Unreachable();
CPyL82: ;
    cpy_r_r103 = ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__44;
    if (unlikely(cpy_r_r103.f0 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "_get_deployment", "_get_deployment_gen", "__mypyc_temp__44", -1, CPyStatic_brownie___globals);
        goto CPyL251;
    }
    CPy_INCREF(cpy_r_r103.f0);
    CPy_INCREF(cpy_r_r103.f1);
    CPy_INCREF(cpy_r_r103.f2);
CPyL83: ;
    CPy_RestoreExcInfo(cpy_r_r103);
    CPy_DecRef(cpy_r_r103.f0);
    CPy_DecRef(cpy_r_r103.f1);
    CPy_DecRef(cpy_r_r103.f2);
    goto CPyL87;
CPyL84: ;
    cpy_r_r104 = ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__44;
    if (unlikely(cpy_r_r104.f0 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "_get_deployment", "_get_deployment_gen", "__mypyc_temp__44", -1, CPyStatic_brownie___globals);
        goto CPyL251;
    }
    CPy_INCREF(cpy_r_r104.f0);
    CPy_INCREF(cpy_r_r104.f1);
    CPy_INCREF(cpy_r_r104.f2);
CPyL85: ;
    CPy_RestoreExcInfo(cpy_r_r104);
    CPy_DecRef(cpy_r_r104.f0);
    CPy_DecRef(cpy_r_r104.f1);
    CPy_DecRef(cpy_r_r104.f2);
    cpy_r_r105 = CPy_KeepPropagating();
    if (!cpy_r_r105) goto CPyL251;
    CPy_Unreachable();
CPyL87: ;
    cpy_r_r106 = ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__row;
    if (unlikely(cpy_r_r106 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "_get_deployment", "_get_deployment_gen", "row", 167, CPyStatic_brownie___globals);
        goto CPyL251;
    }
    CPy_INCREF(cpy_r_r106);
CPyL88: ;
    cpy_r_r107 = PyObject_IsTrue(cpy_r_r106);
    CPy_DECREF(cpy_r_r106);
    cpy_r_r108 = cpy_r_r107 >= 0;
    if (unlikely(!cpy_r_r108)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL251;
    }
    cpy_r_r109 = cpy_r_r107;
    if (cpy_r_r109) goto CPyL95;
    cpy_r_r110.f0 = 1;
    cpy_r_r110.f1 = 1;
    cpy_r_r111 = PyTuple_New(2);
    if (unlikely(cpy_r_r111 == NULL))
        CPyError_OutOfMemory();
    PyObject *__tmp17 = Py_None;
    CPy_INCREF(__tmp17);
    PyTuple_SET_ITEM(cpy_r_r111, 0, __tmp17);
    PyObject *__tmp18 = Py_None;
    CPy_INCREF(__tmp18);
    PyTuple_SET_ITEM(cpy_r_r111, 1, __tmp18);
    ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_next_label__ = -1;
    if (cpy_r_stop_iter_ptr != NULL) goto CPyL94;
    CPyGen_SetStopIterationValue(cpy_r_r111);
    CPy_DECREF(cpy_r_r111);
    if (!0) goto CPyL251;
    CPy_Unreachable();
CPyL94: ;
    *(PyObject * *)cpy_r_stop_iter_ptr = cpy_r_r111;
    return 0;
CPyL95: ;
    cpy_r_r113 = CPyStatic_brownie___SOURCE_KEYS;
    if (likely(cpy_r_r113.f0 != NULL)) goto CPyL98;
    PyErr_SetString(PyExc_NameError, "value for final name \"SOURCE_KEYS\" was not set");
    cpy_r_r114 = 0;
    if (unlikely(!cpy_r_r114)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL251;
    }
    CPy_Unreachable();
CPyL98: ;
    cpy_r_r115 = ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__row;
    if (unlikely(cpy_r_r115 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "_get_deployment", "_get_deployment_gen", "row", 170, CPyStatic_brownie___globals);
        goto CPyL251;
    }
    CPy_INCREF(cpy_r_r115);
CPyL99: ;
    cpy_r_r116 = CPyModule_builtins;
    cpy_r_r117 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'zip' */
    cpy_r_r118 = CPyObject_GetAttr(cpy_r_r116, cpy_r_r117);
    if (unlikely(cpy_r_r118 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL267;
    }
    CPy_INCREF(cpy_r_r113.f0);
    CPy_INCREF(cpy_r_r113.f1);
    CPy_INCREF(cpy_r_r113.f2);
    CPy_INCREF(cpy_r_r113.f3);
    CPy_INCREF(cpy_r_r113.f4);
    CPy_INCREF(cpy_r_r113.f5);
    CPy_INCREF(cpy_r_r113.f6);
    CPy_INCREF(cpy_r_r113.f7);
    CPy_INCREF(cpy_r_r113.f8);
    CPy_INCREF(cpy_r_r113.f9);
    CPy_INCREF(cpy_r_r113.f10);
    CPy_INCREF(cpy_r_r113.f11);
    CPy_INCREF(cpy_r_r113.f12);
    CPy_INCREF(cpy_r_r113.f13);
    CPy_INCREF(cpy_r_r113.f14);
    CPy_INCREF(cpy_r_r113.f15);
    cpy_r_r119 = PyTuple_New(16);
    if (unlikely(cpy_r_r119 == NULL))
        CPyError_OutOfMemory();
    PyObject *__tmp19 = cpy_r_r113.f0;
    PyTuple_SET_ITEM(cpy_r_r119, 0, __tmp19);
    PyObject *__tmp20 = cpy_r_r113.f1;
    PyTuple_SET_ITEM(cpy_r_r119, 1, __tmp20);
    PyObject *__tmp21 = cpy_r_r113.f2;
    PyTuple_SET_ITEM(cpy_r_r119, 2, __tmp21);
    PyObject *__tmp22 = cpy_r_r113.f3;
    PyTuple_SET_ITEM(cpy_r_r119, 3, __tmp22);
    PyObject *__tmp23 = cpy_r_r113.f4;
    PyTuple_SET_ITEM(cpy_r_r119, 4, __tmp23);
    PyObject *__tmp24 = cpy_r_r113.f5;
    PyTuple_SET_ITEM(cpy_r_r119, 5, __tmp24);
    PyObject *__tmp25 = cpy_r_r113.f6;
    PyTuple_SET_ITEM(cpy_r_r119, 6, __tmp25);
    PyObject *__tmp26 = cpy_r_r113.f7;
    PyTuple_SET_ITEM(cpy_r_r119, 7, __tmp26);
    PyObject *__tmp27 = cpy_r_r113.f8;
    PyTuple_SET_ITEM(cpy_r_r119, 8, __tmp27);
    PyObject *__tmp28 = cpy_r_r113.f9;
    PyTuple_SET_ITEM(cpy_r_r119, 9, __tmp28);
    PyObject *__tmp29 = cpy_r_r113.f10;
    PyTuple_SET_ITEM(cpy_r_r119, 10, __tmp29);
    PyObject *__tmp30 = cpy_r_r113.f11;
    PyTuple_SET_ITEM(cpy_r_r119, 11, __tmp30);
    PyObject *__tmp31 = cpy_r_r113.f12;
    PyTuple_SET_ITEM(cpy_r_r119, 12, __tmp31);
    PyObject *__tmp32 = cpy_r_r113.f13;
    PyTuple_SET_ITEM(cpy_r_r119, 13, __tmp32);
    PyObject *__tmp33 = cpy_r_r113.f14;
    PyTuple_SET_ITEM(cpy_r_r119, 14, __tmp33);
    PyObject *__tmp34 = cpy_r_r113.f15;
    PyTuple_SET_ITEM(cpy_r_r119, 15, __tmp34);
    PyObject *cpy_r_r120[2] = {cpy_r_r119, cpy_r_r115};
    cpy_r_r121 = (PyObject **)&cpy_r_r120;
    cpy_r_r122 = PyObject_Vectorcall(cpy_r_r118, cpy_r_r121, 2, 0);
    CPy_DECREF(cpy_r_r118);
    if (unlikely(cpy_r_r122 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL268;
    }
    CPy_DECREF(cpy_r_r119);
    CPy_DECREF(cpy_r_r115);
    cpy_r_r123 = CPyDict_FromAny(cpy_r_r122);
    CPy_DECREF(cpy_r_r122);
    if (unlikely(cpy_r_r123 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL251;
    }
    if (((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__build_json != NULL) {
        CPy_DECREF(((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__build_json);
    }
    ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__build_json = cpy_r_r123;
    cpy_r_r124 = 1;
    if (unlikely(!cpy_r_r124)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL251;
    }
    cpy_r_r125 = ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__build_json;
    if (unlikely(cpy_r_r125 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "_get_deployment", "_get_deployment_gen", "build_json", 171, CPyStatic_brownie___globals);
        goto CPyL251;
    }
    CPy_INCREF(cpy_r_r125);
CPyL104: ;
    cpy_r_r126 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'paths' */
    cpy_r_r127 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'pop' */
    PyObject *cpy_r_r128[2] = {cpy_r_r125, cpy_r_r126};
    cpy_r_r129 = (PyObject **)&cpy_r_r128;
    cpy_r_r130 = PyObject_VectorcallMethod(cpy_r_r127, cpy_r_r129, 9223372036854775810ULL, 0);
    if (unlikely(cpy_r_r130 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL269;
    }
    CPy_DECREF(cpy_r_r125);
    if (likely(PyDict_Check(cpy_r_r130)))
        cpy_r_r131 = cpy_r_r130;
    else {
        CPy_TypeErrorTraceback("y/_db/brownie.py", "_get_deployment", 171, CPyStatic_brownie___globals, "dict", cpy_r_r130);
        goto CPyL251;
    }
    if (((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__path_map != NULL) {
        CPy_DECREF(((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__path_map);
    }
    ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__path_map = cpy_r_r131;
    cpy_r_r132 = 1;
    if (unlikely(!cpy_r_r132)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL251;
    }
    cpy_r_r133 = PyDict_New();
    if (unlikely(cpy_r_r133 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL251;
    }
    if (((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__45 != NULL) {
        CPy_DECREF(((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__45);
    }
    ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__45 = cpy_r_r133;
    cpy_r_r134 = 1;
    if (unlikely(!cpy_r_r134)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", -1, CPyStatic_brownie___globals);
        goto CPyL251;
    }
    cpy_r_r135 = ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__path_map;
    if (unlikely(cpy_r_r135 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "_get_deployment", "_get_deployment_gen", "path_map", 175, CPyStatic_brownie___globals);
        goto CPyL251;
    }
    CPy_INCREF(cpy_r_r135);
CPyL110: ;
    CPy_INCREF(cpy_r_r135);
    if (((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__46 != NULL) {
        CPy_DECREF(((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__46);
    }
    ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__46 = cpy_r_r135;
    cpy_r_r136 = 1;
    if (unlikely(!cpy_r_r136)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", -1, CPyStatic_brownie___globals);
        goto CPyL270;
    }
    ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__47 = 0;
    cpy_r_r137 = 1;
    if (unlikely(!cpy_r_r137)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", -1, CPyStatic_brownie___globals);
        goto CPyL270;
    }
    cpy_r_r138 = ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__46;
    if (unlikely(cpy_r_r138 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "_get_deployment", "_get_deployment_gen", "__mypyc_temp__46", 173, CPyStatic_brownie___globals);
        goto CPyL270;
    }
    CPy_INCREF(cpy_r_r138);
CPyL113: ;
    cpy_r_r139 = PyDict_Size(cpy_r_r138);
    CPy_DECREF(cpy_r_r138);
    ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__48 = cpy_r_r139;
    cpy_r_r140 = 1;
    if (unlikely(!cpy_r_r140)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", -1, CPyStatic_brownie___globals);
        goto CPyL270;
    }
    cpy_r_r141 = CPyDict_GetValuesIter(cpy_r_r135);
    CPy_DECREF(cpy_r_r135);
    if (unlikely(cpy_r_r141 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL251;
    }
    if (((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__49 != NULL) {
        CPy_DECREF(((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__49);
    }
    ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__49 = cpy_r_r141;
    cpy_r_r142 = 1;
    if (unlikely(!cpy_r_r142)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", -1, CPyStatic_brownie___globals);
        goto CPyL251;
    }
CPyL116: ;
    cpy_r_r143 = ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__49;
    if (unlikely(cpy_r_r143 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "_get_deployment", "_get_deployment_gen", "__mypyc_temp__49", 173, CPyStatic_brownie___globals);
        goto CPyL251;
    }
    CPy_INCREF(cpy_r_r143);
CPyL117: ;
    cpy_r_r144 = ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__47;
    if (unlikely(cpy_r_r144 == CPY_INT_TAG)) {
        CPy_AttributeError("y/_db/brownie.py", "_get_deployment", "_get_deployment_gen", "__mypyc_temp__47", 173, CPyStatic_brownie___globals);
        goto CPyL271;
    }
CPyL118: ;
    cpy_r_r145 = CPyDict_NextValue(cpy_r_r143, cpy_r_r144);
    CPy_DECREF(cpy_r_r143);
    cpy_r_r146 = cpy_r_r145.f1;
    ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__47 = cpy_r_r146;
    cpy_r_r147 = 1;
    if (unlikely(!cpy_r_r147)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL272;
    }
    cpy_r_r148 = cpy_r_r145.f0;
    if (!cpy_r_r148) goto CPyL273;
    cpy_r_r149 = cpy_r_r145.f2;
    CPy_INCREF(cpy_r_r149);
    CPy_DECREF(cpy_r_r145.f2);
    cpy_r_r150 = PyObject_GetIter(cpy_r_r149);
    CPy_DECREF(cpy_r_r149);
    if (unlikely(cpy_r_r150 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL251;
    }
    cpy_r_r151 = PyIter_Next(cpy_r_r150);
    if (cpy_r_r151 == NULL) {
        goto CPyL274;
    } else
        goto CPyL124;
CPyL122: ;
    PyErr_SetString(PyExc_ValueError, "not enough values to unpack");
    cpy_r_r152 = 0;
    if (unlikely(!cpy_r_r152)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL251;
    }
    CPy_Unreachable();
CPyL124: ;
    if (((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__val != NULL) {
        CPy_DECREF(((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__val);
    }
    ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__val = cpy_r_r151;
    cpy_r_r153 = 1;
    if (unlikely(!cpy_r_r153)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL275;
    }
    cpy_r_r154 = PyIter_Next(cpy_r_r150);
    if (cpy_r_r154 == NULL) {
        goto CPyL276;
    } else
        goto CPyL128;
CPyL126: ;
    PyErr_SetString(PyExc_ValueError, "not enough values to unpack");
    cpy_r_r155 = 0;
    if (unlikely(!cpy_r_r155)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL251;
    }
    CPy_Unreachable();
CPyL128: ;
    if (((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__source_key != NULL) {
        CPy_DECREF(((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__source_key);
    }
    ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__source_key = cpy_r_r154;
    cpy_r_r156 = 1;
    if (unlikely(!cpy_r_r156)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL275;
    }
    cpy_r_r157 = PyIter_Next(cpy_r_r150);
    CPy_DECREF(cpy_r_r150);
    if (cpy_r_r157 == NULL) {
        goto CPyL132;
    } else
        goto CPyL277;
CPyL130: ;
    PyErr_SetString(PyExc_ValueError, "too many values to unpack");
    cpy_r_r158 = 0;
    if (unlikely(!cpy_r_r158)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL251;
    }
    CPy_Unreachable();
CPyL132: ;
    cpy_r_r159 = ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__source_key;
    if (unlikely(cpy_r_r159 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "_get_deployment", "_get_deployment_gen", "source_key", 176, CPyStatic_brownie___globals);
        goto CPyL251;
    }
    CPy_INCREF(cpy_r_r159);
CPyL133: ;
    cpy_r_r160 = ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__skip_source_keys;
    if (unlikely(cpy_r_r160 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "_get_deployment", "_get_deployment_gen", "skip_source_keys", 176, CPyStatic_brownie___globals);
        goto CPyL278;
    }
    CPy_INCREF(cpy_r_r160);
CPyL134: ;
    cpy_r_r161 = PySequence_Contains(cpy_r_r160, cpy_r_r159);
    CPy_DECREF(cpy_r_r160);
    CPy_DECREF(cpy_r_r159);
    cpy_r_r162 = cpy_r_r161 >= 0;
    if (unlikely(!cpy_r_r162)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL251;
    }
    cpy_r_r163 = cpy_r_r161;
    cpy_r_r164 = cpy_r_r163 ^ 1;
    if (!cpy_r_r164) goto CPyL169;
    cpy_r_r165 = ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__source_key;
    if (unlikely(cpy_r_r165 == NULL)) {
        PyErr_SetString(PyExc_AttributeError, "attribute 'source_key' of '_get_deployment_gen' undefined");
    } else {
        CPy_INCREF(cpy_r_r165);
    }
    if (((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__2_0 != NULL) {
        CPy_DECREF(((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__2_0);
    }
    ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__2_0 = cpy_r_r165;
    cpy_r_r166 = 1;
    if (unlikely(cpy_r_r165 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL251;
    }
CPyL137: ;
    cpy_r_r167 = ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__val;
    if (unlikely(cpy_r_r167 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "_get_deployment", "_get_deployment_gen", "val", 174, CPyStatic_brownie___globals);
        goto CPyL279;
    }
    CPy_INCREF(cpy_r_r167);
CPyL138: ;
    if (likely(PyUnicode_Check(cpy_r_r167)))
        cpy_r_r168 = cpy_r_r167;
    else {
        CPy_TypeErrorTraceback("y/_db/brownie.py", "_get_deployment", 174, CPyStatic_brownie___globals, "str", cpy_r_r167);
        goto CPyL279;
    }
    cpy_r_r169 = CPyDef_brownie_____fetch_source_for_hash(cpy_r_r168);
    CPy_DECREF(cpy_r_r168);
    if (unlikely(cpy_r_r169 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL279;
    }
    if (((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__50 != NULL) {
        CPy_DECREF_NO_IMM(((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__50);
    }
    ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__50 = cpy_r_r169;
    cpy_r_r170 = 1;
    if (unlikely(!cpy_r_r170)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", -1, CPyStatic_brownie___globals);
        goto CPyL279;
    }
    cpy_r_r171 = ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__50;
    if (unlikely(cpy_r_r171 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "_get_deployment", "_get_deployment_gen", "__mypyc_temp__50", -1, CPyStatic_brownie___globals);
        goto CPyL279;
    }
    CPy_INCREF_NO_IMM(cpy_r_r171);
CPyL142: ;
    cpy_r_r172 = (PyObject *)&_Py_NoneStruct;
    cpy_r_r173 = NULL;
    cpy_r_r3 = cpy_r_r173;
    cpy_r_r174 = (PyObject **)&cpy_r_r3;
    cpy_r_r175 = CPyDef_brownie_____fetch_source_for_hash_gen_____mypyc_generator_helper__(cpy_r_r171, cpy_r_r172, cpy_r_r172, cpy_r_r172, cpy_r_r172, cpy_r_r174);
    CPy_DECREF_NO_IMM(cpy_r_r171);
    if (cpy_r_r175 != NULL) goto CPyL280;
    cpy_r_r176 = cpy_r_r3 != 0;
    if (unlikely(!cpy_r_r176)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", -1, CPyStatic_brownie___globals);
        goto CPyL281;
    }
    cpy_r_r177 = cpy_r_r3;
    cpy_r_r178 = NULL;
    if (((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__50 != NULL) {
        CPy_DECREF_NO_IMM(((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__50);
    }
    ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__50 = cpy_r_r178;
    cpy_r_r179 = 1;
    if (unlikely(!cpy_r_r179)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL282;
    } else
        goto CPyL167;
CPyL145: ;
    cpy_r_r180 = cpy_r_r175;
CPyL146: ;
    ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_next_label__ = 2;
    return cpy_r_r180;
CPyL147: ;
    cpy_r_r182 = (PyObject *)&_Py_NoneStruct;
    cpy_r_r183 = cpy_r_type != cpy_r_r182;
    if (!cpy_r_r183) goto CPyL283;
    CPyErr_SetObjectAndTraceback(cpy_r_type, cpy_r_value, cpy_r_traceback);
    if (unlikely(!0)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL151;
    } else
        goto CPyL284;
CPyL149: ;
    CPy_Unreachable();
CPyL150: ;
    CPy_INCREF(cpy_r_arg);
    goto CPyL162;
CPyL151: ;
    cpy_r_r184 = CPy_CatchError();
    if (((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__51.f0 != NULL) {
        CPy_DECREF(((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__51.f0);
        CPy_DECREF(((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__51.f1);
        CPy_DECREF(((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__51.f2);
    }
    ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__51 = cpy_r_r184;
    cpy_r_r185 = 1;
    if (unlikely(!cpy_r_r185)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", -1, CPyStatic_brownie___globals);
        goto CPyL285;
    }
    cpy_r_r186 = (PyObject **)&cpy_r_r5;
    cpy_r_r187 = ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__50;
    if (unlikely(cpy_r_r187 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "_get_deployment", "_get_deployment_gen", "__mypyc_temp__50", -1, CPyStatic_brownie___globals);
        goto CPyL285;
    }
    CPy_INCREF_NO_IMM(cpy_r_r187);
CPyL153: ;
    cpy_r_r188 = CPy_YieldFromErrorHandle(cpy_r_r187, cpy_r_r186);
    CPy_DecRef(cpy_r_r187);
    if (unlikely(cpy_r_r188 == 2)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL285;
    }
    if (cpy_r_r188) {
        goto CPyL157;
    } else
        goto CPyL286;
CPyL155: ;
    cpy_r_r180 = cpy_r_r5;
    cpy_r_r189 = ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__51;
    if (unlikely(cpy_r_r189.f0 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "_get_deployment", "_get_deployment_gen", "__mypyc_temp__51", -1, CPyStatic_brownie___globals);
        goto CPyL287;
    }
    CPy_INCREF(cpy_r_r189.f0);
    CPy_INCREF(cpy_r_r189.f1);
    CPy_INCREF(cpy_r_r189.f2);
CPyL156: ;
    CPy_RestoreExcInfo(cpy_r_r189);
    CPy_DecRef(cpy_r_r189.f0);
    CPy_DecRef(cpy_r_r189.f1);
    CPy_DecRef(cpy_r_r189.f2);
    goto CPyL146;
CPyL157: ;
    cpy_r_r177 = cpy_r_r5;
    cpy_r_r190 = ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__51;
    if (unlikely(cpy_r_r190.f0 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "_get_deployment", "_get_deployment_gen", "__mypyc_temp__51", -1, CPyStatic_brownie___globals);
        goto CPyL288;
    }
    CPy_INCREF(cpy_r_r190.f0);
    CPy_INCREF(cpy_r_r190.f1);
    CPy_INCREF(cpy_r_r190.f2);
CPyL158: ;
    CPy_RestoreExcInfo(cpy_r_r190);
    CPy_DecRef(cpy_r_r190.f0);
    CPy_DecRef(cpy_r_r190.f1);
    CPy_DecRef(cpy_r_r190.f2);
    goto CPyL167;
CPyL159: ;
    cpy_r_r191 = ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__51;
    if (unlikely(cpy_r_r191.f0 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "_get_deployment", "_get_deployment_gen", "__mypyc_temp__51", -1, CPyStatic_brownie___globals);
        goto CPyL251;
    }
    CPy_INCREF(cpy_r_r191.f0);
    CPy_INCREF(cpy_r_r191.f1);
    CPy_INCREF(cpy_r_r191.f2);
CPyL160: ;
    CPy_RestoreExcInfo(cpy_r_r191);
    CPy_DecRef(cpy_r_r191.f0);
    CPy_DecRef(cpy_r_r191.f1);
    CPy_DecRef(cpy_r_r191.f2);
    cpy_r_r192 = CPy_KeepPropagating();
    if (!cpy_r_r192) goto CPyL251;
    CPy_Unreachable();
CPyL162: ;
    cpy_r_r193 = ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__50;
    if (unlikely(cpy_r_r193 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "_get_deployment", "_get_deployment_gen", "__mypyc_temp__50", -1, CPyStatic_brownie___globals);
        goto CPyL289;
    }
    CPy_INCREF_NO_IMM(cpy_r_r193);
CPyL163: ;
    cpy_r_r194 = CPyIter_Send(cpy_r_r193, cpy_r_arg);
    CPy_DECREF_NO_IMM(cpy_r_r193);
    CPy_DECREF(cpy_r_arg);
    if (cpy_r_r194 == NULL) {
        goto CPyL165;
    } else
        goto CPyL290;
CPyL164: ;
    cpy_r_r180 = cpy_r_r194;
    goto CPyL146;
CPyL165: ;
    cpy_r_r195 = CPy_FetchStopIterationValue();
    if (unlikely(cpy_r_r195 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL279;
    }
    cpy_r_r177 = cpy_r_r195;
CPyL167: ;
    cpy_r_r196 = ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__45;
    if (unlikely(cpy_r_r196 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "_get_deployment", "_get_deployment_gen", "__mypyc_temp__45", -1, CPyStatic_brownie___globals);
        goto CPyL282;
    }
    CPy_INCREF(cpy_r_r196);
CPyL168: ;
    cpy_r_r197 = ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__2_0;
    if (unlikely(cpy_r_r197 == NULL)) {
        PyErr_SetString(PyExc_AttributeError, "attribute '__mypyc_temp__2_0' of '_get_deployment_gen' undefined");
    } else {
        CPy_INCREF(cpy_r_r197);
    }
    cpy_r_r198 = PyDict_SetItem(cpy_r_r196, cpy_r_r197, cpy_r_r177);
    CPy_DECREF(cpy_r_r197);
    CPy_DECREF(cpy_r_r196);
    cpy_r_r199 = NULL;
    if (((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__2_0 != NULL) {
        CPy_DECREF(((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__2_0);
    }
    ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__2_0 = cpy_r_r199;
    cpy_r_r200 = 1;
    CPy_DECREF(cpy_r_r177);
    cpy_r_r201 = cpy_r_r198 >= 0;
    if (unlikely(!cpy_r_r201)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL251;
    }
CPyL169: ;
    cpy_r_r202 = ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__46;
    if (unlikely(cpy_r_r202 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "_get_deployment", "_get_deployment_gen", "__mypyc_temp__46", 173, CPyStatic_brownie___globals);
        goto CPyL251;
    }
    CPy_INCREF(cpy_r_r202);
CPyL170: ;
    cpy_r_r203 = ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__48;
    if (unlikely(cpy_r_r203 == -113)) {
        CPy_AttributeError("y/_db/brownie.py", "_get_deployment", "_get_deployment_gen", "__mypyc_temp__48", 173, CPyStatic_brownie___globals);
        goto CPyL291;
    }
CPyL171: ;
    cpy_r_r204 = CPyDict_CheckSize(cpy_r_r202, cpy_r_r203);
    CPy_DECREF(cpy_r_r202);
    if (unlikely(!cpy_r_r204)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL251;
    } else
        goto CPyL116;
CPyL172: ;
    cpy_r_r205 = CPy_NoErrOccurred();
    if (unlikely(!cpy_r_r205)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL251;
    }
    cpy_r_r206 = ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__45;
    if (unlikely(cpy_r_r206 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "_get_deployment", "_get_deployment_gen", "__mypyc_temp__45", -1, CPyStatic_brownie___globals);
        goto CPyL251;
    }
    CPy_INCREF(cpy_r_r206);
CPyL174: ;
    if (((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__sources != NULL) {
        CPy_DECREF(((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__sources);
    }
    ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__sources = cpy_r_r206;
    cpy_r_r207 = 1;
    if (unlikely(!cpy_r_r207)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL251;
    }
    cpy_r_r208 = PyDict_New();
    if (unlikely(cpy_r_r208 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL251;
    }
    if (((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__52 != NULL) {
        CPy_DECREF(((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__52);
    }
    ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__52 = cpy_r_r208;
    cpy_r_r209 = 1;
    if (unlikely(!cpy_r_r209)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", -1, CPyStatic_brownie___globals);
        goto CPyL251;
    }
    cpy_r_r210 = ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__path_map;
    if (unlikely(cpy_r_r210 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "_get_deployment", "_get_deployment_gen", "path_map", 179, CPyStatic_brownie___globals);
        goto CPyL251;
    }
    CPy_INCREF(cpy_r_r210);
CPyL178: ;
    CPy_INCREF(cpy_r_r210);
    if (((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__53 != NULL) {
        CPy_DECREF(((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__53);
    }
    ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__53 = cpy_r_r210;
    cpy_r_r211 = 1;
    if (unlikely(!cpy_r_r211)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", -1, CPyStatic_brownie___globals);
        goto CPyL292;
    }
    ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__54 = 0;
    cpy_r_r212 = 1;
    if (unlikely(!cpy_r_r212)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", -1, CPyStatic_brownie___globals);
        goto CPyL292;
    }
    cpy_r_r213 = ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__53;
    if (unlikely(cpy_r_r213 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "_get_deployment", "_get_deployment_gen", "__mypyc_temp__53", 179, CPyStatic_brownie___globals);
        goto CPyL292;
    }
    CPy_INCREF(cpy_r_r213);
CPyL181: ;
    cpy_r_r214 = PyDict_Size(cpy_r_r213);
    CPy_DECREF(cpy_r_r213);
    ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__55 = cpy_r_r214;
    cpy_r_r215 = 1;
    if (unlikely(!cpy_r_r215)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", -1, CPyStatic_brownie___globals);
        goto CPyL292;
    }
    cpy_r_r216 = CPyDict_GetItemsIter(cpy_r_r210);
    CPy_DECREF(cpy_r_r210);
    if (unlikely(cpy_r_r216 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL251;
    }
    if (((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__56 != NULL) {
        CPy_DECREF(((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__56);
    }
    ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__56 = cpy_r_r216;
    cpy_r_r217 = 1;
    if (unlikely(!cpy_r_r217)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", -1, CPyStatic_brownie___globals);
        goto CPyL251;
    }
CPyL184: ;
    cpy_r_r218 = ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__56;
    if (unlikely(cpy_r_r218 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "_get_deployment", "_get_deployment_gen", "__mypyc_temp__56", 179, CPyStatic_brownie___globals);
        goto CPyL251;
    }
    CPy_INCREF(cpy_r_r218);
CPyL185: ;
    cpy_r_r219 = ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__54;
    if (unlikely(cpy_r_r219 == CPY_INT_TAG)) {
        CPy_AttributeError("y/_db/brownie.py", "_get_deployment", "_get_deployment_gen", "__mypyc_temp__54", 179, CPyStatic_brownie___globals);
        goto CPyL293;
    }
CPyL186: ;
    cpy_r_r220 = CPyDict_NextItem(cpy_r_r218, cpy_r_r219);
    CPy_DECREF(cpy_r_r218);
    cpy_r_r221 = cpy_r_r220.f1;
    ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__54 = cpy_r_r221;
    cpy_r_r222 = 1;
    if (unlikely(!cpy_r_r222)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL294;
    }
    cpy_r_r223 = cpy_r_r220.f0;
    if (!cpy_r_r223) goto CPyL295;
    cpy_r_r224 = cpy_r_r220.f2;
    CPy_INCREF(cpy_r_r224);
    cpy_r_r225 = cpy_r_r220.f3;
    CPy_INCREF(cpy_r_r225);
    CPy_DECREF(cpy_r_r220.f2);
    CPy_DECREF(cpy_r_r220.f3);
    if (((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__k != NULL) {
        CPy_DECREF(((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__k);
    }
    ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__k = cpy_r_r224;
    cpy_r_r226 = 1;
    if (unlikely(!cpy_r_r226)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL296;
    }
    if (((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__v != NULL) {
        CPy_DECREF(((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__v);
    }
    ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__v = cpy_r_r225;
    cpy_r_r227 = 1;
    if (unlikely(!cpy_r_r227)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL251;
    }
    cpy_r_r228 = ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__k;
    if (unlikely(cpy_r_r228 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "_get_deployment", "_get_deployment_gen", "k", 179, CPyStatic_brownie___globals);
        goto CPyL251;
    }
    CPy_INCREF(cpy_r_r228);
CPyL191: ;
    cpy_r_r229 = ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__v;
    if (unlikely(cpy_r_r229 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "_get_deployment", "_get_deployment_gen", "v", 179, CPyStatic_brownie___globals);
        goto CPyL297;
    }
    CPy_INCREF(cpy_r_r229);
CPyL192: ;
    cpy_r_r230 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 1 */
    cpy_r_r231 = PyObject_GetItem(cpy_r_r229, cpy_r_r230);
    CPy_DECREF(cpy_r_r229);
    if (unlikely(cpy_r_r231 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL297;
    }
    cpy_r_r232 = ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__52;
    if (unlikely(cpy_r_r232 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "_get_deployment", "_get_deployment_gen", "__mypyc_temp__52", -1, CPyStatic_brownie___globals);
        goto CPyL298;
    }
    CPy_INCREF(cpy_r_r232);
CPyL194: ;
    cpy_r_r233 = PyDict_SetItem(cpy_r_r232, cpy_r_r228, cpy_r_r231);
    CPy_DECREF(cpy_r_r232);
    CPy_DECREF(cpy_r_r228);
    CPy_DECREF(cpy_r_r231);
    cpy_r_r234 = cpy_r_r233 >= 0;
    if (unlikely(!cpy_r_r234)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL251;
    }
    cpy_r_r235 = ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__53;
    if (unlikely(cpy_r_r235 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "_get_deployment", "_get_deployment_gen", "__mypyc_temp__53", 179, CPyStatic_brownie___globals);
        goto CPyL251;
    }
    CPy_INCREF(cpy_r_r235);
CPyL196: ;
    cpy_r_r236 = ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__55;
    if (unlikely(cpy_r_r236 == -113)) {
        CPy_AttributeError("y/_db/brownie.py", "_get_deployment", "_get_deployment_gen", "__mypyc_temp__55", 179, CPyStatic_brownie___globals);
        goto CPyL299;
    }
CPyL197: ;
    cpy_r_r237 = CPyDict_CheckSize(cpy_r_r235, cpy_r_r236);
    CPy_DECREF(cpy_r_r235);
    if (unlikely(!cpy_r_r237)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL251;
    } else
        goto CPyL184;
CPyL198: ;
    cpy_r_r238 = CPy_NoErrOccurred();
    if (unlikely(!cpy_r_r238)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL251;
    }
    cpy_r_r239 = ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__52;
    if (unlikely(cpy_r_r239 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "_get_deployment", "_get_deployment_gen", "__mypyc_temp__52", -1, CPyStatic_brownie___globals);
        goto CPyL251;
    }
    CPy_INCREF(cpy_r_r239);
CPyL200: ;
    cpy_r_r240 = ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__build_json;
    if (unlikely(cpy_r_r240 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "_get_deployment", "_get_deployment_gen", "build_json", 179, CPyStatic_brownie___globals);
        goto CPyL300;
    }
    CPy_INCREF(cpy_r_r240);
CPyL201: ;
    cpy_r_r241 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'allSourcePaths' */
    cpy_r_r242 = CPyDict_SetItem(cpy_r_r240, cpy_r_r241, cpy_r_r239);
    CPy_DECREF(cpy_r_r240);
    CPy_DECREF(cpy_r_r239);
    cpy_r_r243 = cpy_r_r242 >= 0;
    if (unlikely(!cpy_r_r243)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL251;
    }
    cpy_r_r244 = ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__build_json;
    if (unlikely(cpy_r_r244 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "_get_deployment", "_get_deployment_gen", "build_json", 180, CPyStatic_brownie___globals);
        goto CPyL251;
    }
    CPy_INCREF(cpy_r_r244);
CPyL203: ;
    cpy_r_r245 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'pcMap' */
    cpy_r_r246 = CPyDict_GetWithNone(cpy_r_r244, cpy_r_r245);
    CPy_DECREF(cpy_r_r244);
    if (unlikely(cpy_r_r246 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL251;
    }
    if (PyDict_Check(cpy_r_r246))
        cpy_r_r247 = cpy_r_r246;
    else {
        cpy_r_r247 = NULL;
    }
    if (cpy_r_r247 != NULL) goto __LL35;
    if (cpy_r_r246 == Py_None)
        cpy_r_r247 = cpy_r_r246;
    else {
        cpy_r_r247 = NULL;
    }
    if (cpy_r_r247 != NULL) goto __LL35;
    CPy_TypeErrorTraceback("y/_db/brownie.py", "_get_deployment", 180, CPyStatic_brownie___globals, "dict or None", cpy_r_r246);
    goto CPyL251;
__LL35: ;
    if (((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__pc_map != NULL) {
        CPy_DECREF(((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__pc_map);
    }
    ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__pc_map = cpy_r_r247;
    cpy_r_r248 = 1;
    if (unlikely(!cpy_r_r248)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL251;
    }
    cpy_r_r249 = ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__pc_map;
    if (unlikely(cpy_r_r249 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "_get_deployment", "_get_deployment_gen", "pc_map", 181, CPyStatic_brownie___globals);
        goto CPyL251;
    }
    CPy_INCREF(cpy_r_r249);
CPyL207: ;
    cpy_r_r250 = (PyObject *)&_Py_NoneStruct;
    cpy_r_r251 = cpy_r_r249 != cpy_r_r250;
    CPy_DECREF(cpy_r_r249);
    if (!cpy_r_r251) goto CPyL239;
    cpy_r_r252 = PyDict_New();
    if (unlikely(cpy_r_r252 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL251;
    }
    if (((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__57 != NULL) {
        CPy_DECREF(((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__57);
    }
    ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__57 = cpy_r_r252;
    cpy_r_r253 = 1;
    if (unlikely(!cpy_r_r253)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", -1, CPyStatic_brownie___globals);
        goto CPyL251;
    }
    cpy_r_r254 = ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__pc_map;
    if (unlikely(cpy_r_r254 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "_get_deployment", "_get_deployment_gen", "pc_map", 182, CPyStatic_brownie___globals);
        goto CPyL251;
    }
    CPy_INCREF(cpy_r_r254);
CPyL211: ;
    if (likely(cpy_r_r254 != Py_None))
        cpy_r_r255 = cpy_r_r254;
    else {
        CPy_TypeErrorTraceback("y/_db/brownie.py", "_get_deployment", 182, CPyStatic_brownie___globals, "dict", cpy_r_r254);
        goto CPyL251;
    }
    CPy_INCREF(cpy_r_r255);
    if (((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__58 != NULL) {
        CPy_DECREF(((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__58);
    }
    ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__58 = cpy_r_r255;
    cpy_r_r256 = 1;
    if (unlikely(!cpy_r_r256)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", -1, CPyStatic_brownie___globals);
        goto CPyL301;
    }
    ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__59 = 0;
    cpy_r_r257 = 1;
    if (unlikely(!cpy_r_r257)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", -1, CPyStatic_brownie___globals);
        goto CPyL301;
    }
    cpy_r_r258 = ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__58;
    if (unlikely(cpy_r_r258 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "_get_deployment", "_get_deployment_gen", "__mypyc_temp__58", 182, CPyStatic_brownie___globals);
        goto CPyL301;
    }
    CPy_INCREF(cpy_r_r258);
CPyL215: ;
    cpy_r_r259 = PyDict_Size(cpy_r_r258);
    CPy_DECREF(cpy_r_r258);
    ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__60 = cpy_r_r259;
    cpy_r_r260 = 1;
    if (unlikely(!cpy_r_r260)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", -1, CPyStatic_brownie___globals);
        goto CPyL301;
    }
    cpy_r_r261 = CPyDict_GetKeysIter(cpy_r_r255);
    CPy_DECREF(cpy_r_r255);
    if (unlikely(cpy_r_r261 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL251;
    }
    if (((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__61 != NULL) {
        CPy_DECREF(((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__61);
    }
    ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__61 = cpy_r_r261;
    cpy_r_r262 = 1;
    if (unlikely(!cpy_r_r262)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", -1, CPyStatic_brownie___globals);
        goto CPyL251;
    }
CPyL218: ;
    cpy_r_r263 = ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__61;
    if (unlikely(cpy_r_r263 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "_get_deployment", "_get_deployment_gen", "__mypyc_temp__61", 182, CPyStatic_brownie___globals);
        goto CPyL251;
    }
    CPy_INCREF(cpy_r_r263);
CPyL219: ;
    cpy_r_r264 = ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__59;
    if (unlikely(cpy_r_r264 == CPY_INT_TAG)) {
        CPy_AttributeError("y/_db/brownie.py", "_get_deployment", "_get_deployment_gen", "__mypyc_temp__59", 182, CPyStatic_brownie___globals);
        goto CPyL302;
    }
CPyL220: ;
    cpy_r_r265 = CPyDict_NextKey(cpy_r_r263, cpy_r_r264);
    CPy_DECREF(cpy_r_r263);
    cpy_r_r266 = cpy_r_r265.f1;
    ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__59 = cpy_r_r266;
    cpy_r_r267 = 1;
    if (unlikely(!cpy_r_r267)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL303;
    }
    cpy_r_r268 = cpy_r_r265.f0;
    if (!cpy_r_r268) goto CPyL304;
    cpy_r_r269 = cpy_r_r265.f2;
    CPy_INCREF(cpy_r_r269);
    CPy_DECREF(cpy_r_r265.f2);
    if (((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__key != NULL) {
        CPy_DECREF(((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__key);
    }
    ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__key = cpy_r_r269;
    cpy_r_r270 = 1;
    if (unlikely(!cpy_r_r270)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL251;
    }
    cpy_r_r271 = ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__key;
    if (unlikely(cpy_r_r271 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "_get_deployment", "_get_deployment_gen", "key", 182, CPyStatic_brownie___globals);
        goto CPyL251;
    }
    CPy_INCREF(cpy_r_r271);
CPyL224: ;
    cpy_r_r272 = (PyObject *)&PyLong_Type;
    PyObject *cpy_r_r273[1] = {cpy_r_r271};
    cpy_r_r274 = (PyObject **)&cpy_r_r273;
    cpy_r_r275 = PyObject_Vectorcall(cpy_r_r272, cpy_r_r274, 1, 0);
    if (unlikely(cpy_r_r275 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL305;
    }
    CPy_DECREF(cpy_r_r271);
    if (likely(PyLong_Check(cpy_r_r275)))
        cpy_r_r276 = CPyTagged_FromObject(cpy_r_r275);
    else {
        CPy_TypeError("int", cpy_r_r275); cpy_r_r276 = CPY_INT_TAG;
    }
    CPy_DECREF(cpy_r_r275);
    if (unlikely(cpy_r_r276 == CPY_INT_TAG)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL251;
    }
    cpy_r_r277 = ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__pc_map;
    if (unlikely(cpy_r_r277 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "_get_deployment", "_get_deployment_gen", "pc_map", 182, CPyStatic_brownie___globals);
        goto CPyL306;
    }
    CPy_INCREF(cpy_r_r277);
CPyL227: ;
    if (likely(cpy_r_r277 != Py_None))
        cpy_r_r278 = cpy_r_r277;
    else {
        CPy_TypeErrorTraceback("y/_db/brownie.py", "_get_deployment", 182, CPyStatic_brownie___globals, "dict", cpy_r_r277);
        goto CPyL306;
    }
    cpy_r_r279 = ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__key;
    if (unlikely(cpy_r_r279 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "_get_deployment", "_get_deployment_gen", "key", 182, CPyStatic_brownie___globals);
        goto CPyL307;
    }
    CPy_INCREF(cpy_r_r279);
CPyL229: ;
    cpy_r_r280 = CPyDict_GetItem(cpy_r_r278, cpy_r_r279);
    CPy_DECREF(cpy_r_r278);
    CPy_DECREF(cpy_r_r279);
    if (unlikely(cpy_r_r280 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL306;
    }
    cpy_r_r281 = ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__57;
    if (unlikely(cpy_r_r281 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "_get_deployment", "_get_deployment_gen", "__mypyc_temp__57", -1, CPyStatic_brownie___globals);
        goto CPyL308;
    }
    CPy_INCREF(cpy_r_r281);
CPyL231: ;
    cpy_r_r282 = CPyTagged_StealAsObject(cpy_r_r276);
    cpy_r_r283 = PyDict_SetItem(cpy_r_r281, cpy_r_r282, cpy_r_r280);
    CPy_DECREF(cpy_r_r281);
    CPy_DECREF(cpy_r_r282);
    CPy_DECREF(cpy_r_r280);
    cpy_r_r284 = cpy_r_r283 >= 0;
    if (unlikely(!cpy_r_r284)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL251;
    }
    cpy_r_r285 = ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__58;
    if (unlikely(cpy_r_r285 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "_get_deployment", "_get_deployment_gen", "__mypyc_temp__58", 182, CPyStatic_brownie___globals);
        goto CPyL251;
    }
    CPy_INCREF(cpy_r_r285);
CPyL233: ;
    cpy_r_r286 = ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__60;
    if (unlikely(cpy_r_r286 == -113)) {
        CPy_AttributeError("y/_db/brownie.py", "_get_deployment", "_get_deployment_gen", "__mypyc_temp__60", 182, CPyStatic_brownie___globals);
        goto CPyL309;
    }
CPyL234: ;
    cpy_r_r287 = CPyDict_CheckSize(cpy_r_r285, cpy_r_r286);
    CPy_DECREF(cpy_r_r285);
    if (unlikely(!cpy_r_r287)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL251;
    } else
        goto CPyL218;
CPyL235: ;
    cpy_r_r288 = CPy_NoErrOccurred();
    if (unlikely(!cpy_r_r288)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL251;
    }
    cpy_r_r289 = ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__57;
    if (unlikely(cpy_r_r289 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "_get_deployment", "_get_deployment_gen", "__mypyc_temp__57", -1, CPyStatic_brownie___globals);
        goto CPyL251;
    }
    CPy_INCREF(cpy_r_r289);
CPyL237: ;
    cpy_r_r290 = ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__build_json;
    if (unlikely(cpy_r_r290 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "_get_deployment", "_get_deployment_gen", "build_json", 182, CPyStatic_brownie___globals);
        goto CPyL310;
    }
    CPy_INCREF(cpy_r_r290);
CPyL238: ;
    cpy_r_r291 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'pcMap' */
    cpy_r_r292 = CPyDict_SetItem(cpy_r_r290, cpy_r_r291, cpy_r_r289);
    CPy_DECREF(cpy_r_r290);
    CPy_DECREF(cpy_r_r289);
    cpy_r_r293 = cpy_r_r292 >= 0;
    if (unlikely(!cpy_r_r293)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL251;
    }
CPyL239: ;
    cpy_r_r294 = ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__build_json;
    if (unlikely(cpy_r_r294 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "_get_deployment", "_get_deployment_gen", "build_json", 184, CPyStatic_brownie___globals);
        goto CPyL251;
    }
    CPy_INCREF(cpy_r_r294);
CPyL240: ;
    cpy_r_r295 = ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__sources;
    if (unlikely(cpy_r_r295 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "_get_deployment", "_get_deployment_gen", "sources", 184, CPyStatic_brownie___globals);
        goto CPyL311;
    }
    CPy_INCREF(cpy_r_r295);
CPyL241: ;
    cpy_r_r296.f0 = cpy_r_r294;
    cpy_r_r296.f1 = cpy_r_r295;
    cpy_r_r297 = PyTuple_New(2);
    if (unlikely(cpy_r_r297 == NULL))
        CPyError_OutOfMemory();
    PyObject *__tmp36 = cpy_r_r296.f0;
    PyTuple_SET_ITEM(cpy_r_r297, 0, __tmp36);
    PyObject *__tmp37 = cpy_r_r296.f1;
    PyTuple_SET_ITEM(cpy_r_r297, 1, __tmp37);
    ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_next_label__ = -1;
    if (cpy_r_stop_iter_ptr != NULL) goto CPyL245;
    CPyGen_SetStopIterationValue(cpy_r_r297);
    CPy_DECREF(cpy_r_r297);
    if (!0) goto CPyL251;
    CPy_Unreachable();
CPyL245: ;
    *(PyObject * *)cpy_r_stop_iter_ptr = cpy_r_r297;
    return 0;
CPyL246: ;
    cpy_r_r299 = cpy_r_r6 == 0;
    if (cpy_r_r299) goto CPyL312;
    cpy_r_r300 = cpy_r_r6 == 1;
    if (cpy_r_r300) {
        goto CPyL313;
    } else
        goto CPyL314;
CPyL248: ;
    cpy_r_r301 = cpy_r_r6 == 2;
    if (cpy_r_r301) {
        goto CPyL147;
    } else
        goto CPyL315;
CPyL249: ;
    PyErr_SetNone(PyExc_StopIteration);
    cpy_r_r302 = 0;
    if (unlikely(!cpy_r_r302)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL251;
    }
    CPy_Unreachable();
CPyL251: ;
    cpy_r_r303 = NULL;
    return cpy_r_r303;
CPyL252: ;
    CPy_DECREF(cpy_r_r9);
    goto CPyL16;
CPyL253: ;
    CPy_DECREF(cpy_r_r14);
    goto CPyL16;
CPyL254: ;
    CPy_DECREF(cpy_r_r26);
    goto CPyL30;
CPyL255: ;
    CPy_DecRef(cpy_r_r32);
    goto CPyL251;
CPyL256: ;
    CPy_DECREF(cpy_r_r47);
    goto CPyL38;
CPyL257: ;
    CPy_DecRef(cpy_r_r62);
    goto CPyL76;
CPyL258: ;
    CPy_DecRef(cpy_r_r64);
    goto CPyL44;
CPyL259: ;
    CPy_DecRef(cpy_r_r64);
    goto CPyL76;
CPyL260: ;
    CPy_DecRef(cpy_r_r75);
    goto CPyL76;
CPyL261: ;
    CPy_XDECREF(cpy_r_r1);
    goto CPyL58;
CPyL262: ;
    CPy_XDECREF(cpy_r_r1);
    goto CPyL57;
CPyL263: ;
    CPy_XDecRef(cpy_r_r1);
    goto CPyL67;
CPyL264: ;
    CPy_DecRef(cpy_r_r78);
    goto CPyL67;
CPyL265: ;
    CPy_DecRef(cpy_r_r75);
    goto CPyL67;
CPyL266: ;
    CPy_DecRef(cpy_r_arg);
    goto CPyL76;
CPyL267: ;
    CPy_DecRef(cpy_r_r115);
    goto CPyL251;
CPyL268: ;
    CPy_DecRef(cpy_r_r115);
    CPy_DecRef(cpy_r_r119);
    goto CPyL251;
CPyL269: ;
    CPy_DecRef(cpy_r_r125);
    goto CPyL251;
CPyL270: ;
    CPy_DecRef(cpy_r_r135);
    goto CPyL251;
CPyL271: ;
    CPy_DecRef(cpy_r_r143);
    goto CPyL251;
CPyL272: ;
    CPy_DecRef(cpy_r_r145.f2);
    goto CPyL251;
CPyL273: ;
    CPy_DECREF(cpy_r_r145.f2);
    goto CPyL172;
CPyL274: ;
    CPy_DECREF(cpy_r_r150);
    goto CPyL122;
CPyL275: ;
    CPy_DecRef(cpy_r_r150);
    goto CPyL251;
CPyL276: ;
    CPy_DECREF(cpy_r_r150);
    goto CPyL126;
CPyL277: ;
    CPy_DECREF(cpy_r_r157);
    goto CPyL130;
CPyL278: ;
    CPy_DecRef(cpy_r_r159);
    goto CPyL251;
CPyL279: ;
    goto CPyL251;
CPyL280: ;
    CPy_XDECREF(cpy_r_r3);
    goto CPyL145;
CPyL281: ;
    CPy_XDecRef(cpy_r_r3);
    goto CPyL251;
CPyL282: ;
    CPy_DecRef(cpy_r_r177);
    goto CPyL251;
CPyL283: ;
    CPy_XDECREF(cpy_r_r5);
    goto CPyL150;
CPyL284: ;
    CPy_XDECREF(cpy_r_r5);
    goto CPyL149;
CPyL285: ;
    CPy_XDecRef(cpy_r_r5);
    cpy_r_r304 = NULL;
    if (((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__2_0 != NULL) {
        CPy_DECREF(((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__2_0);
    }
    ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__2_0 = cpy_r_r304;
    cpy_r_r305 = 1;
    goto CPyL159;
CPyL286: ;
    goto CPyL155;
CPyL287: ;
    CPy_DecRef(cpy_r_r180);
    goto CPyL159;
CPyL288: ;
    cpy_r_r306 = NULL;
    if (((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__2_0 != NULL) {
        CPy_DECREF(((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__2_0);
    }
    ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__2_0 = cpy_r_r306;
    cpy_r_r307 = 1;
    CPy_DecRef(cpy_r_r177);
    goto CPyL159;
CPyL289: ;
    CPy_DecRef(cpy_r_arg);
    goto CPyL251;
CPyL290: ;
    goto CPyL164;
CPyL291: ;
    CPy_DecRef(cpy_r_r202);
    goto CPyL251;
CPyL292: ;
    CPy_DecRef(cpy_r_r210);
    goto CPyL251;
CPyL293: ;
    CPy_DecRef(cpy_r_r218);
    goto CPyL251;
CPyL294: ;
    CPy_DecRef(cpy_r_r220.f2);
    CPy_DecRef(cpy_r_r220.f3);
    goto CPyL251;
CPyL295: ;
    CPy_DECREF(cpy_r_r220.f2);
    CPy_DECREF(cpy_r_r220.f3);
    goto CPyL198;
CPyL296: ;
    CPy_DecRef(cpy_r_r225);
    goto CPyL251;
CPyL297: ;
    CPy_DecRef(cpy_r_r228);
    goto CPyL251;
CPyL298: ;
    CPy_DecRef(cpy_r_r228);
    CPy_DecRef(cpy_r_r231);
    goto CPyL251;
CPyL299: ;
    CPy_DecRef(cpy_r_r235);
    goto CPyL251;
CPyL300: ;
    CPy_DecRef(cpy_r_r239);
    goto CPyL251;
CPyL301: ;
    CPy_DecRef(cpy_r_r255);
    goto CPyL251;
CPyL302: ;
    CPy_DecRef(cpy_r_r263);
    goto CPyL251;
CPyL303: ;
    CPy_DecRef(cpy_r_r265.f2);
    goto CPyL251;
CPyL304: ;
    CPy_DECREF(cpy_r_r265.f2);
    goto CPyL235;
CPyL305: ;
    CPy_DecRef(cpy_r_r271);
    goto CPyL251;
CPyL306: ;
    CPyTagged_DecRef(cpy_r_r276);
    goto CPyL251;
CPyL307: ;
    CPyTagged_DecRef(cpy_r_r276);
    CPy_DecRef(cpy_r_r278);
    goto CPyL251;
CPyL308: ;
    CPyTagged_DecRef(cpy_r_r276);
    CPy_DecRef(cpy_r_r280);
    goto CPyL251;
CPyL309: ;
    CPy_DecRef(cpy_r_r285);
    goto CPyL251;
CPyL310: ;
    CPy_DecRef(cpy_r_r289);
    goto CPyL251;
CPyL311: ;
    CPy_DecRef(cpy_r_r294);
    goto CPyL251;
CPyL312: ;
    CPy_XDECREF(cpy_r_r1);
    CPy_XDECREF(cpy_r_r5);
    cpy_r_r308 = NULL;
    if (((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__2_0 != NULL) {
        CPy_DECREF(((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__2_0);
    }
    ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__2_0 = cpy_r_r308;
    cpy_r_r309 = 1;
    goto CPyL1;
CPyL313: ;
    CPy_XDECREF(cpy_r_r5);
    cpy_r_r310 = NULL;
    if (((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__2_0 != NULL) {
        CPy_DECREF(((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__2_0);
    }
    ((y____db___brownie____get_deployment_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__2_0 = cpy_r_r310;
    cpy_r_r311 = 1;
    goto CPyL55;
CPyL314: ;
    CPy_XDECREF(cpy_r_r1);
    goto CPyL248;
CPyL315: ;
    CPy_XDECREF(cpy_r_r5);
    goto CPyL249;
}

PyObject *CPyDef_brownie____get_deployment_gen_____next__(PyObject *cpy_r___mypyc_self__) {
    PyObject *cpy_r_r0;
    PyObject *cpy_r_r1;
    PyObject *cpy_r_r2;
    cpy_r_r0 = (PyObject *)&_Py_NoneStruct;
    cpy_r_r1 = CPyDef_brownie____get_deployment_gen_____mypyc_generator_helper__(cpy_r___mypyc_self__, cpy_r_r0, cpy_r_r0, cpy_r_r0, cpy_r_r0, 0);
    if (cpy_r_r1 == NULL) goto CPyL2;
    return cpy_r_r1;
CPyL2: ;
    cpy_r_r2 = NULL;
    return cpy_r_r2;
}

PyObject *CPyPy_brownie____get_deployment_gen_____next__(PyObject *self, PyObject *const *args, size_t nargs, PyObject *kwnames) {
    PyObject *obj___mypyc_self__ = self;
    static const char * const kwlist[] = {0};
    static CPyArg_Parser parser = {":__next__", kwlist, 0};
    if (!CPyArg_ParseStackAndKeywordsNoArgs(args, nargs, kwnames, &parser)) {
        return NULL;
    }
    PyObject *arg___mypyc_self__;
    if (likely(Py_TYPE(obj___mypyc_self__) == CPyType_brownie____get_deployment_gen))
        arg___mypyc_self__ = obj___mypyc_self__;
    else {
        CPy_TypeError("y._db.brownie._get_deployment_gen", obj___mypyc_self__); 
        goto fail;
    }
    PyObject *retval = CPyDef_brownie____get_deployment_gen_____next__(arg___mypyc_self__);
    return retval;
fail: ;
    CPy_AddTraceback("y/_db/brownie.py", "__next__", -1, CPyStatic_brownie___globals);
    return NULL;
}

PyObject *CPyDef_brownie____get_deployment_gen___send(PyObject *cpy_r___mypyc_self__, PyObject *cpy_r_arg) {
    PyObject *cpy_r_r0;
    PyObject *cpy_r_r1;
    PyObject *cpy_r_r2;
    cpy_r_r0 = (PyObject *)&_Py_NoneStruct;
    cpy_r_r1 = CPyDef_brownie____get_deployment_gen_____mypyc_generator_helper__(cpy_r___mypyc_self__, cpy_r_r0, cpy_r_r0, cpy_r_r0, cpy_r_arg, 0);
    if (cpy_r_r1 == NULL) goto CPyL2;
    return cpy_r_r1;
CPyL2: ;
    cpy_r_r2 = NULL;
    return cpy_r_r2;
}

PyObject *CPyPy_brownie____get_deployment_gen___send(PyObject *self, PyObject *const *args, size_t nargs, PyObject *kwnames) {
    PyObject *obj___mypyc_self__ = self;
    static const char * const kwlist[] = {"arg", 0};
    static CPyArg_Parser parser = {"O:send", kwlist, 0};
    PyObject *obj_arg;
    if (!CPyArg_ParseStackAndKeywordsOneArg(args, nargs, kwnames, &parser, &obj_arg)) {
        return NULL;
    }
    PyObject *arg___mypyc_self__;
    if (likely(Py_TYPE(obj___mypyc_self__) == CPyType_brownie____get_deployment_gen))
        arg___mypyc_self__ = obj___mypyc_self__;
    else {
        CPy_TypeError("y._db.brownie._get_deployment_gen", obj___mypyc_self__); 
        goto fail;
    }
    PyObject *arg_arg = obj_arg;
    PyObject *retval = CPyDef_brownie____get_deployment_gen___send(arg___mypyc_self__, arg_arg);
    return retval;
fail: ;
    CPy_AddTraceback("y/_db/brownie.py", "send", -1, CPyStatic_brownie___globals);
    return NULL;
}

PyObject *CPyDef_brownie____get_deployment_gen_____iter__(PyObject *cpy_r___mypyc_self__) {
    CPy_INCREF_NO_IMM(cpy_r___mypyc_self__);
    return cpy_r___mypyc_self__;
}

PyObject *CPyPy_brownie____get_deployment_gen_____iter__(PyObject *self, PyObject *const *args, size_t nargs, PyObject *kwnames) {
    PyObject *obj___mypyc_self__ = self;
    static const char * const kwlist[] = {0};
    static CPyArg_Parser parser = {":__iter__", kwlist, 0};
    if (!CPyArg_ParseStackAndKeywordsNoArgs(args, nargs, kwnames, &parser)) {
        return NULL;
    }
    PyObject *arg___mypyc_self__;
    if (likely(Py_TYPE(obj___mypyc_self__) == CPyType_brownie____get_deployment_gen))
        arg___mypyc_self__ = obj___mypyc_self__;
    else {
        CPy_TypeError("y._db.brownie._get_deployment_gen", obj___mypyc_self__); 
        goto fail;
    }
    PyObject *retval = CPyDef_brownie____get_deployment_gen_____iter__(arg___mypyc_self__);
    return retval;
fail: ;
    CPy_AddTraceback("y/_db/brownie.py", "__iter__", -1, CPyStatic_brownie___globals);
    return NULL;
}

PyObject *CPyDef_brownie____get_deployment_gen___throw(PyObject *cpy_r___mypyc_self__, PyObject *cpy_r_type, PyObject *cpy_r_value, PyObject *cpy_r_traceback) {
    PyObject *cpy_r_r0;
    PyObject *cpy_r_r1;
    PyObject *cpy_r_r2;
    cpy_r_r0 = (PyObject *)&_Py_NoneStruct;
    if (cpy_r_value != NULL) goto CPyL7;
    CPy_INCREF(cpy_r_r0);
    cpy_r_value = cpy_r_r0;
CPyL2: ;
    if (cpy_r_traceback != NULL) goto CPyL8;
    CPy_INCREF(cpy_r_r0);
    cpy_r_traceback = cpy_r_r0;
CPyL4: ;
    cpy_r_r1 = CPyDef_brownie____get_deployment_gen_____mypyc_generator_helper__(cpy_r___mypyc_self__, cpy_r_type, cpy_r_value, cpy_r_traceback, cpy_r_r0, 0);
    CPy_DECREF(cpy_r_value);
    CPy_DECREF(cpy_r_traceback);
    if (cpy_r_r1 == NULL) goto CPyL6;
    return cpy_r_r1;
CPyL6: ;
    cpy_r_r2 = NULL;
    return cpy_r_r2;
CPyL7: ;
    CPy_INCREF(cpy_r_value);
    goto CPyL2;
CPyL8: ;
    CPy_INCREF(cpy_r_traceback);
    goto CPyL4;
}

PyObject *CPyPy_brownie____get_deployment_gen___throw(PyObject *self, PyObject *const *args, size_t nargs, PyObject *kwnames) {
    PyObject *obj___mypyc_self__ = self;
    static const char * const kwlist[] = {"type", "value", "traceback", 0};
    static CPyArg_Parser parser = {"O|OO:throw", kwlist, 0};
    PyObject *obj_type;
    PyObject *obj_value = NULL;
    PyObject *obj_traceback = NULL;
    if (!CPyArg_ParseStackAndKeywordsSimple(args, nargs, kwnames, &parser, &obj_type, &obj_value, &obj_traceback)) {
        return NULL;
    }
    PyObject *arg___mypyc_self__;
    if (likely(Py_TYPE(obj___mypyc_self__) == CPyType_brownie____get_deployment_gen))
        arg___mypyc_self__ = obj___mypyc_self__;
    else {
        CPy_TypeError("y._db.brownie._get_deployment_gen", obj___mypyc_self__); 
        goto fail;
    }
    PyObject *arg_type = obj_type;
    PyObject *arg_value;
    if (obj_value == NULL) {
        arg_value = NULL;
    } else {
        arg_value = obj_value; 
    }
    PyObject *arg_traceback;
    if (obj_traceback == NULL) {
        arg_traceback = NULL;
    } else {
        arg_traceback = obj_traceback; 
    }
    PyObject *retval = CPyDef_brownie____get_deployment_gen___throw(arg___mypyc_self__, arg_type, arg_value, arg_traceback);
    return retval;
fail: ;
    CPy_AddTraceback("y/_db/brownie.py", "throw", -1, CPyStatic_brownie___globals);
    return NULL;
}

PyObject *CPyDef_brownie____get_deployment_gen___close(PyObject *cpy_r___mypyc_self__) {
    PyObject *cpy_r_r0;
    PyObject *cpy_r_r1;
    PyObject *cpy_r_r2;
    PyObject *cpy_r_r3;
    PyObject *cpy_r_r4;
    PyObject *cpy_r_r5;
    tuple_T3OOO cpy_r_r6;
    PyObject *cpy_r_r7;
    PyObject *cpy_r_r8;
    PyObject *cpy_r_r9;
    tuple_T2OO cpy_r_r10;
    PyObject *cpy_r_r11;
    char cpy_r_r12;
    PyObject *cpy_r_r13;
    char cpy_r_r14;
    PyObject *cpy_r_r15;
    cpy_r_r0 = CPyModule_builtins;
    cpy_r_r1 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'GeneratorExit' */
    cpy_r_r2 = CPyObject_GetAttr(cpy_r_r0, cpy_r_r1);
    if (cpy_r_r2 == NULL) goto CPyL3;
    cpy_r_r3 = (PyObject *)&_Py_NoneStruct;
    cpy_r_r4 = (PyObject *)&_Py_NoneStruct;
    cpy_r_r5 = CPyDef_brownie____get_deployment_gen___throw(cpy_r___mypyc_self__, cpy_r_r2, cpy_r_r3, cpy_r_r4);
    if (cpy_r_r5 != NULL) goto CPyL11;
CPyL3: ;
    cpy_r_r6 = CPy_CatchError();
    cpy_r_r7 = CPyModule_builtins;
    cpy_r_r8 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'StopIteration' */
    cpy_r_r9 = CPyObject_GetAttr(cpy_r_r7, cpy_r_r8);
    if (cpy_r_r9 == NULL) goto CPyL12;
    cpy_r_r10.f0 = cpy_r_r2;
    cpy_r_r10.f1 = cpy_r_r9;
    cpy_r_r11 = PyTuple_New(2);
    if (unlikely(cpy_r_r11 == NULL))
        CPyError_OutOfMemory();
    PyObject *__tmp38 = cpy_r_r10.f0;
    PyTuple_SET_ITEM(cpy_r_r11, 0, __tmp38);
    PyObject *__tmp39 = cpy_r_r10.f1;
    PyTuple_SET_ITEM(cpy_r_r11, 1, __tmp39);
    cpy_r_r12 = CPy_ExceptionMatches(cpy_r_r11);
    CPy_DECREF(cpy_r_r11);
    if (!cpy_r_r12) goto CPyL13;
    CPy_RestoreExcInfo(cpy_r_r6);
    CPy_DECREF(cpy_r_r6.f0);
    CPy_DECREF(cpy_r_r6.f1);
    CPy_DECREF(cpy_r_r6.f2);
    cpy_r_r13 = (PyObject *)&_Py_NoneStruct;
    CPy_INCREF(cpy_r_r13);
    return cpy_r_r13;
CPyL6: ;
    CPy_Reraise();
    if (!0) goto CPyL10;
    CPy_Unreachable();
CPyL8: ;
    PyErr_SetString(PyExc_RuntimeError, "generator ignored GeneratorExit");
    cpy_r_r14 = 0;
    if (!cpy_r_r14) goto CPyL10;
    CPy_Unreachable();
CPyL10: ;
    cpy_r_r15 = NULL;
    return cpy_r_r15;
CPyL11: ;
    CPy_DECREF(cpy_r_r2);
    CPy_DECREF(cpy_r_r5);
    goto CPyL8;
CPyL12: ;
    CPy_DECREF(cpy_r_r2);
    CPy_DECREF(cpy_r_r6.f0);
    CPy_DECREF(cpy_r_r6.f1);
    CPy_DECREF(cpy_r_r6.f2);
    goto CPyL10;
CPyL13: ;
    CPy_DECREF(cpy_r_r6.f0);
    CPy_DECREF(cpy_r_r6.f1);
    CPy_DECREF(cpy_r_r6.f2);
    goto CPyL6;
}

PyObject *CPyPy_brownie____get_deployment_gen___close(PyObject *self, PyObject *const *args, size_t nargs, PyObject *kwnames) {
    PyObject *obj___mypyc_self__ = self;
    static const char * const kwlist[] = {0};
    static CPyArg_Parser parser = {":close", kwlist, 0};
    if (!CPyArg_ParseStackAndKeywordsNoArgs(args, nargs, kwnames, &parser)) {
        return NULL;
    }
    PyObject *arg___mypyc_self__;
    if (likely(Py_TYPE(obj___mypyc_self__) == CPyType_brownie____get_deployment_gen))
        arg___mypyc_self__ = obj___mypyc_self__;
    else {
        CPy_TypeError("y._db.brownie._get_deployment_gen", obj___mypyc_self__); 
        goto fail;
    }
    PyObject *retval = CPyDef_brownie____get_deployment_gen___close(arg___mypyc_self__);
    return retval;
fail: ;
    CPy_AddTraceback("y/_db/brownie.py", "close", -1, CPyStatic_brownie___globals);
    return NULL;
}

PyObject *CPyDef_brownie____get_deployment_gen_____await__(PyObject *cpy_r___mypyc_self__) {
    CPy_INCREF_NO_IMM(cpy_r___mypyc_self__);
    return cpy_r___mypyc_self__;
}

PyObject *CPyPy_brownie____get_deployment_gen_____await__(PyObject *self, PyObject *const *args, size_t nargs, PyObject *kwnames) {
    PyObject *obj___mypyc_self__ = self;
    static const char * const kwlist[] = {0};
    static CPyArg_Parser parser = {":__await__", kwlist, 0};
    if (!CPyArg_ParseStackAndKeywordsNoArgs(args, nargs, kwnames, &parser)) {
        return NULL;
    }
    PyObject *arg___mypyc_self__;
    if (likely(Py_TYPE(obj___mypyc_self__) == CPyType_brownie____get_deployment_gen))
        arg___mypyc_self__ = obj___mypyc_self__;
    else {
        CPy_TypeError("y._db.brownie._get_deployment_gen", obj___mypyc_self__); 
        goto fail;
    }
    PyObject *retval = CPyDef_brownie____get_deployment_gen_____await__(arg___mypyc_self__);
    return retval;
fail: ;
    CPy_AddTraceback("y/_db/brownie.py", "__await__", -1, CPyStatic_brownie___globals);
    return NULL;
}

PyObject *CPyDef_brownie____get_deployment(PyObject *cpy_r_address, PyObject *cpy_r_alias, PyObject *cpy_r_skip_source_keys) {
    PyObject *cpy_r_r0;
    PyObject *cpy_r_r1;
    PyObject *cpy_r_r2;
    PyObject *cpy_r_r3;
    char cpy_r_r4;
    char cpy_r_r5;
    char cpy_r_r6;
    char cpy_r_r7;
    PyObject *cpy_r_r8;
    if (cpy_r_address != NULL) goto CPyL12;
    cpy_r_r0 = Py_None;
    cpy_r_address = cpy_r_r0;
CPyL2: ;
    if (cpy_r_alias != NULL) goto CPyL13;
    cpy_r_r1 = Py_None;
    cpy_r_alias = cpy_r_r1;
CPyL4: ;
    if (cpy_r_skip_source_keys != NULL) goto CPyL14;
    cpy_r_r2 = CPyStatic_brownie___y____db___brownie____get_deployment___skip_source_keys;
    CPy_INCREF(cpy_r_r2);
    cpy_r_skip_source_keys = cpy_r_r2;
CPyL6: ;
    cpy_r_r3 = CPyDef_brownie____get_deployment_gen();
    if (unlikely(cpy_r_r3 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL15;
    }
    ((y____db___brownie____get_deployment_genObject *)cpy_r_r3)->___mypyc_next_label__ = 0;
    if (((y____db___brownie____get_deployment_genObject *)cpy_r_r3)->___mypyc_generator_attribute__address != NULL) {
        CPy_DECREF(((y____db___brownie____get_deployment_genObject *)cpy_r_r3)->___mypyc_generator_attribute__address);
    }
    ((y____db___brownie____get_deployment_genObject *)cpy_r_r3)->___mypyc_generator_attribute__address = cpy_r_address;
    cpy_r_r5 = 1;
    if (unlikely(!cpy_r_r5)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL16;
    }
    if (((y____db___brownie____get_deployment_genObject *)cpy_r_r3)->___mypyc_generator_attribute__alias != NULL) {
        CPy_DECREF(((y____db___brownie____get_deployment_genObject *)cpy_r_r3)->___mypyc_generator_attribute__alias);
    }
    ((y____db___brownie____get_deployment_genObject *)cpy_r_r3)->___mypyc_generator_attribute__alias = cpy_r_alias;
    cpy_r_r6 = 1;
    if (unlikely(!cpy_r_r6)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL17;
    }
    if (((y____db___brownie____get_deployment_genObject *)cpy_r_r3)->___mypyc_generator_attribute__skip_source_keys != NULL) {
        CPy_DECREF(((y____db___brownie____get_deployment_genObject *)cpy_r_r3)->___mypyc_generator_attribute__skip_source_keys);
    }
    ((y____db___brownie____get_deployment_genObject *)cpy_r_r3)->___mypyc_generator_attribute__skip_source_keys = cpy_r_skip_source_keys;
    cpy_r_r7 = 1;
    if (unlikely(!cpy_r_r7)) {
        CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL18;
    }
    return cpy_r_r3;
CPyL11: ;
    cpy_r_r8 = NULL;
    return cpy_r_r8;
CPyL12: ;
    CPy_INCREF(cpy_r_address);
    goto CPyL2;
CPyL13: ;
    CPy_INCREF(cpy_r_alias);
    goto CPyL4;
CPyL14: ;
    CPy_INCREF(cpy_r_skip_source_keys);
    goto CPyL6;
CPyL15: ;
    CPy_DecRef(cpy_r_address);
    CPy_DecRef(cpy_r_alias);
    CPy_DecRef(cpy_r_skip_source_keys);
    goto CPyL11;
CPyL16: ;
    CPy_DecRef(cpy_r_alias);
    CPy_DecRef(cpy_r_skip_source_keys);
    CPy_DecRef(cpy_r_r3);
    goto CPyL11;
CPyL17: ;
    CPy_DecRef(cpy_r_skip_source_keys);
    CPy_DecRef(cpy_r_r3);
    goto CPyL11;
CPyL18: ;
    CPy_DecRef(cpy_r_r3);
    goto CPyL11;
}

PyObject *CPyPy_brownie____get_deployment(PyObject *self, PyObject *const *args, size_t nargs, PyObject *kwnames) {
    static const char * const kwlist[] = {"address", "alias", "skip_source_keys", 0};
    static CPyArg_Parser parser = {"|OOO:_get_deployment", kwlist, 0};
    PyObject *obj_address = NULL;
    PyObject *obj_alias = NULL;
    PyObject *obj_skip_source_keys = NULL;
    if (!CPyArg_ParseStackAndKeywordsSimple(args, nargs, kwnames, &parser, &obj_address, &obj_alias, &obj_skip_source_keys)) {
        return NULL;
    }
    PyObject *arg_address;
    if (obj_address == NULL) {
        arg_address = NULL;
        goto __LL40;
    }
    if (PyUnicode_Check(obj_address))
        arg_address = obj_address;
    else {
        arg_address = NULL;
    }
    if (arg_address != NULL) goto __LL40;
    if (obj_address == Py_None)
        arg_address = obj_address;
    else {
        arg_address = NULL;
    }
    if (arg_address != NULL) goto __LL40;
    CPy_TypeError("str or None", obj_address); 
    goto fail;
__LL40: ;
    PyObject *arg_alias;
    if (obj_alias == NULL) {
        arg_alias = NULL;
        goto __LL41;
    }
    if (PyUnicode_Check(obj_alias))
        arg_alias = obj_alias;
    else {
        arg_alias = NULL;
    }
    if (arg_alias != NULL) goto __LL41;
    if (obj_alias == Py_None)
        arg_alias = obj_alias;
    else {
        arg_alias = NULL;
    }
    if (arg_alias != NULL) goto __LL41;
    CPy_TypeError("str or None", obj_alias); 
    goto fail;
__LL41: ;
    PyObject *arg_skip_source_keys;
    if (obj_skip_source_keys == NULL) {
        arg_skip_source_keys = NULL;
    } else {
        arg_skip_source_keys = obj_skip_source_keys; 
    }
    PyObject *retval = CPyDef_brownie____get_deployment(arg_address, arg_alias, arg_skip_source_keys);
    return retval;
fail: ;
    CPy_AddTraceback("y/_db/brownie.py", "_get_deployment", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
    return NULL;
}

PyObject *CPyDef_brownie_____fetch_source_for_hash_gen_____mypyc_generator_helper__(PyObject *cpy_r___mypyc_self__, PyObject *cpy_r_type, PyObject *cpy_r_value, PyObject *cpy_r_traceback, PyObject *cpy_r_arg, PyObject **cpy_r_stop_iter_ptr) {
    PyObject *cpy_r_r0;
    PyObject *cpy_r_r1;
    int32_t cpy_r_r2;
    PyObject *cpy_r_r3;
    char cpy_r_r4;
    PyObject *cpy_r_r5;
    PyObject *cpy_r_r6;
    PyObject *cpy_r_r7;
    char cpy_r_r8;
    PyObject **cpy_r_r10;
    PyObject *cpy_r_r11;
    PyObject *cpy_r_r12;
    char cpy_r_r13;
    PyObject *cpy_r_r14;
    PyObject *cpy_r_r15;
    PyObject *cpy_r_r16;
    PyObject *cpy_r_r17;
    PyObject *cpy_r_r18;
    char cpy_r_r19;
    PyObject *cpy_r_r20;
    char cpy_r_r21;
    PyObject *cpy_r_r22;
    char cpy_r_r23;
    tuple_T3OOO cpy_r_r24;
    char cpy_r_r25;
    PyObject **cpy_r_r26;
    PyObject *cpy_r_r27;
    char cpy_r_r28;
    tuple_T3OOO cpy_r_r29;
    tuple_T3OOO cpy_r_r30;
    tuple_T3OOO cpy_r_r31;
    char cpy_r_r32;
    PyObject *cpy_r_r33;
    PyObject *cpy_r_r34;
    PyObject *cpy_r_r35;
    char cpy_r_r36;
    PyObject *cpy_r_r37;
    PyObject *cpy_r_r38;
    PyObject *cpy_r_r39;
    char cpy_r_r40;
    char cpy_r_r41;
    char cpy_r_r42;
    char cpy_r_r43;
    PyObject *cpy_r_r44;
    cpy_r_r0 = NULL;
    cpy_r_r1 = cpy_r_r0;
    cpy_r_r2 = ((y____db___brownie_____fetch_source_for_hash_genObject *)cpy_r___mypyc_self__)->___mypyc_next_label__;
    goto CPyL46;
CPyL1: ;
    cpy_r_r3 = (PyObject *)&_Py_NoneStruct;
    cpy_r_r4 = cpy_r_type != cpy_r_r3;
    if (!cpy_r_r4) goto CPyL4;
    CPyErr_SetObjectAndTraceback(cpy_r_type, cpy_r_value, cpy_r_traceback);
    if (unlikely(!0)) {
        CPy_AddTraceback("y/_db/brownie.py", "__fetch_source_for_hash", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL50;
    }
    CPy_Unreachable();
CPyL4: ;
    cpy_r_r5 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'SELECT source FROM sources WHERE hash=?' */
    cpy_r_r6 = ((y____db___brownie_____fetch_source_for_hash_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__hashval;
    if (unlikely(cpy_r_r6 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "__fetch_source_for_hash", "__fetch_source_for_hash_gen", "hashval", 188, CPyStatic_brownie___globals);
        goto CPyL50;
    }
    CPy_INCREF(cpy_r_r6);
CPyL5: ;
    cpy_r_r7 = CPyStatic_brownie___fetchone;
    if (unlikely(cpy_r_r7 == NULL)) {
        goto CPyL51;
    } else
        goto CPyL8;
CPyL6: ;
    PyErr_SetString(PyExc_NameError, "value for final name \"fetchone\" was not set");
    cpy_r_r8 = 0;
    if (unlikely(!cpy_r_r8)) {
        CPy_AddTraceback("y/_db/brownie.py", "__fetch_source_for_hash", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL50;
    }
    CPy_Unreachable();
CPyL8: ;
    PyObject *cpy_r_r9[2] = {cpy_r_r5, cpy_r_r6};
    cpy_r_r10 = (PyObject **)&cpy_r_r9;
    cpy_r_r11 = PyObject_Vectorcall(cpy_r_r7, cpy_r_r10, 2, 0);
    if (unlikely(cpy_r_r11 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "__fetch_source_for_hash", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL52;
    }
    CPy_DECREF(cpy_r_r6);
    cpy_r_r12 = CPy_GetCoro(cpy_r_r11);
    CPy_DECREF(cpy_r_r11);
    if (unlikely(cpy_r_r12 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "__fetch_source_for_hash", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL50;
    }
    if (((y____db___brownie_____fetch_source_for_hash_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__62 != NULL) {
        CPy_DECREF(((y____db___brownie_____fetch_source_for_hash_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__62);
    }
    ((y____db___brownie_____fetch_source_for_hash_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__62 = cpy_r_r12;
    cpy_r_r13 = 1;
    if (unlikely(!cpy_r_r13)) {
        CPy_AddTraceback("y/_db/brownie.py", "__fetch_source_for_hash", -1, CPyStatic_brownie___globals);
        goto CPyL50;
    }
    cpy_r_r14 = ((y____db___brownie_____fetch_source_for_hash_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__62;
    if (unlikely(cpy_r_r14 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "__fetch_source_for_hash", "__fetch_source_for_hash_gen", "__mypyc_temp__62", -1, CPyStatic_brownie___globals);
        goto CPyL50;
    }
    CPy_INCREF(cpy_r_r14);
CPyL12: ;
    cpy_r_r15 = CPyIter_Next(cpy_r_r14);
    CPy_DECREF(cpy_r_r14);
    if (cpy_r_r15 != NULL) goto CPyL15;
    cpy_r_r16 = CPy_FetchStopIterationValue();
    if (unlikely(cpy_r_r16 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "__fetch_source_for_hash", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL50;
    }
    cpy_r_r17 = cpy_r_r16;
    cpy_r_r18 = NULL;
    if (((y____db___brownie_____fetch_source_for_hash_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__62 != NULL) {
        CPy_DECREF(((y____db___brownie_____fetch_source_for_hash_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__62);
    }
    ((y____db___brownie_____fetch_source_for_hash_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__62 = cpy_r_r18;
    cpy_r_r19 = 1;
    if (unlikely(!cpy_r_r19)) {
        CPy_AddTraceback("y/_db/brownie.py", "__fetch_source_for_hash", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL53;
    } else
        goto CPyL37;
CPyL15: ;
    cpy_r_r20 = cpy_r_r15;
CPyL16: ;
    ((y____db___brownie_____fetch_source_for_hash_genObject *)cpy_r___mypyc_self__)->___mypyc_next_label__ = 1;
    return cpy_r_r20;
CPyL17: ;
    cpy_r_r22 = (PyObject *)&_Py_NoneStruct;
    cpy_r_r23 = cpy_r_type != cpy_r_r22;
    if (!cpy_r_r23) goto CPyL54;
    CPyErr_SetObjectAndTraceback(cpy_r_type, cpy_r_value, cpy_r_traceback);
    if (unlikely(!0)) {
        CPy_AddTraceback("y/_db/brownie.py", "__fetch_source_for_hash", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL21;
    } else
        goto CPyL55;
CPyL19: ;
    CPy_Unreachable();
CPyL20: ;
    CPy_INCREF(cpy_r_arg);
    goto CPyL32;
CPyL21: ;
    cpy_r_r24 = CPy_CatchError();
    if (((y____db___brownie_____fetch_source_for_hash_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__63.f0 != NULL) {
        CPy_DECREF(((y____db___brownie_____fetch_source_for_hash_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__63.f0);
        CPy_DECREF(((y____db___brownie_____fetch_source_for_hash_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__63.f1);
        CPy_DECREF(((y____db___brownie_____fetch_source_for_hash_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__63.f2);
    }
    ((y____db___brownie_____fetch_source_for_hash_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__63 = cpy_r_r24;
    cpy_r_r25 = 1;
    if (unlikely(!cpy_r_r25)) {
        CPy_AddTraceback("y/_db/brownie.py", "__fetch_source_for_hash", -1, CPyStatic_brownie___globals);
        goto CPyL56;
    }
    cpy_r_r26 = (PyObject **)&cpy_r_r1;
    cpy_r_r27 = ((y____db___brownie_____fetch_source_for_hash_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__62;
    if (unlikely(cpy_r_r27 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "__fetch_source_for_hash", "__fetch_source_for_hash_gen", "__mypyc_temp__62", -1, CPyStatic_brownie___globals);
        goto CPyL56;
    }
    CPy_INCREF(cpy_r_r27);
CPyL23: ;
    cpy_r_r28 = CPy_YieldFromErrorHandle(cpy_r_r27, cpy_r_r26);
    CPy_DecRef(cpy_r_r27);
    if (unlikely(cpy_r_r28 == 2)) {
        CPy_AddTraceback("y/_db/brownie.py", "__fetch_source_for_hash", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL56;
    }
    if (cpy_r_r28) goto CPyL27;
    cpy_r_r20 = cpy_r_r1;
    cpy_r_r29 = ((y____db___brownie_____fetch_source_for_hash_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__63;
    if (unlikely(cpy_r_r29.f0 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "__fetch_source_for_hash", "__fetch_source_for_hash_gen", "__mypyc_temp__63", -1, CPyStatic_brownie___globals);
        goto CPyL57;
    }
    CPy_INCREF(cpy_r_r29.f0);
    CPy_INCREF(cpy_r_r29.f1);
    CPy_INCREF(cpy_r_r29.f2);
CPyL26: ;
    CPy_RestoreExcInfo(cpy_r_r29);
    CPy_DecRef(cpy_r_r29.f0);
    CPy_DecRef(cpy_r_r29.f1);
    CPy_DecRef(cpy_r_r29.f2);
    goto CPyL16;
CPyL27: ;
    cpy_r_r17 = cpy_r_r1;
    cpy_r_r30 = ((y____db___brownie_____fetch_source_for_hash_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__63;
    if (unlikely(cpy_r_r30.f0 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "__fetch_source_for_hash", "__fetch_source_for_hash_gen", "__mypyc_temp__63", -1, CPyStatic_brownie___globals);
        goto CPyL58;
    }
    CPy_INCREF(cpy_r_r30.f0);
    CPy_INCREF(cpy_r_r30.f1);
    CPy_INCREF(cpy_r_r30.f2);
CPyL28: ;
    CPy_RestoreExcInfo(cpy_r_r30);
    CPy_DecRef(cpy_r_r30.f0);
    CPy_DecRef(cpy_r_r30.f1);
    CPy_DecRef(cpy_r_r30.f2);
    goto CPyL37;
CPyL29: ;
    cpy_r_r31 = ((y____db___brownie_____fetch_source_for_hash_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__63;
    if (unlikely(cpy_r_r31.f0 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "__fetch_source_for_hash", "__fetch_source_for_hash_gen", "__mypyc_temp__63", -1, CPyStatic_brownie___globals);
        goto CPyL50;
    }
    CPy_INCREF(cpy_r_r31.f0);
    CPy_INCREF(cpy_r_r31.f1);
    CPy_INCREF(cpy_r_r31.f2);
CPyL30: ;
    CPy_RestoreExcInfo(cpy_r_r31);
    CPy_DecRef(cpy_r_r31.f0);
    CPy_DecRef(cpy_r_r31.f1);
    CPy_DecRef(cpy_r_r31.f2);
    cpy_r_r32 = CPy_KeepPropagating();
    if (!cpy_r_r32) goto CPyL50;
    CPy_Unreachable();
CPyL32: ;
    cpy_r_r33 = ((y____db___brownie_____fetch_source_for_hash_genObject *)cpy_r___mypyc_self__)->___mypyc_temp__62;
    if (unlikely(cpy_r_r33 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "__fetch_source_for_hash", "__fetch_source_for_hash_gen", "__mypyc_temp__62", -1, CPyStatic_brownie___globals);
        goto CPyL59;
    }
    CPy_INCREF(cpy_r_r33);
CPyL33: ;
    cpy_r_r34 = CPyIter_Send(cpy_r_r33, cpy_r_arg);
    CPy_DECREF(cpy_r_r33);
    CPy_DECREF(cpy_r_arg);
    if (cpy_r_r34 == NULL) goto CPyL35;
    cpy_r_r20 = cpy_r_r34;
    goto CPyL16;
CPyL35: ;
    cpy_r_r35 = CPy_FetchStopIterationValue();
    if (unlikely(cpy_r_r35 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "__fetch_source_for_hash", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL50;
    }
    cpy_r_r17 = cpy_r_r35;
CPyL37: ;
    if (((y____db___brownie_____fetch_source_for_hash_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__row != NULL) {
        CPy_DECREF(((y____db___brownie_____fetch_source_for_hash_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__row);
    }
    ((y____db___brownie_____fetch_source_for_hash_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__row = cpy_r_r17;
    cpy_r_r36 = 1;
    if (unlikely(!cpy_r_r36)) {
        CPy_AddTraceback("y/_db/brownie.py", "__fetch_source_for_hash", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL50;
    }
    cpy_r_r37 = ((y____db___brownie_____fetch_source_for_hash_genObject *)cpy_r___mypyc_self__)->___mypyc_generator_attribute__row;
    if (unlikely(cpy_r_r37 == NULL)) {
        CPy_AttributeError("y/_db/brownie.py", "__fetch_source_for_hash", "__fetch_source_for_hash_gen", "row", 189, CPyStatic_brownie___globals);
        goto CPyL50;
    }
    CPy_INCREF(cpy_r_r37);
CPyL39: ;
    if (likely(PyTuple_Check(cpy_r_r37)))
        cpy_r_r38 = cpy_r_r37;
    else {
        CPy_TypeErrorTraceback("y/_db/brownie.py", "__fetch_source_for_hash", 189, CPyStatic_brownie___globals, "tuple", cpy_r_r37);
        goto CPyL50;
    }
    cpy_r_r39 = CPySequenceTuple_GetItem(cpy_r_r38, 0);
    CPy_DECREF(cpy_r_r38);
    if (unlikely(cpy_r_r39 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "__fetch_source_for_hash", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL50;
    }
    ((y____db___brownie_____fetch_source_for_hash_genObject *)cpy_r___mypyc_self__)->___mypyc_next_label__ = -1;
    if (cpy_r_stop_iter_ptr != NULL) goto CPyL45;
    CPyGen_SetStopIterationValue(cpy_r_r39);
    CPy_DECREF(cpy_r_r39);
    if (!0) goto CPyL50;
    CPy_Unreachable();
CPyL45: ;
    *(PyObject * *)cpy_r_stop_iter_ptr = cpy_r_r39;
    return 0;
CPyL46: ;
    cpy_r_r41 = cpy_r_r2 == 0;
    if (cpy_r_r41) goto CPyL60;
    cpy_r_r42 = cpy_r_r2 == 1;
    if (cpy_r_r42) {
        goto CPyL17;
    } else
        goto CPyL61;
CPyL48: ;
    PyErr_SetNone(PyExc_StopIteration);
    cpy_r_r43 = 0;
    if (unlikely(!cpy_r_r43)) {
        CPy_AddTraceback("y/_db/brownie.py", "__fetch_source_for_hash", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL50;
    }
    CPy_Unreachable();
CPyL50: ;
    cpy_r_r44 = NULL;
    return cpy_r_r44;
CPyL51: ;
    CPy_DecRef(cpy_r_r6);
    goto CPyL6;
CPyL52: ;
    CPy_DecRef(cpy_r_r6);
    goto CPyL50;
CPyL53: ;
    CPy_DecRef(cpy_r_r17);
    goto CPyL50;
CPyL54: ;
    CPy_XDECREF(cpy_r_r1);
    goto CPyL20;
CPyL55: ;
    CPy_XDECREF(cpy_r_r1);
    goto CPyL19;
CPyL56: ;
    CPy_XDecRef(cpy_r_r1);
    goto CPyL29;
CPyL57: ;
    CPy_DecRef(cpy_r_r20);
    goto CPyL29;
CPyL58: ;
    CPy_DecRef(cpy_r_r17);
    goto CPyL29;
CPyL59: ;
    CPy_DecRef(cpy_r_arg);
    goto CPyL50;
CPyL60: ;
    CPy_XDECREF(cpy_r_r1);
    goto CPyL1;
CPyL61: ;
    CPy_XDECREF(cpy_r_r1);
    goto CPyL48;
}

PyObject *CPyDef_brownie_____fetch_source_for_hash_gen_____next__(PyObject *cpy_r___mypyc_self__) {
    PyObject *cpy_r_r0;
    PyObject *cpy_r_r1;
    PyObject *cpy_r_r2;
    cpy_r_r0 = (PyObject *)&_Py_NoneStruct;
    cpy_r_r1 = CPyDef_brownie_____fetch_source_for_hash_gen_____mypyc_generator_helper__(cpy_r___mypyc_self__, cpy_r_r0, cpy_r_r0, cpy_r_r0, cpy_r_r0, 0);
    if (cpy_r_r1 == NULL) goto CPyL2;
    return cpy_r_r1;
CPyL2: ;
    cpy_r_r2 = NULL;
    return cpy_r_r2;
}

PyObject *CPyPy_brownie_____fetch_source_for_hash_gen_____next__(PyObject *self, PyObject *const *args, size_t nargs, PyObject *kwnames) {
    PyObject *obj___mypyc_self__ = self;
    static const char * const kwlist[] = {0};
    static CPyArg_Parser parser = {":__next__", kwlist, 0};
    if (!CPyArg_ParseStackAndKeywordsNoArgs(args, nargs, kwnames, &parser)) {
        return NULL;
    }
    PyObject *arg___mypyc_self__;
    if (likely(Py_TYPE(obj___mypyc_self__) == CPyType_brownie_____fetch_source_for_hash_gen))
        arg___mypyc_self__ = obj___mypyc_self__;
    else {
        CPy_TypeError("y._db.brownie.__fetch_source_for_hash_gen", obj___mypyc_self__); 
        goto fail;
    }
    PyObject *retval = CPyDef_brownie_____fetch_source_for_hash_gen_____next__(arg___mypyc_self__);
    return retval;
fail: ;
    CPy_AddTraceback("y/_db/brownie.py", "__next__", -1, CPyStatic_brownie___globals);
    return NULL;
}

PyObject *CPyDef_brownie_____fetch_source_for_hash_gen___send(PyObject *cpy_r___mypyc_self__, PyObject *cpy_r_arg) {
    PyObject *cpy_r_r0;
    PyObject *cpy_r_r1;
    PyObject *cpy_r_r2;
    cpy_r_r0 = (PyObject *)&_Py_NoneStruct;
    cpy_r_r1 = CPyDef_brownie_____fetch_source_for_hash_gen_____mypyc_generator_helper__(cpy_r___mypyc_self__, cpy_r_r0, cpy_r_r0, cpy_r_r0, cpy_r_arg, 0);
    if (cpy_r_r1 == NULL) goto CPyL2;
    return cpy_r_r1;
CPyL2: ;
    cpy_r_r2 = NULL;
    return cpy_r_r2;
}

PyObject *CPyPy_brownie_____fetch_source_for_hash_gen___send(PyObject *self, PyObject *const *args, size_t nargs, PyObject *kwnames) {
    PyObject *obj___mypyc_self__ = self;
    static const char * const kwlist[] = {"arg", 0};
    static CPyArg_Parser parser = {"O:send", kwlist, 0};
    PyObject *obj_arg;
    if (!CPyArg_ParseStackAndKeywordsOneArg(args, nargs, kwnames, &parser, &obj_arg)) {
        return NULL;
    }
    PyObject *arg___mypyc_self__;
    if (likely(Py_TYPE(obj___mypyc_self__) == CPyType_brownie_____fetch_source_for_hash_gen))
        arg___mypyc_self__ = obj___mypyc_self__;
    else {
        CPy_TypeError("y._db.brownie.__fetch_source_for_hash_gen", obj___mypyc_self__); 
        goto fail;
    }
    PyObject *arg_arg = obj_arg;
    PyObject *retval = CPyDef_brownie_____fetch_source_for_hash_gen___send(arg___mypyc_self__, arg_arg);
    return retval;
fail: ;
    CPy_AddTraceback("y/_db/brownie.py", "send", -1, CPyStatic_brownie___globals);
    return NULL;
}

PyObject *CPyDef_brownie_____fetch_source_for_hash_gen_____iter__(PyObject *cpy_r___mypyc_self__) {
    CPy_INCREF_NO_IMM(cpy_r___mypyc_self__);
    return cpy_r___mypyc_self__;
}

PyObject *CPyPy_brownie_____fetch_source_for_hash_gen_____iter__(PyObject *self, PyObject *const *args, size_t nargs, PyObject *kwnames) {
    PyObject *obj___mypyc_self__ = self;
    static const char * const kwlist[] = {0};
    static CPyArg_Parser parser = {":__iter__", kwlist, 0};
    if (!CPyArg_ParseStackAndKeywordsNoArgs(args, nargs, kwnames, &parser)) {
        return NULL;
    }
    PyObject *arg___mypyc_self__;
    if (likely(Py_TYPE(obj___mypyc_self__) == CPyType_brownie_____fetch_source_for_hash_gen))
        arg___mypyc_self__ = obj___mypyc_self__;
    else {
        CPy_TypeError("y._db.brownie.__fetch_source_for_hash_gen", obj___mypyc_self__); 
        goto fail;
    }
    PyObject *retval = CPyDef_brownie_____fetch_source_for_hash_gen_____iter__(arg___mypyc_self__);
    return retval;
fail: ;
    CPy_AddTraceback("y/_db/brownie.py", "__iter__", -1, CPyStatic_brownie___globals);
    return NULL;
}

PyObject *CPyDef_brownie_____fetch_source_for_hash_gen___throw(PyObject *cpy_r___mypyc_self__, PyObject *cpy_r_type, PyObject *cpy_r_value, PyObject *cpy_r_traceback) {
    PyObject *cpy_r_r0;
    PyObject *cpy_r_r1;
    PyObject *cpy_r_r2;
    cpy_r_r0 = (PyObject *)&_Py_NoneStruct;
    if (cpy_r_value != NULL) goto CPyL7;
    CPy_INCREF(cpy_r_r0);
    cpy_r_value = cpy_r_r0;
CPyL2: ;
    if (cpy_r_traceback != NULL) goto CPyL8;
    CPy_INCREF(cpy_r_r0);
    cpy_r_traceback = cpy_r_r0;
CPyL4: ;
    cpy_r_r1 = CPyDef_brownie_____fetch_source_for_hash_gen_____mypyc_generator_helper__(cpy_r___mypyc_self__, cpy_r_type, cpy_r_value, cpy_r_traceback, cpy_r_r0, 0);
    CPy_DECREF(cpy_r_value);
    CPy_DECREF(cpy_r_traceback);
    if (cpy_r_r1 == NULL) goto CPyL6;
    return cpy_r_r1;
CPyL6: ;
    cpy_r_r2 = NULL;
    return cpy_r_r2;
CPyL7: ;
    CPy_INCREF(cpy_r_value);
    goto CPyL2;
CPyL8: ;
    CPy_INCREF(cpy_r_traceback);
    goto CPyL4;
}

PyObject *CPyPy_brownie_____fetch_source_for_hash_gen___throw(PyObject *self, PyObject *const *args, size_t nargs, PyObject *kwnames) {
    PyObject *obj___mypyc_self__ = self;
    static const char * const kwlist[] = {"type", "value", "traceback", 0};
    static CPyArg_Parser parser = {"O|OO:throw", kwlist, 0};
    PyObject *obj_type;
    PyObject *obj_value = NULL;
    PyObject *obj_traceback = NULL;
    if (!CPyArg_ParseStackAndKeywordsSimple(args, nargs, kwnames, &parser, &obj_type, &obj_value, &obj_traceback)) {
        return NULL;
    }
    PyObject *arg___mypyc_self__;
    if (likely(Py_TYPE(obj___mypyc_self__) == CPyType_brownie_____fetch_source_for_hash_gen))
        arg___mypyc_self__ = obj___mypyc_self__;
    else {
        CPy_TypeError("y._db.brownie.__fetch_source_for_hash_gen", obj___mypyc_self__); 
        goto fail;
    }
    PyObject *arg_type = obj_type;
    PyObject *arg_value;
    if (obj_value == NULL) {
        arg_value = NULL;
    } else {
        arg_value = obj_value; 
    }
    PyObject *arg_traceback;
    if (obj_traceback == NULL) {
        arg_traceback = NULL;
    } else {
        arg_traceback = obj_traceback; 
    }
    PyObject *retval = CPyDef_brownie_____fetch_source_for_hash_gen___throw(arg___mypyc_self__, arg_type, arg_value, arg_traceback);
    return retval;
fail: ;
    CPy_AddTraceback("y/_db/brownie.py", "throw", -1, CPyStatic_brownie___globals);
    return NULL;
}

PyObject *CPyDef_brownie_____fetch_source_for_hash_gen___close(PyObject *cpy_r___mypyc_self__) {
    PyObject *cpy_r_r0;
    PyObject *cpy_r_r1;
    PyObject *cpy_r_r2;
    PyObject *cpy_r_r3;
    PyObject *cpy_r_r4;
    PyObject *cpy_r_r5;
    tuple_T3OOO cpy_r_r6;
    PyObject *cpy_r_r7;
    PyObject *cpy_r_r8;
    PyObject *cpy_r_r9;
    tuple_T2OO cpy_r_r10;
    PyObject *cpy_r_r11;
    char cpy_r_r12;
    PyObject *cpy_r_r13;
    char cpy_r_r14;
    PyObject *cpy_r_r15;
    cpy_r_r0 = CPyModule_builtins;
    cpy_r_r1 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'GeneratorExit' */
    cpy_r_r2 = CPyObject_GetAttr(cpy_r_r0, cpy_r_r1);
    if (cpy_r_r2 == NULL) goto CPyL3;
    cpy_r_r3 = (PyObject *)&_Py_NoneStruct;
    cpy_r_r4 = (PyObject *)&_Py_NoneStruct;
    cpy_r_r5 = CPyDef_brownie_____fetch_source_for_hash_gen___throw(cpy_r___mypyc_self__, cpy_r_r2, cpy_r_r3, cpy_r_r4);
    if (cpy_r_r5 != NULL) goto CPyL11;
CPyL3: ;
    cpy_r_r6 = CPy_CatchError();
    cpy_r_r7 = CPyModule_builtins;
    cpy_r_r8 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'StopIteration' */
    cpy_r_r9 = CPyObject_GetAttr(cpy_r_r7, cpy_r_r8);
    if (cpy_r_r9 == NULL) goto CPyL12;
    cpy_r_r10.f0 = cpy_r_r2;
    cpy_r_r10.f1 = cpy_r_r9;
    cpy_r_r11 = PyTuple_New(2);
    if (unlikely(cpy_r_r11 == NULL))
        CPyError_OutOfMemory();
    PyObject *__tmp42 = cpy_r_r10.f0;
    PyTuple_SET_ITEM(cpy_r_r11, 0, __tmp42);
    PyObject *__tmp43 = cpy_r_r10.f1;
    PyTuple_SET_ITEM(cpy_r_r11, 1, __tmp43);
    cpy_r_r12 = CPy_ExceptionMatches(cpy_r_r11);
    CPy_DECREF(cpy_r_r11);
    if (!cpy_r_r12) goto CPyL13;
    CPy_RestoreExcInfo(cpy_r_r6);
    CPy_DECREF(cpy_r_r6.f0);
    CPy_DECREF(cpy_r_r6.f1);
    CPy_DECREF(cpy_r_r6.f2);
    cpy_r_r13 = (PyObject *)&_Py_NoneStruct;
    CPy_INCREF(cpy_r_r13);
    return cpy_r_r13;
CPyL6: ;
    CPy_Reraise();
    if (!0) goto CPyL10;
    CPy_Unreachable();
CPyL8: ;
    PyErr_SetString(PyExc_RuntimeError, "generator ignored GeneratorExit");
    cpy_r_r14 = 0;
    if (!cpy_r_r14) goto CPyL10;
    CPy_Unreachable();
CPyL10: ;
    cpy_r_r15 = NULL;
    return cpy_r_r15;
CPyL11: ;
    CPy_DECREF(cpy_r_r2);
    CPy_DECREF(cpy_r_r5);
    goto CPyL8;
CPyL12: ;
    CPy_DECREF(cpy_r_r2);
    CPy_DECREF(cpy_r_r6.f0);
    CPy_DECREF(cpy_r_r6.f1);
    CPy_DECREF(cpy_r_r6.f2);
    goto CPyL10;
CPyL13: ;
    CPy_DECREF(cpy_r_r6.f0);
    CPy_DECREF(cpy_r_r6.f1);
    CPy_DECREF(cpy_r_r6.f2);
    goto CPyL6;
}

PyObject *CPyPy_brownie_____fetch_source_for_hash_gen___close(PyObject *self, PyObject *const *args, size_t nargs, PyObject *kwnames) {
    PyObject *obj___mypyc_self__ = self;
    static const char * const kwlist[] = {0};
    static CPyArg_Parser parser = {":close", kwlist, 0};
    if (!CPyArg_ParseStackAndKeywordsNoArgs(args, nargs, kwnames, &parser)) {
        return NULL;
    }
    PyObject *arg___mypyc_self__;
    if (likely(Py_TYPE(obj___mypyc_self__) == CPyType_brownie_____fetch_source_for_hash_gen))
        arg___mypyc_self__ = obj___mypyc_self__;
    else {
        CPy_TypeError("y._db.brownie.__fetch_source_for_hash_gen", obj___mypyc_self__); 
        goto fail;
    }
    PyObject *retval = CPyDef_brownie_____fetch_source_for_hash_gen___close(arg___mypyc_self__);
    return retval;
fail: ;
    CPy_AddTraceback("y/_db/brownie.py", "close", -1, CPyStatic_brownie___globals);
    return NULL;
}

PyObject *CPyDef_brownie_____fetch_source_for_hash_gen_____await__(PyObject *cpy_r___mypyc_self__) {
    CPy_INCREF_NO_IMM(cpy_r___mypyc_self__);
    return cpy_r___mypyc_self__;
}

PyObject *CPyPy_brownie_____fetch_source_for_hash_gen_____await__(PyObject *self, PyObject *const *args, size_t nargs, PyObject *kwnames) {
    PyObject *obj___mypyc_self__ = self;
    static const char * const kwlist[] = {0};
    static CPyArg_Parser parser = {":__await__", kwlist, 0};
    if (!CPyArg_ParseStackAndKeywordsNoArgs(args, nargs, kwnames, &parser)) {
        return NULL;
    }
    PyObject *arg___mypyc_self__;
    if (likely(Py_TYPE(obj___mypyc_self__) == CPyType_brownie_____fetch_source_for_hash_gen))
        arg___mypyc_self__ = obj___mypyc_self__;
    else {
        CPy_TypeError("y._db.brownie.__fetch_source_for_hash_gen", obj___mypyc_self__); 
        goto fail;
    }
    PyObject *retval = CPyDef_brownie_____fetch_source_for_hash_gen_____await__(arg___mypyc_self__);
    return retval;
fail: ;
    CPy_AddTraceback("y/_db/brownie.py", "__await__", -1, CPyStatic_brownie___globals);
    return NULL;
}

PyObject *CPyDef_brownie_____fetch_source_for_hash(PyObject *cpy_r_hashval) {
    PyObject *cpy_r_r0;
    char cpy_r_r1;
    char cpy_r_r2;
    PyObject *cpy_r_r3;
    cpy_r_r0 = CPyDef_brownie_____fetch_source_for_hash_gen();
    if (unlikely(cpy_r_r0 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "__fetch_source_for_hash", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL3;
    }
    ((y____db___brownie_____fetch_source_for_hash_genObject *)cpy_r_r0)->___mypyc_next_label__ = 0;
    CPy_INCREF(cpy_r_hashval);
    if (((y____db___brownie_____fetch_source_for_hash_genObject *)cpy_r_r0)->___mypyc_generator_attribute__hashval != NULL) {
        CPy_DECREF(((y____db___brownie_____fetch_source_for_hash_genObject *)cpy_r_r0)->___mypyc_generator_attribute__hashval);
    }
    ((y____db___brownie_____fetch_source_for_hash_genObject *)cpy_r_r0)->___mypyc_generator_attribute__hashval = cpy_r_hashval;
    cpy_r_r2 = 1;
    if (unlikely(!cpy_r_r2)) {
        CPy_AddTraceback("y/_db/brownie.py", "__fetch_source_for_hash", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL4;
    }
    return cpy_r_r0;
CPyL3: ;
    cpy_r_r3 = NULL;
    return cpy_r_r3;
CPyL4: ;
    CPy_DecRef(cpy_r_r0);
    goto CPyL3;
}

PyObject *CPyPy_brownie_____fetch_source_for_hash(PyObject *self, PyObject *const *args, size_t nargs, PyObject *kwnames) {
    static const char * const kwlist[] = {"hashval", 0};
    static CPyArg_Parser parser = {"O:__fetch_source_for_hash", kwlist, 0};
    PyObject *obj_hashval;
    if (!CPyArg_ParseStackAndKeywordsOneArg(args, nargs, kwnames, &parser, &obj_hashval)) {
        return NULL;
    }
    PyObject *arg_hashval;
    if (likely(PyUnicode_Check(obj_hashval)))
        arg_hashval = obj_hashval;
    else {
        CPy_TypeError("str", obj_hashval); 
        goto fail;
    }
    PyObject *retval = CPyDef_brownie_____fetch_source_for_hash(arg_hashval);
    return retval;
fail: ;
    CPy_AddTraceback("y/_db/brownie.py", "__fetch_source_for_hash", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
    return NULL;
}

char CPyDef_brownie_____top_level__(void) {
    PyObject *cpy_r_r0;
    PyObject *cpy_r_r1;
    char cpy_r_r2;
    PyObject *cpy_r_r3;
    PyObject *cpy_r_r4;
    PyObject **cpy_r_r5;
    PyObject **cpy_r_r6;
    void *cpy_r_r8;
    void *cpy_r_r10;
    PyObject *cpy_r_r11;
    PyObject *cpy_r_r12;
    PyObject *cpy_r_r13;
    PyObject *cpy_r_r14;
    char cpy_r_r15;
    PyObject *cpy_r_r16;
    PyObject *cpy_r_r17;
    PyObject *cpy_r_r18;
    PyObject *cpy_r_r19;
    PyObject *cpy_r_r20;
    PyObject *cpy_r_r21;
    PyObject *cpy_r_r22;
    PyObject *cpy_r_r23;
    PyObject *cpy_r_r24;
    PyObject *cpy_r_r25;
    PyObject *cpy_r_r26;
    PyObject *cpy_r_r27;
    PyObject **cpy_r_r28;
    void *cpy_r_r30;
    void *cpy_r_r32;
    PyObject *cpy_r_r33;
    PyObject *cpy_r_r34;
    PyObject *cpy_r_r35;
    PyObject *cpy_r_r36;
    char cpy_r_r37;
    PyObject *cpy_r_r38;
    PyObject *cpy_r_r39;
    PyObject *cpy_r_r40;
    PyObject *cpy_r_r41;
    PyObject *cpy_r_r42;
    PyObject *cpy_r_r43;
    PyObject *cpy_r_r44;
    PyObject *cpy_r_r45;
    PyObject *cpy_r_r46;
    PyObject *cpy_r_r47;
    PyObject *cpy_r_r48;
    PyObject *cpy_r_r49;
    PyObject *cpy_r_r50;
    PyObject *cpy_r_r51;
    PyObject *cpy_r_r52;
    PyObject *cpy_r_r53;
    PyObject *cpy_r_r54;
    PyObject *cpy_r_r55;
    PyObject *cpy_r_r56;
    PyObject *cpy_r_r57;
    PyObject *cpy_r_r58;
    PyObject *cpy_r_r59;
    PyObject *cpy_r_r60;
    PyObject *cpy_r_r61;
    PyObject *cpy_r_r62;
    PyObject *cpy_r_r63;
    PyObject *cpy_r_r64;
    PyObject *cpy_r_r65;
    PyObject *cpy_r_r66;
    PyObject *cpy_r_r67;
    PyObject *cpy_r_r68;
    PyObject *cpy_r_r69;
    PyObject *cpy_r_r70;
    PyObject *cpy_r_r71;
    PyObject *cpy_r_r72;
    PyObject *cpy_r_r73;
    PyObject *cpy_r_r74;
    PyObject *cpy_r_r75;
    PyObject *cpy_r_r76;
    PyObject *cpy_r_r77;
    PyObject *cpy_r_r78;
    PyObject *cpy_r_r79;
    PyObject *cpy_r_r80;
    PyObject *cpy_r_r81;
    PyObject *cpy_r_r82;
    PyObject *cpy_r_r83;
    PyObject *cpy_r_r84;
    PyObject *cpy_r_r85;
    PyObject *cpy_r_r86;
    PyObject *cpy_r_r87;
    PyObject *cpy_r_r88;
    PyObject *cpy_r_r89;
    PyObject *cpy_r_r90;
    PyObject *cpy_r_r91;
    PyObject *cpy_r_r92;
    tuple_T16OOOOOOOOOOOOOOOO cpy_r_r93;
    PyObject *cpy_r_r94;
    PyObject *cpy_r_r95;
    PyObject *cpy_r_r96;
    PyObject *cpy_r_r97;
    int32_t cpy_r_r98;
    char cpy_r_r99;
    PyObject *cpy_r_r100;
    PyObject *cpy_r_r101;
    PyObject *cpy_r_r102;
    PyObject *cpy_r_r103;
    PyObject *cpy_r_r104;
    PyObject *cpy_r_r105;
    PyObject *cpy_r_r106;
    tuple_T2OO cpy_r_r107;
    PyObject *cpy_r_r108;
    PyObject *cpy_r_r109;
    PyObject *cpy_r_r110;
    PyObject *cpy_r_r111;
    int32_t cpy_r_r112;
    char cpy_r_r113;
    PyObject *cpy_r_r114;
    PyObject *cpy_r_r115;
    PyObject *cpy_r_r116;
    PyObject *cpy_r_r117;
    PyObject *cpy_r_r118;
    PyObject *cpy_r_r119;
    PyObject *cpy_r_r120;
    PyObject *cpy_r_r121;
    PyObject *cpy_r_r122;
    tuple_T2OO cpy_r_r123;
    PyObject *cpy_r_r124;
    PyObject *cpy_r_r125;
    PyObject *cpy_r_r126;
    PyObject *cpy_r_r127;
    int32_t cpy_r_r128;
    char cpy_r_r129;
    PyObject *cpy_r_r130;
    PyObject *cpy_r_r131;
    PyObject *cpy_r_r132;
    PyObject *cpy_r_r133;
    PyObject *cpy_r_r134;
    PyObject *cpy_r_r135;
    PyObject *cpy_r_r136;
    PyObject *cpy_r_r137;
    PyObject *cpy_r_r138;
    PyObject *cpy_r_r139;
    PyObject *cpy_r_r140;
    PyObject *cpy_r_r141;
    PyObject *cpy_r_r142;
    PyObject *cpy_r_r143;
    PyObject *cpy_r_r144;
    PyObject *cpy_r_r145;
    tuple_T16OOOOOOOOOOOOOOOO cpy_r_r146;
    PyObject *cpy_r_r147;
    PyObject *cpy_r_r148;
    PyObject *cpy_r_r149;
    int32_t cpy_r_r150;
    char cpy_r_r151;
    PyObject *cpy_r_r152;
    PyObject *cpy_r_r153;
    PyObject *cpy_r_r154;
    PyObject *cpy_r_r155;
    PyObject *cpy_r_r156;
    PyObject *cpy_r_r157;
    PyObject *cpy_r_r158;
    PyObject *cpy_r_r159;
    tuple_T8OOOOOOOO cpy_r_r160;
    PyObject *cpy_r_r161;
    PyObject *cpy_r_r162;
    PyObject *cpy_r_r163;
    int32_t cpy_r_r164;
    char cpy_r_r165;
    PyObject *cpy_r_r166;
    PyObject *cpy_r_r167;
    PyObject *cpy_r_r168;
    PyObject *cpy_r_r169;
    PyObject *cpy_r_r170;
    int32_t cpy_r_r171;
    char cpy_r_r172;
    PyObject *cpy_r_r173;
    PyObject *cpy_r_r174;
    PyObject *cpy_r_r175;
    PyObject *cpy_r_r176;
    PyObject *cpy_r_r177;
    int32_t cpy_r_r178;
    char cpy_r_r179;
    PyObject *cpy_r_r180;
    PyObject *cpy_r_r181;
    PyObject *cpy_r_r182;
    PyObject *cpy_r_r183;
    PyObject *cpy_r_r184;
    int32_t cpy_r_r185;
    char cpy_r_r186;
    PyObject *cpy_r_r187;
    PyObject *cpy_r_r188;
    PyObject *cpy_r_r189;
    PyObject *cpy_r_r190;
    PyObject *cpy_r_r191;
    PyObject *cpy_r_r192;
    int32_t cpy_r_r193;
    char cpy_r_r194;
    PyObject *cpy_r_r195;
    PyObject *cpy_r_r196;
    PyObject *cpy_r_r197;
    PyObject *cpy_r_r198;
    char cpy_r_r199;
    PyObject *cpy_r_r200;
    PyObject *cpy_r_r201;
    PyObject *cpy_r_r202;
    PyObject *cpy_r_r203;
    PyObject *cpy_r_r204;
    PyObject *cpy_r_r205;
    int32_t cpy_r_r206;
    char cpy_r_r207;
    PyObject *cpy_r_r208;
    PyObject *cpy_r_r209;
    int32_t cpy_r_r210;
    char cpy_r_r211;
    PyObject *cpy_r_r212;
    PyObject *cpy_r_r213;
    PyObject *cpy_r_r214;
    PyObject *cpy_r_r215;
    PyObject *cpy_r_r216;
    PyObject *cpy_r_r217;
    PyObject **cpy_r_r219;
    PyObject *cpy_r_r220;
    PyObject *cpy_r_r221;
    PyObject *cpy_r_r222;
    PyObject *cpy_r_r223;
    int32_t cpy_r_r224;
    char cpy_r_r225;
    PyObject *cpy_r_r226;
    char cpy_r_r227;
    PyObject *cpy_r_r228;
    PyObject *cpy_r_r229;
    PyObject *cpy_r_r230;
    PyObject *cpy_r_r231;
    PyObject *cpy_r_r232;
    PyObject *cpy_r_r233;
    PyObject **cpy_r_r235;
    PyObject *cpy_r_r236;
    PyObject *cpy_r_r237;
    PyObject *cpy_r_r238;
    PyObject *cpy_r_r239;
    int32_t cpy_r_r240;
    char cpy_r_r241;
    PyObject *cpy_r_r242;
    PyObject *cpy_r_r243;
    PyObject *cpy_r_r244;
    PyObject *cpy_r_r245;
    PyObject *cpy_r_r246;
    PyObject *cpy_r_r247;
    PyObject *cpy_r_r248;
    PyObject **cpy_r_r250;
    PyObject *cpy_r_r251;
    PyObject *cpy_r_r252;
    PyObject **cpy_r_r254;
    PyObject *cpy_r_r255;
    PyObject *cpy_r_r256;
    PyObject *cpy_r_r257;
    int32_t cpy_r_r258;
    char cpy_r_r259;
    tuple_T8OOOOOOOO cpy_r_r260;
    char cpy_r_r261;
    PyObject *cpy_r_r262;
    char cpy_r_r263;
    cpy_r_r0 = CPyModule_builtins;
    cpy_r_r1 = (PyObject *)&_Py_NoneStruct;
    cpy_r_r2 = cpy_r_r0 != cpy_r_r1;
    if (cpy_r_r2) goto CPyL3;
    cpy_r_r3 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'builtins' */
    cpy_r_r4 = PyImport_Import(cpy_r_r3);
    if (unlikely(cpy_r_r4 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "<module>", -1, CPyStatic_brownie___globals);
        goto CPyL66;
    }
    CPyModule_builtins = cpy_r_r4;
    CPy_INCREF(CPyModule_builtins);
    CPy_DECREF(cpy_r_r4);
CPyL3: ;
    cpy_r_r5 = (PyObject **)&CPyModule_hashlib;
    cpy_r_r6 = (PyObject **)&CPyModule_json;
    PyObject **cpy_r_r7[2] = {cpy_r_r5, cpy_r_r6};
    cpy_r_r8 = (void *)&cpy_r_r7;
    int64_t cpy_r_r9[2] = {1, 2};
    cpy_r_r10 = (void *)&cpy_r_r9;
    cpy_r_r11 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* (('hashlib', 'hashlib', 'hashlib'),
                                    ('json', 'json', 'json')) */
    cpy_r_r12 = CPyStatic_brownie___globals;
    cpy_r_r13 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'y/_db/brownie.py' */
    cpy_r_r14 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* '<module>' */
    cpy_r_r15 = CPyImport_ImportMany(cpy_r_r11, cpy_r_r8, cpy_r_r12, cpy_r_r13, cpy_r_r14, cpy_r_r10);
    if (!cpy_r_r15) goto CPyL66;
    cpy_r_r16 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* ('Lock',) */
    cpy_r_r17 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'asyncio' */
    cpy_r_r18 = CPyStatic_brownie___globals;
    cpy_r_r19 = CPyImport_ImportFromMany(cpy_r_r17, cpy_r_r16, cpy_r_r16, cpy_r_r18);
    if (unlikely(cpy_r_r19 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "<module>", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL66;
    }
    CPyModule_asyncio = cpy_r_r19;
    CPy_INCREF(CPyModule_asyncio);
    CPy_DECREF(cpy_r_r19);
    cpy_r_r20 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* ('Path',) */
    cpy_r_r21 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'pathlib' */
    cpy_r_r22 = CPyStatic_brownie___globals;
    cpy_r_r23 = CPyImport_ImportFromMany(cpy_r_r21, cpy_r_r20, cpy_r_r20, cpy_r_r22);
    if (unlikely(cpy_r_r23 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "<module>", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL66;
    }
    CPyModule_pathlib = cpy_r_r23;
    CPy_INCREF(CPyModule_pathlib);
    CPy_DECREF(cpy_r_r23);
    cpy_r_r24 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* ('Any', 'Callable', 'Container', 'Dict', 'Final',
                                    'Literal', 'Optional', 'Tuple', 'cast', 'final') */
    cpy_r_r25 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'typing' */
    cpy_r_r26 = CPyStatic_brownie___globals;
    cpy_r_r27 = CPyImport_ImportFromMany(cpy_r_r25, cpy_r_r24, cpy_r_r24, cpy_r_r26);
    if (unlikely(cpy_r_r27 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "<module>", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL66;
    }
    CPyModule_typing = cpy_r_r27;
    CPy_INCREF(CPyModule_typing);
    CPy_DECREF(cpy_r_r27);
    cpy_r_r28 = (PyObject **)&CPyModule_aiosqlite;
    PyObject **cpy_r_r29[1] = {cpy_r_r28};
    cpy_r_r30 = (void *)&cpy_r_r29;
    int64_t cpy_r_r31[1] = {7};
    cpy_r_r32 = (void *)&cpy_r_r31;
    cpy_r_r33 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* (('aiosqlite', 'aiosqlite', 'aiosqlite'),) */
    cpy_r_r34 = CPyStatic_brownie___globals;
    cpy_r_r35 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'y/_db/brownie.py' */
    cpy_r_r36 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* '<module>' */
    cpy_r_r37 = CPyImport_ImportMany(cpy_r_r33, cpy_r_r30, cpy_r_r34, cpy_r_r35, cpy_r_r36, cpy_r_r32);
    if (!cpy_r_r37) goto CPyL66;
    cpy_r_r38 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* ('SmartProcessingQueue',) */
    cpy_r_r39 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'a_sync' */
    cpy_r_r40 = CPyStatic_brownie___globals;
    cpy_r_r41 = CPyImport_ImportFromMany(cpy_r_r39, cpy_r_r38, cpy_r_r38, cpy_r_r40);
    if (unlikely(cpy_r_r41 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "<module>", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL66;
    }
    CPyModule_a_sync = cpy_r_r41;
    CPy_INCREF(CPyModule_a_sync);
    CPy_DECREF(cpy_r_r41);
    cpy_r_r42 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* ('Result',) */
    cpy_r_r43 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'aiosqlite.context' */
    cpy_r_r44 = CPyStatic_brownie___globals;
    cpy_r_r45 = CPyImport_ImportFromMany(cpy_r_r43, cpy_r_r42, cpy_r_r42, cpy_r_r44);
    if (unlikely(cpy_r_r45 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "<module>", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL66;
    }
    CPyModule_aiosqlite___context = cpy_r_r45;
    CPy_INCREF(CPyModule_aiosqlite___context);
    CPy_DECREF(cpy_r_r45);
    cpy_r_r46 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* ('CONFIG', '_get_data_folder') */
    cpy_r_r47 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'brownie._config' */
    cpy_r_r48 = CPyStatic_brownie___globals;
    cpy_r_r49 = CPyImport_ImportFromMany(cpy_r_r47, cpy_r_r46, cpy_r_r46, cpy_r_r48);
    if (unlikely(cpy_r_r49 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "<module>", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL66;
    }
    CPyModule_brownie____config = cpy_r_r49;
    CPy_INCREF(CPyModule_brownie____config);
    CPy_DECREF(cpy_r_r49);
    cpy_r_r50 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* ('BrownieEnvironmentError',) */
    cpy_r_r51 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'brownie.exceptions' */
    cpy_r_r52 = CPyStatic_brownie___globals;
    cpy_r_r53 = CPyImport_ImportFromMany(cpy_r_r51, cpy_r_r50, cpy_r_r50, cpy_r_r52);
    if (unlikely(cpy_r_r53 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "<module>", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL66;
    }
    CPyModule_brownie___exceptions = cpy_r_r53;
    CPy_INCREF(CPyModule_brownie___exceptions);
    CPy_DECREF(cpy_r_r53);
    cpy_r_r54 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* ('_resolve_address',) */
    cpy_r_r55 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'brownie.network.contract' */
    cpy_r_r56 = CPyStatic_brownie___globals;
    cpy_r_r57 = CPyImport_ImportFromMany(cpy_r_r55, cpy_r_r54, cpy_r_r54, cpy_r_r56);
    if (unlikely(cpy_r_r57 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "<module>", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL66;
    }
    CPyModule_brownie___network___contract = cpy_r_r57;
    CPy_INCREF(CPyModule_brownie___network___contract);
    CPy_DECREF(cpy_r_r57);
    cpy_r_r58 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* ('DEPLOYMENT_KEYS',) */
    cpy_r_r59 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'brownie.project.build' */
    cpy_r_r60 = CPyStatic_brownie___globals;
    cpy_r_r61 = CPyImport_ImportFromMany(cpy_r_r59, cpy_r_r58, cpy_r_r58, cpy_r_r60);
    if (unlikely(cpy_r_r61 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "<module>", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL66;
    }
    CPyModule_brownie___project___build = cpy_r_r61;
    CPy_INCREF(CPyModule_brownie___project___build);
    CPy_DECREF(cpy_r_r61);
    cpy_r_r62 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* ('lru_cache',) */
    cpy_r_r63 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'functools' */
    cpy_r_r64 = CPyStatic_brownie___globals;
    cpy_r_r65 = CPyImport_ImportFromMany(cpy_r_r63, cpy_r_r62, cpy_r_r62, cpy_r_r64);
    if (unlikely(cpy_r_r65 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "<module>", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL66;
    }
    CPyModule_functools = cpy_r_r65;
    CPy_INCREF(CPyModule_functools);
    CPy_DECREF(cpy_r_r65);
    cpy_r_r66 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* ('InterfaceError', 'OperationalError') */
    cpy_r_r67 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'sqlite3' */
    cpy_r_r68 = CPyStatic_brownie___globals;
    cpy_r_r69 = CPyImport_ImportFromMany(cpy_r_r67, cpy_r_r66, cpy_r_r66, cpy_r_r68);
    if (unlikely(cpy_r_r69 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "<module>", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL66;
    }
    CPyModule_sqlite3 = cpy_r_r69;
    CPy_INCREF(CPyModule_sqlite3);
    CPy_DECREF(cpy_r_r69);
    cpy_r_r70 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* ('Address',) */
    cpy_r_r71 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'y.datatypes' */
    cpy_r_r72 = CPyStatic_brownie___globals;
    cpy_r_r73 = CPyImport_ImportFromMany(cpy_r_r71, cpy_r_r70, cpy_r_r70, cpy_r_r72);
    if (unlikely(cpy_r_r73 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "<module>", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL66;
    }
    CPyModule_y___datatypes = cpy_r_r73;
    CPy_INCREF(CPyModule_y___datatypes);
    CPy_DECREF(cpy_r_r73);
    cpy_r_r74 = CPyStatic_brownie___globals;
    cpy_r_r75 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'Literal' */
    cpy_r_r76 = CPyDict_GetItem(cpy_r_r74, cpy_r_r75);
    if (unlikely(cpy_r_r76 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "<module>", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL66;
    }
    cpy_r_r77 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'address' */
    cpy_r_r78 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'alias' */
    cpy_r_r79 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'paths' */
    cpy_r_r80 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'abi' */
    cpy_r_r81 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'ast' */
    cpy_r_r82 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'bytecode' */
    cpy_r_r83 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'compiler' */
    cpy_r_r84 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'contractName' */
    cpy_r_r85 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'deployedBytecode' */
    cpy_r_r86 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'deployedSourceMap' */
    cpy_r_r87 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'language' */
    cpy_r_r88 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'natspec' */
    cpy_r_r89 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'opcodes' */
    cpy_r_r90 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'pcMap' */
    cpy_r_r91 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'sourceMap' */
    cpy_r_r92 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'type' */
    CPy_INCREF(cpy_r_r77);
    CPy_INCREF(cpy_r_r78);
    CPy_INCREF(cpy_r_r79);
    CPy_INCREF(cpy_r_r80);
    CPy_INCREF(cpy_r_r81);
    CPy_INCREF(cpy_r_r82);
    CPy_INCREF(cpy_r_r83);
    CPy_INCREF(cpy_r_r84);
    CPy_INCREF(cpy_r_r85);
    CPy_INCREF(cpy_r_r86);
    CPy_INCREF(cpy_r_r87);
    CPy_INCREF(cpy_r_r88);
    CPy_INCREF(cpy_r_r89);
    CPy_INCREF(cpy_r_r90);
    CPy_INCREF(cpy_r_r91);
    CPy_INCREF(cpy_r_r92);
    cpy_r_r93.f0 = cpy_r_r77;
    cpy_r_r93.f1 = cpy_r_r78;
    cpy_r_r93.f2 = cpy_r_r79;
    cpy_r_r93.f3 = cpy_r_r80;
    cpy_r_r93.f4 = cpy_r_r81;
    cpy_r_r93.f5 = cpy_r_r82;
    cpy_r_r93.f6 = cpy_r_r83;
    cpy_r_r93.f7 = cpy_r_r84;
    cpy_r_r93.f8 = cpy_r_r85;
    cpy_r_r93.f9 = cpy_r_r86;
    cpy_r_r93.f10 = cpy_r_r87;
    cpy_r_r93.f11 = cpy_r_r88;
    cpy_r_r93.f12 = cpy_r_r89;
    cpy_r_r93.f13 = cpy_r_r90;
    cpy_r_r93.f14 = cpy_r_r91;
    cpy_r_r93.f15 = cpy_r_r92;
    cpy_r_r94 = PyTuple_New(16);
    if (unlikely(cpy_r_r94 == NULL))
        CPyError_OutOfMemory();
    PyObject *__tmp44 = cpy_r_r93.f0;
    PyTuple_SET_ITEM(cpy_r_r94, 0, __tmp44);
    PyObject *__tmp45 = cpy_r_r93.f1;
    PyTuple_SET_ITEM(cpy_r_r94, 1, __tmp45);
    PyObject *__tmp46 = cpy_r_r93.f2;
    PyTuple_SET_ITEM(cpy_r_r94, 2, __tmp46);
    PyObject *__tmp47 = cpy_r_r93.f3;
    PyTuple_SET_ITEM(cpy_r_r94, 3, __tmp47);
    PyObject *__tmp48 = cpy_r_r93.f4;
    PyTuple_SET_ITEM(cpy_r_r94, 4, __tmp48);
    PyObject *__tmp49 = cpy_r_r93.f5;
    PyTuple_SET_ITEM(cpy_r_r94, 5, __tmp49);
    PyObject *__tmp50 = cpy_r_r93.f6;
    PyTuple_SET_ITEM(cpy_r_r94, 6, __tmp50);
    PyObject *__tmp51 = cpy_r_r93.f7;
    PyTuple_SET_ITEM(cpy_r_r94, 7, __tmp51);
    PyObject *__tmp52 = cpy_r_r93.f8;
    PyTuple_SET_ITEM(cpy_r_r94, 8, __tmp52);
    PyObject *__tmp53 = cpy_r_r93.f9;
    PyTuple_SET_ITEM(cpy_r_r94, 9, __tmp53);
    PyObject *__tmp54 = cpy_r_r93.f10;
    PyTuple_SET_ITEM(cpy_r_r94, 10, __tmp54);
    PyObject *__tmp55 = cpy_r_r93.f11;
    PyTuple_SET_ITEM(cpy_r_r94, 11, __tmp55);
    PyObject *__tmp56 = cpy_r_r93.f12;
    PyTuple_SET_ITEM(cpy_r_r94, 12, __tmp56);
    PyObject *__tmp57 = cpy_r_r93.f13;
    PyTuple_SET_ITEM(cpy_r_r94, 13, __tmp57);
    PyObject *__tmp58 = cpy_r_r93.f14;
    PyTuple_SET_ITEM(cpy_r_r94, 14, __tmp58);
    PyObject *__tmp59 = cpy_r_r93.f15;
    PyTuple_SET_ITEM(cpy_r_r94, 15, __tmp59);
    cpy_r_r95 = PyObject_GetItem(cpy_r_r76, cpy_r_r94);
    CPy_DECREF(cpy_r_r76);
    CPy_DECREF(cpy_r_r94);
    if (unlikely(cpy_r_r95 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "<module>", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL66;
    }
    cpy_r_r96 = CPyStatic_brownie___globals;
    cpy_r_r97 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'SourceKey' */
    cpy_r_r98 = CPyDict_SetItem(cpy_r_r96, cpy_r_r97, cpy_r_r95);
    CPy_DECREF(cpy_r_r95);
    cpy_r_r99 = cpy_r_r98 >= 0;
    if (unlikely(!cpy_r_r99)) {
        CPy_AddTraceback("y/_db/brownie.py", "<module>", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL66;
    }
    cpy_r_r100 = CPyStatic_brownie___globals;
    cpy_r_r101 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'Dict' */
    cpy_r_r102 = CPyDict_GetItem(cpy_r_r100, cpy_r_r101);
    if (unlikely(cpy_r_r102 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "<module>", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL66;
    }
    cpy_r_r103 = (PyObject *)&PyUnicode_Type;
    cpy_r_r104 = CPyStatic_brownie___globals;
    cpy_r_r105 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'Any' */
    cpy_r_r106 = CPyDict_GetItem(cpy_r_r104, cpy_r_r105);
    if (unlikely(cpy_r_r106 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "<module>", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL67;
    }
    CPy_INCREF(cpy_r_r103);
    cpy_r_r107.f0 = cpy_r_r103;
    cpy_r_r107.f1 = cpy_r_r106;
    cpy_r_r108 = PyTuple_New(2);
    if (unlikely(cpy_r_r108 == NULL))
        CPyError_OutOfMemory();
    PyObject *__tmp60 = cpy_r_r107.f0;
    PyTuple_SET_ITEM(cpy_r_r108, 0, __tmp60);
    PyObject *__tmp61 = cpy_r_r107.f1;
    PyTuple_SET_ITEM(cpy_r_r108, 1, __tmp61);
    cpy_r_r109 = PyObject_GetItem(cpy_r_r102, cpy_r_r108);
    CPy_DECREF(cpy_r_r102);
    CPy_DECREF(cpy_r_r108);
    if (unlikely(cpy_r_r109 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "<module>", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL66;
    }
    cpy_r_r110 = CPyStatic_brownie___globals;
    cpy_r_r111 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'BuildJson' */
    cpy_r_r112 = CPyDict_SetItem(cpy_r_r110, cpy_r_r111, cpy_r_r109);
    CPy_DECREF(cpy_r_r109);
    cpy_r_r113 = cpy_r_r112 >= 0;
    if (unlikely(!cpy_r_r113)) {
        CPy_AddTraceback("y/_db/brownie.py", "<module>", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL66;
    }
    cpy_r_r114 = CPyStatic_brownie___globals;
    cpy_r_r115 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'Dict' */
    cpy_r_r116 = CPyDict_GetItem(cpy_r_r114, cpy_r_r115);
    if (unlikely(cpy_r_r116 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "<module>", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL66;
    }
    cpy_r_r117 = CPyStatic_brownie___globals;
    cpy_r_r118 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'SourceKey' */
    cpy_r_r119 = CPyDict_GetItem(cpy_r_r117, cpy_r_r118);
    if (unlikely(cpy_r_r119 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "<module>", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL68;
    }
    cpy_r_r120 = CPyStatic_brownie___globals;
    cpy_r_r121 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'Any' */
    cpy_r_r122 = CPyDict_GetItem(cpy_r_r120, cpy_r_r121);
    if (unlikely(cpy_r_r122 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "<module>", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL69;
    }
    cpy_r_r123.f0 = cpy_r_r119;
    cpy_r_r123.f1 = cpy_r_r122;
    cpy_r_r124 = PyTuple_New(2);
    if (unlikely(cpy_r_r124 == NULL))
        CPyError_OutOfMemory();
    PyObject *__tmp62 = cpy_r_r123.f0;
    PyTuple_SET_ITEM(cpy_r_r124, 0, __tmp62);
    PyObject *__tmp63 = cpy_r_r123.f1;
    PyTuple_SET_ITEM(cpy_r_r124, 1, __tmp63);
    cpy_r_r125 = PyObject_GetItem(cpy_r_r116, cpy_r_r124);
    CPy_DECREF(cpy_r_r116);
    CPy_DECREF(cpy_r_r124);
    if (unlikely(cpy_r_r125 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "<module>", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL66;
    }
    cpy_r_r126 = CPyStatic_brownie___globals;
    cpy_r_r127 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'Sources' */
    cpy_r_r128 = CPyDict_SetItem(cpy_r_r126, cpy_r_r127, cpy_r_r125);
    CPy_DECREF(cpy_r_r125);
    cpy_r_r129 = cpy_r_r128 >= 0;
    if (unlikely(!cpy_r_r129)) {
        CPy_AddTraceback("y/_db/brownie.py", "<module>", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL66;
    }
    cpy_r_r130 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'address' */
    cpy_r_r131 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'alias' */
    cpy_r_r132 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'paths' */
    cpy_r_r133 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'abi' */
    cpy_r_r134 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'ast' */
    cpy_r_r135 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'bytecode' */
    cpy_r_r136 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'compiler' */
    cpy_r_r137 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'contractName' */
    cpy_r_r138 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'deployedBytecode' */
    cpy_r_r139 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'deployedSourceMap' */
    cpy_r_r140 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'language' */
    cpy_r_r141 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'natspec' */
    cpy_r_r142 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'opcodes' */
    cpy_r_r143 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'pcMap' */
    cpy_r_r144 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'sourceMap' */
    cpy_r_r145 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'type' */
    CPy_INCREF(cpy_r_r130);
    CPy_INCREF(cpy_r_r131);
    CPy_INCREF(cpy_r_r132);
    CPy_INCREF(cpy_r_r133);
    CPy_INCREF(cpy_r_r134);
    CPy_INCREF(cpy_r_r135);
    CPy_INCREF(cpy_r_r136);
    CPy_INCREF(cpy_r_r137);
    CPy_INCREF(cpy_r_r138);
    CPy_INCREF(cpy_r_r139);
    CPy_INCREF(cpy_r_r140);
    CPy_INCREF(cpy_r_r141);
    CPy_INCREF(cpy_r_r142);
    CPy_INCREF(cpy_r_r143);
    CPy_INCREF(cpy_r_r144);
    CPy_INCREF(cpy_r_r145);
    cpy_r_r146.f0 = cpy_r_r130;
    cpy_r_r146.f1 = cpy_r_r131;
    cpy_r_r146.f2 = cpy_r_r132;
    cpy_r_r146.f3 = cpy_r_r133;
    cpy_r_r146.f4 = cpy_r_r134;
    cpy_r_r146.f5 = cpy_r_r135;
    cpy_r_r146.f6 = cpy_r_r136;
    cpy_r_r146.f7 = cpy_r_r137;
    cpy_r_r146.f8 = cpy_r_r138;
    cpy_r_r146.f9 = cpy_r_r139;
    cpy_r_r146.f10 = cpy_r_r140;
    cpy_r_r146.f11 = cpy_r_r141;
    cpy_r_r146.f12 = cpy_r_r142;
    cpy_r_r146.f13 = cpy_r_r143;
    cpy_r_r146.f14 = cpy_r_r144;
    cpy_r_r146.f15 = cpy_r_r145;
    CPyStatic_brownie___SOURCE_KEYS = cpy_r_r146;
    CPy_INCREF(CPyStatic_brownie___SOURCE_KEYS.f0);
    CPy_INCREF(CPyStatic_brownie___SOURCE_KEYS.f1);
    CPy_INCREF(CPyStatic_brownie___SOURCE_KEYS.f2);
    CPy_INCREF(CPyStatic_brownie___SOURCE_KEYS.f3);
    CPy_INCREF(CPyStatic_brownie___SOURCE_KEYS.f4);
    CPy_INCREF(CPyStatic_brownie___SOURCE_KEYS.f5);
    CPy_INCREF(CPyStatic_brownie___SOURCE_KEYS.f6);
    CPy_INCREF(CPyStatic_brownie___SOURCE_KEYS.f7);
    CPy_INCREF(CPyStatic_brownie___SOURCE_KEYS.f8);
    CPy_INCREF(CPyStatic_brownie___SOURCE_KEYS.f9);
    CPy_INCREF(CPyStatic_brownie___SOURCE_KEYS.f10);
    CPy_INCREF(CPyStatic_brownie___SOURCE_KEYS.f11);
    CPy_INCREF(CPyStatic_brownie___SOURCE_KEYS.f12);
    CPy_INCREF(CPyStatic_brownie___SOURCE_KEYS.f13);
    CPy_INCREF(CPyStatic_brownie___SOURCE_KEYS.f14);
    CPy_INCREF(CPyStatic_brownie___SOURCE_KEYS.f15);
    cpy_r_r147 = CPyStatic_brownie___globals;
    cpy_r_r148 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'SOURCE_KEYS' */
    cpy_r_r149 = PyTuple_New(16);
    if (unlikely(cpy_r_r149 == NULL))
        CPyError_OutOfMemory();
    PyObject *__tmp64 = cpy_r_r146.f0;
    PyTuple_SET_ITEM(cpy_r_r149, 0, __tmp64);
    PyObject *__tmp65 = cpy_r_r146.f1;
    PyTuple_SET_ITEM(cpy_r_r149, 1, __tmp65);
    PyObject *__tmp66 = cpy_r_r146.f2;
    PyTuple_SET_ITEM(cpy_r_r149, 2, __tmp66);
    PyObject *__tmp67 = cpy_r_r146.f3;
    PyTuple_SET_ITEM(cpy_r_r149, 3, __tmp67);
    PyObject *__tmp68 = cpy_r_r146.f4;
    PyTuple_SET_ITEM(cpy_r_r149, 4, __tmp68);
    PyObject *__tmp69 = cpy_r_r146.f5;
    PyTuple_SET_ITEM(cpy_r_r149, 5, __tmp69);
    PyObject *__tmp70 = cpy_r_r146.f6;
    PyTuple_SET_ITEM(cpy_r_r149, 6, __tmp70);
    PyObject *__tmp71 = cpy_r_r146.f7;
    PyTuple_SET_ITEM(cpy_r_r149, 7, __tmp71);
    PyObject *__tmp72 = cpy_r_r146.f8;
    PyTuple_SET_ITEM(cpy_r_r149, 8, __tmp72);
    PyObject *__tmp73 = cpy_r_r146.f9;
    PyTuple_SET_ITEM(cpy_r_r149, 9, __tmp73);
    PyObject *__tmp74 = cpy_r_r146.f10;
    PyTuple_SET_ITEM(cpy_r_r149, 10, __tmp74);
    PyObject *__tmp75 = cpy_r_r146.f11;
    PyTuple_SET_ITEM(cpy_r_r149, 11, __tmp75);
    PyObject *__tmp76 = cpy_r_r146.f12;
    PyTuple_SET_ITEM(cpy_r_r149, 12, __tmp76);
    PyObject *__tmp77 = cpy_r_r146.f13;
    PyTuple_SET_ITEM(cpy_r_r149, 13, __tmp77);
    PyObject *__tmp78 = cpy_r_r146.f14;
    PyTuple_SET_ITEM(cpy_r_r149, 14, __tmp78);
    PyObject *__tmp79 = cpy_r_r146.f15;
    PyTuple_SET_ITEM(cpy_r_r149, 15, __tmp79);
    cpy_r_r150 = CPyDict_SetItem(cpy_r_r147, cpy_r_r148, cpy_r_r149);
    CPy_DECREF(cpy_r_r149);
    cpy_r_r151 = cpy_r_r150 >= 0;
    if (unlikely(!cpy_r_r151)) {
        CPy_AddTraceback("y/_db/brownie.py", "<module>", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL66;
    }
    cpy_r_r152 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'ast' */
    cpy_r_r153 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'bytecode' */
    cpy_r_r154 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'coverageMap' */
    cpy_r_r155 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'deployedBytecode' */
    cpy_r_r156 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'deployedSourceMap' */
    cpy_r_r157 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'natspec' */
    cpy_r_r158 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'opcodes' */
    cpy_r_r159 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'pcMap' */
    CPy_INCREF(cpy_r_r152);
    CPy_INCREF(cpy_r_r153);
    CPy_INCREF(cpy_r_r154);
    CPy_INCREF(cpy_r_r155);
    CPy_INCREF(cpy_r_r156);
    CPy_INCREF(cpy_r_r157);
    CPy_INCREF(cpy_r_r158);
    CPy_INCREF(cpy_r_r159);
    cpy_r_r160.f0 = cpy_r_r152;
    cpy_r_r160.f1 = cpy_r_r153;
    cpy_r_r160.f2 = cpy_r_r154;
    cpy_r_r160.f3 = cpy_r_r155;
    cpy_r_r160.f4 = cpy_r_r156;
    cpy_r_r160.f5 = cpy_r_r157;
    cpy_r_r160.f6 = cpy_r_r158;
    cpy_r_r160.f7 = cpy_r_r159;
    CPyStatic_brownie___DISCARD_SOURCE_KEYS = cpy_r_r160;
    CPy_INCREF(CPyStatic_brownie___DISCARD_SOURCE_KEYS.f0);
    CPy_INCREF(CPyStatic_brownie___DISCARD_SOURCE_KEYS.f1);
    CPy_INCREF(CPyStatic_brownie___DISCARD_SOURCE_KEYS.f2);
    CPy_INCREF(CPyStatic_brownie___DISCARD_SOURCE_KEYS.f3);
    CPy_INCREF(CPyStatic_brownie___DISCARD_SOURCE_KEYS.f4);
    CPy_INCREF(CPyStatic_brownie___DISCARD_SOURCE_KEYS.f5);
    CPy_INCREF(CPyStatic_brownie___DISCARD_SOURCE_KEYS.f6);
    CPy_INCREF(CPyStatic_brownie___DISCARD_SOURCE_KEYS.f7);
    cpy_r_r161 = CPyStatic_brownie___globals;
    cpy_r_r162 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'DISCARD_SOURCE_KEYS' */
    cpy_r_r163 = PyTuple_New(8);
    if (unlikely(cpy_r_r163 == NULL))
        CPyError_OutOfMemory();
    PyObject *__tmp80 = cpy_r_r160.f0;
    PyTuple_SET_ITEM(cpy_r_r163, 0, __tmp80);
    PyObject *__tmp81 = cpy_r_r160.f1;
    PyTuple_SET_ITEM(cpy_r_r163, 1, __tmp81);
    PyObject *__tmp82 = cpy_r_r160.f2;
    PyTuple_SET_ITEM(cpy_r_r163, 2, __tmp82);
    PyObject *__tmp83 = cpy_r_r160.f3;
    PyTuple_SET_ITEM(cpy_r_r163, 3, __tmp83);
    PyObject *__tmp84 = cpy_r_r160.f4;
    PyTuple_SET_ITEM(cpy_r_r163, 4, __tmp84);
    PyObject *__tmp85 = cpy_r_r160.f5;
    PyTuple_SET_ITEM(cpy_r_r163, 5, __tmp85);
    PyObject *__tmp86 = cpy_r_r160.f6;
    PyTuple_SET_ITEM(cpy_r_r163, 6, __tmp86);
    PyObject *__tmp87 = cpy_r_r160.f7;
    PyTuple_SET_ITEM(cpy_r_r163, 7, __tmp87);
    cpy_r_r164 = CPyDict_SetItem(cpy_r_r161, cpy_r_r162, cpy_r_r163);
    CPy_DECREF(cpy_r_r163);
    cpy_r_r165 = cpy_r_r164 >= 0;
    if (unlikely(!cpy_r_r165)) {
        CPy_AddTraceback("y/_db/brownie.py", "<module>", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL66;
    }
    cpy_r_r166 = CPyModule_hashlib;
    cpy_r_r167 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'sha1' */
    cpy_r_r168 = CPyObject_GetAttr(cpy_r_r166, cpy_r_r167);
    if (unlikely(cpy_r_r168 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "<module>", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL66;
    }
    CPyStatic_brownie___sha1 = cpy_r_r168;
    CPy_INCREF(CPyStatic_brownie___sha1);
    cpy_r_r169 = CPyStatic_brownie___globals;
    cpy_r_r170 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'sha1' */
    cpy_r_r171 = CPyDict_SetItem(cpy_r_r169, cpy_r_r170, cpy_r_r168);
    CPy_DECREF(cpy_r_r168);
    cpy_r_r172 = cpy_r_r171 >= 0;
    if (unlikely(!cpy_r_r172)) {
        CPy_AddTraceback("y/_db/brownie.py", "<module>", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL66;
    }
    cpy_r_r173 = CPyModule_json;
    cpy_r_r174 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'dumps' */
    cpy_r_r175 = CPyObject_GetAttr(cpy_r_r173, cpy_r_r174);
    if (unlikely(cpy_r_r175 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "<module>", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL66;
    }
    CPyStatic_brownie___dumps = cpy_r_r175;
    CPy_INCREF(CPyStatic_brownie___dumps);
    cpy_r_r176 = CPyStatic_brownie___globals;
    cpy_r_r177 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'dumps' */
    cpy_r_r178 = CPyDict_SetItem(cpy_r_r176, cpy_r_r177, cpy_r_r175);
    CPy_DECREF(cpy_r_r175);
    cpy_r_r179 = cpy_r_r178 >= 0;
    if (unlikely(!cpy_r_r179)) {
        CPy_AddTraceback("y/_db/brownie.py", "<module>", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL66;
    }
    cpy_r_r180 = CPyModule_json;
    cpy_r_r181 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'loads' */
    cpy_r_r182 = CPyObject_GetAttr(cpy_r_r180, cpy_r_r181);
    if (unlikely(cpy_r_r182 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "<module>", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL66;
    }
    CPyStatic_brownie___loads = cpy_r_r182;
    CPy_INCREF(CPyStatic_brownie___loads);
    cpy_r_r183 = CPyStatic_brownie___globals;
    cpy_r_r184 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'loads' */
    cpy_r_r185 = CPyDict_SetItem(cpy_r_r183, cpy_r_r184, cpy_r_r182);
    CPy_DECREF(cpy_r_r182);
    cpy_r_r186 = cpy_r_r185 >= 0;
    if (unlikely(!cpy_r_r186)) {
        CPy_AddTraceback("y/_db/brownie.py", "<module>", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL66;
    }
    cpy_r_r187 = CPyStatic_brownie___globals;
    cpy_r_r188 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'Lock' */
    cpy_r_r189 = CPyDict_GetItem(cpy_r_r187, cpy_r_r188);
    if (unlikely(cpy_r_r189 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "<module>", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL66;
    }
    cpy_r_r190 = PyObject_Vectorcall(cpy_r_r189, 0, 0, 0);
    CPy_DECREF(cpy_r_r189);
    if (unlikely(cpy_r_r190 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "<module>", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL66;
    }
    CPyStatic_brownie___sqlite_lock = cpy_r_r190;
    CPy_INCREF(CPyStatic_brownie___sqlite_lock);
    cpy_r_r191 = CPyStatic_brownie___globals;
    cpy_r_r192 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'sqlite_lock' */
    cpy_r_r193 = CPyDict_SetItem(cpy_r_r191, cpy_r_r192, cpy_r_r190);
    CPy_DECREF(cpy_r_r190);
    cpy_r_r194 = cpy_r_r193 >= 0;
    if (unlikely(!cpy_r_r194)) {
        CPy_AddTraceback("y/_db/brownie.py", "<module>", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL66;
    }
    cpy_r_r195 = NULL;
    cpy_r_r196 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'y._db.brownie' */
    cpy_r_r197 = (PyObject *)CPyType_brownie___AsyncCursor_template;
    cpy_r_r198 = CPyType_FromTemplate(cpy_r_r197, cpy_r_r195, cpy_r_r196);
    if (unlikely(cpy_r_r198 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "<module>", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL66;
    }
    cpy_r_r199 = CPyDef_brownie___AsyncCursor_trait_vtable_setup();
    if (unlikely(cpy_r_r199 == 2)) {
        CPy_AddTraceback("y/_db/brownie.py", "<module>", -1, CPyStatic_brownie___globals);
        goto CPyL70;
    }
    cpy_r_r200 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* '__mypyc_attrs__' */
    cpy_r_r201 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* '_filename' */
    cpy_r_r202 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* '_db' */
    cpy_r_r203 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* '_connected' */
    cpy_r_r204 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* '_execute' */
    cpy_r_r205 = PyTuple_Pack(4, cpy_r_r201, cpy_r_r202, cpy_r_r203, cpy_r_r204);
    if (unlikely(cpy_r_r205 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "<module>", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL70;
    }
    cpy_r_r206 = PyObject_SetAttr(cpy_r_r198, cpy_r_r200, cpy_r_r205);
    CPy_DECREF(cpy_r_r205);
    cpy_r_r207 = cpy_r_r206 >= 0;
    if (unlikely(!cpy_r_r207)) {
        CPy_AddTraceback("y/_db/brownie.py", "<module>", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL70;
    }
    CPyType_brownie___AsyncCursor = (PyTypeObject *)cpy_r_r198;
    CPy_INCREF(CPyType_brownie___AsyncCursor);
    cpy_r_r208 = CPyStatic_brownie___globals;
    cpy_r_r209 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'AsyncCursor' */
    cpy_r_r210 = PyDict_SetItem(cpy_r_r208, cpy_r_r209, cpy_r_r198);
    CPy_DECREF(cpy_r_r198);
    cpy_r_r211 = cpy_r_r210 >= 0;
    if (unlikely(!cpy_r_r211)) {
        CPy_AddTraceback("y/_db/brownie.py", "<module>", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL66;
    }
    cpy_r_r212 = CPyStatic_brownie___globals;
    cpy_r_r213 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* '_get_data_folder' */
    cpy_r_r214 = CPyDict_GetItem(cpy_r_r212, cpy_r_r213);
    if (unlikely(cpy_r_r214 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "<module>", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL66;
    }
    cpy_r_r215 = PyObject_Vectorcall(cpy_r_r214, 0, 0, 0);
    CPy_DECREF(cpy_r_r214);
    if (unlikely(cpy_r_r215 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "<module>", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL66;
    }
    cpy_r_r216 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'deployments.db' */
    cpy_r_r217 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'joinpath' */
    PyObject *cpy_r_r218[2] = {cpy_r_r215, cpy_r_r216};
    cpy_r_r219 = (PyObject **)&cpy_r_r218;
    cpy_r_r220 = PyObject_VectorcallMethod(cpy_r_r217, cpy_r_r219, 9223372036854775810ULL, 0);
    if (unlikely(cpy_r_r220 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "<module>", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL71;
    }
    CPy_DECREF(cpy_r_r215);
    cpy_r_r221 = CPyDef_brownie___AsyncCursor(cpy_r_r220);
    CPy_DECREF(cpy_r_r220);
    if (unlikely(cpy_r_r221 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "<module>", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL66;
    }
    CPyStatic_brownie___cur = cpy_r_r221;
    CPy_INCREF_NO_IMM(CPyStatic_brownie___cur);
    cpy_r_r222 = CPyStatic_brownie___globals;
    cpy_r_r223 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'cur' */
    cpy_r_r224 = CPyDict_SetItem(cpy_r_r222, cpy_r_r223, cpy_r_r221);
    CPy_DECREF_NO_IMM(cpy_r_r221);
    cpy_r_r225 = cpy_r_r224 >= 0;
    if (unlikely(!cpy_r_r225)) {
        CPy_AddTraceback("y/_db/brownie.py", "<module>", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL66;
    }
    cpy_r_r226 = CPyStatic_brownie___cur;
    if (likely(cpy_r_r226 != NULL)) goto CPyL53;
    PyErr_SetString(PyExc_NameError, "value for final name \"cur\" was not set");
    cpy_r_r227 = 0;
    if (unlikely(!cpy_r_r227)) {
        CPy_AddTraceback("y/_db/brownie.py", "<module>", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL66;
    }
    CPy_Unreachable();
CPyL53: ;
    cpy_r_r228 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'fetchone' */
    cpy_r_r229 = CPyObject_GetAttr(cpy_r_r226, cpy_r_r228);
    if (unlikely(cpy_r_r229 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "<module>", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL66;
    }
    cpy_r_r230 = CPyStatic_brownie___globals;
    cpy_r_r231 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'SmartProcessingQueue' */
    cpy_r_r232 = CPyDict_GetItem(cpy_r_r230, cpy_r_r231);
    if (unlikely(cpy_r_r232 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "<module>", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL72;
    }
    cpy_r_r233 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 32 */
    PyObject *cpy_r_r234[2] = {cpy_r_r229, cpy_r_r233};
    cpy_r_r235 = (PyObject **)&cpy_r_r234;
    cpy_r_r236 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* ('num_workers',) */
    cpy_r_r237 = PyObject_Vectorcall(cpy_r_r232, cpy_r_r235, 1, cpy_r_r236);
    CPy_DECREF(cpy_r_r232);
    if (unlikely(cpy_r_r237 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "<module>", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL72;
    }
    CPy_DECREF(cpy_r_r229);
    CPyStatic_brownie___fetchone = cpy_r_r237;
    CPy_INCREF(CPyStatic_brownie___fetchone);
    cpy_r_r238 = CPyStatic_brownie___globals;
    cpy_r_r239 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'fetchone' */
    cpy_r_r240 = CPyDict_SetItem(cpy_r_r238, cpy_r_r239, cpy_r_r237);
    CPy_DECREF(cpy_r_r237);
    cpy_r_r241 = cpy_r_r240 >= 0;
    if (unlikely(!cpy_r_r241)) {
        CPy_AddTraceback("y/_db/brownie.py", "<module>", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL66;
    }
    cpy_r_r242 = CPyStatic_brownie___globals;
    cpy_r_r243 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* '_get_select_statement' */
    cpy_r_r244 = CPyDict_GetItem(cpy_r_r242, cpy_r_r243);
    if (unlikely(cpy_r_r244 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "<module>", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL66;
    }
    cpy_r_r245 = CPyStatic_brownie___globals;
    cpy_r_r246 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'lru_cache' */
    cpy_r_r247 = CPyDict_GetItem(cpy_r_r245, cpy_r_r246);
    if (unlikely(cpy_r_r247 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "<module>", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL73;
    }
    cpy_r_r248 = Py_None;
    PyObject *cpy_r_r249[1] = {cpy_r_r248};
    cpy_r_r250 = (PyObject **)&cpy_r_r249;
    cpy_r_r251 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* ('maxsize',) */
    cpy_r_r252 = PyObject_Vectorcall(cpy_r_r247, cpy_r_r250, 0, cpy_r_r251);
    CPy_DECREF(cpy_r_r247);
    if (unlikely(cpy_r_r252 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "<module>", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL73;
    }
    PyObject *cpy_r_r253[1] = {cpy_r_r244};
    cpy_r_r254 = (PyObject **)&cpy_r_r253;
    cpy_r_r255 = PyObject_Vectorcall(cpy_r_r252, cpy_r_r254, 1, 0);
    CPy_DECREF(cpy_r_r252);
    if (unlikely(cpy_r_r255 == NULL)) {
        CPy_AddTraceback("y/_db/brownie.py", "<module>", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL73;
    }
    CPy_DECREF(cpy_r_r244);
    cpy_r_r256 = CPyStatic_brownie___globals;
    cpy_r_r257 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* '_get_select_statement' */
    cpy_r_r258 = PyDict_SetItem(cpy_r_r256, cpy_r_r257, cpy_r_r255);
    CPy_DECREF(cpy_r_r255);
    cpy_r_r259 = cpy_r_r258 >= 0;
    if (unlikely(!cpy_r_r259)) {
        CPy_AddTraceback("y/_db/brownie.py", "<module>", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL66;
    }
    cpy_r_r260 = CPyStatic_brownie___DISCARD_SOURCE_KEYS;
    if (likely(cpy_r_r260.f0 != NULL)) goto CPyL65;
    PyErr_SetString(PyExc_NameError, "value for final name \"DISCARD_SOURCE_KEYS\" was not set");
    cpy_r_r261 = 0;
    if (unlikely(!cpy_r_r261)) {
        CPy_AddTraceback("y/_db/brownie.py", "<module>", DIFFCHECK_PLACEHOLDER, CPyStatic_brownie___globals);
        goto CPyL66;
    }
    CPy_Unreachable();
CPyL65: ;
    CPy_INCREF(cpy_r_r260.f0);
    CPy_INCREF(cpy_r_r260.f1);
    CPy_INCREF(cpy_r_r260.f2);
    CPy_INCREF(cpy_r_r260.f3);
    CPy_INCREF(cpy_r_r260.f4);
    CPy_INCREF(cpy_r_r260.f5);
    CPy_INCREF(cpy_r_r260.f6);
    CPy_INCREF(cpy_r_r260.f7);
    cpy_r_r262 = PyTuple_New(8);
    if (unlikely(cpy_r_r262 == NULL))
        CPyError_OutOfMemory();
    PyObject *__tmp88 = cpy_r_r260.f0;
    PyTuple_SET_ITEM(cpy_r_r262, 0, __tmp88);
    PyObject *__tmp89 = cpy_r_r260.f1;
    PyTuple_SET_ITEM(cpy_r_r262, 1, __tmp89);
    PyObject *__tmp90 = cpy_r_r260.f2;
    PyTuple_SET_ITEM(cpy_r_r262, 2, __tmp90);
    PyObject *__tmp91 = cpy_r_r260.f3;
    PyTuple_SET_ITEM(cpy_r_r262, 3, __tmp91);
    PyObject *__tmp92 = cpy_r_r260.f4;
    PyTuple_SET_ITEM(cpy_r_r262, 4, __tmp92);
    PyObject *__tmp93 = cpy_r_r260.f5;
    PyTuple_SET_ITEM(cpy_r_r262, 5, __tmp93);
    PyObject *__tmp94 = cpy_r_r260.f6;
    PyTuple_SET_ITEM(cpy_r_r262, 6, __tmp94);
    PyObject *__tmp95 = cpy_r_r260.f7;
    PyTuple_SET_ITEM(cpy_r_r262, 7, __tmp95);
    CPyStatic_brownie___y____db___brownie____get_deployment___skip_source_keys = cpy_r_r262;
    CPy_INCREF(CPyStatic_brownie___y____db___brownie____get_deployment___skip_source_keys);
    CPy_DECREF(cpy_r_r262);
    return 1;
CPyL66: ;
    cpy_r_r263 = 2;
    return cpy_r_r263;
CPyL67: ;
    CPy_DecRef(cpy_r_r102);
    goto CPyL66;
CPyL68: ;
    CPy_DecRef(cpy_r_r116);
    goto CPyL66;
CPyL69: ;
    CPy_DecRef(cpy_r_r116);
    CPy_DecRef(cpy_r_r119);
    goto CPyL66;
CPyL70: ;
    CPy_DecRef(cpy_r_r198);
    goto CPyL66;
CPyL71: ;
    CPy_DecRef(cpy_r_r215);
    goto CPyL66;
CPyL72: ;
    CPy_DecRef(cpy_r_r229);
    goto CPyL66;
CPyL73: ;
    CPy_DecRef(cpy_r_r244);
    goto CPyL66;
}
static PyMethodDef stringifymodule_methods[] = {
    {"stringify_column_value", (PyCFunction)CPyPy_stringify___stringify_column_value, METH_FASTCALL | METH_KEYWORDS, PyDoc_STR("stringify_column_value(value, provider)\n--\n\n") /* docstring */},
    {"build_row", (PyCFunction)CPyPy_stringify___build_row, METH_FASTCALL | METH_KEYWORDS, PyDoc_STR("build_row(row, provider)\n--\n\n") /* docstring */},
    {"build_query", (PyCFunction)CPyPy_stringify___build_query, METH_FASTCALL | METH_KEYWORDS, PyDoc_STR("build_query(provider_name, entity_name, columns, items)\n--\n\n") /* docstring */},
    {NULL, NULL, 0, NULL}
};

int CPyExec_y____db___utils___stringify(PyObject *module)
{
    PyObject* modname = NULL;
    modname = PyObject_GetAttrString((PyObject *)CPyModule_y____db___utils___stringify__internal, "__name__");
    CPyStatic_stringify___globals = PyModule_GetDict(CPyModule_y____db___utils___stringify__internal);
    if (unlikely(CPyStatic_stringify___globals == NULL))
        goto fail;
    if (CPyGlobalsInit() < 0)
        goto fail;
    char result = CPyDef_stringify_____top_level__();
    if (result == 2)
        goto fail;
    Py_DECREF(modname);
    return 0;
    fail:
    Py_CLEAR(CPyModule_y____db___utils___stringify__internal);
    Py_CLEAR(modname);
    CPy_XDECREF(CPyStatic_stringify___UTC);
    CPyStatic_stringify___UTC = NULL;
    CPy_XDECREF(CPyStatic_stringify___astimezone);
    CPyStatic_stringify___astimezone = NULL;
    CPy_XDECREF(CPyStatic_stringify___isoformat);
    CPyStatic_stringify___isoformat = NULL;
    return -1;
}
static struct PyModuleDef stringifymodule = {
    PyModuleDef_HEAD_INIT,
    "y._db.utils.stringify",
    NULL, /* docstring */
    0,       /* size of per-interpreter state of the module */
    stringifymodule_methods,
    NULL,
};

PyObject *CPyInit_y____db___utils___stringify(void)
{
    if (CPyModule_y____db___utils___stringify__internal) {
        Py_INCREF(CPyModule_y____db___utils___stringify__internal);
        return CPyModule_y____db___utils___stringify__internal;
    }
    CPyModule_y____db___utils___stringify__internal = PyModule_Create(&stringifymodule);
    if (unlikely(CPyModule_y____db___utils___stringify__internal == NULL))
        goto fail;
    if (CPyExec_y____db___utils___stringify(CPyModule_y____db___utils___stringify__internal) != 0)
        goto fail;
    return CPyModule_y____db___utils___stringify__internal;
    fail:
    return NULL;
}

PyObject *CPyDef_stringify___stringify_column_value(PyObject *cpy_r_value, PyObject *cpy_r_provider) {
    PyObject *cpy_r_r0;
    char cpy_r_r1;
    PyObject *cpy_r_r2;
    char cpy_r_r3;
    PyObject *cpy_r_r4;
    char cpy_r_r5;
    PyObject *cpy_r_r6;
    PyObject *cpy_r_r7;
    PyObject *cpy_r_r8;
    PyObject *cpy_r_r9;
    PyObject *cpy_r_r10;
    PyObject *cpy_r_r11;
    char cpy_r_r12;
    PyObject *cpy_r_r13;
    PyObject *cpy_r_r14;
    PyObject *cpy_r_r15;
    PyObject **cpy_r_r17;
    PyObject *cpy_r_r18;
    PyObject *cpy_r_r19;
    PyObject *cpy_r_r20;
    PyObject *cpy_r_r21;
    PyObject *cpy_r_r22;
    PyObject *cpy_r_r23;
    PyObject *cpy_r_r24;
    PyObject **cpy_r_r26;
    PyObject *cpy_r_r27;
    char cpy_r_r28;
    PyObject *cpy_r_r29;
    PyObject *cpy_r_r30;
    PyObject *cpy_r_r31;
    PyObject *cpy_r_r32;
    PyObject *cpy_r_r33;
    PyObject *cpy_r_r34;
    PyObject *cpy_r_r35;
    PyObject *cpy_r_r36;
    tuple_T2OO cpy_r_r37;
    PyObject *cpy_r_r38;
    int32_t cpy_r_r39;
    char cpy_r_r40;
    char cpy_r_r41;
    PyObject *cpy_r_r42;
    PyObject *cpy_r_r43;
    PyObject *cpy_r_r44;
    PyObject *cpy_r_r45;
    int32_t cpy_r_r46;
    char cpy_r_r47;
    char cpy_r_r48;
    PyObject *cpy_r_r49;
    PyObject *cpy_r_r50;
    char cpy_r_r51;
    PyObject *cpy_r_r52;
    char cpy_r_r53;
    PyObject **cpy_r_r55;
    PyObject *cpy_r_r56;
    PyObject *cpy_r_r57;
    char cpy_r_r58;
    PyObject **cpy_r_r60;
    PyObject *cpy_r_r61;
    PyObject *cpy_r_r62;
    PyObject *cpy_r_r63;
    PyObject *cpy_r_r64;
    PyObject *cpy_r_r65;
    PyObject *cpy_r_r66;
    PyObject *cpy_r_r67;
    PyObject *cpy_r_r68;
    PyObject **cpy_r_r70;
    PyObject *cpy_r_r71;
    PyObject *cpy_r_r72;
    cpy_r_r0 = (PyObject *)&_Py_NoneStruct;
    cpy_r_r1 = cpy_r_value == cpy_r_r0;
    if (!cpy_r_r1) goto CPyL2;
    cpy_r_r2 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'null' */
    CPy_INCREF(cpy_r_r2);
    return cpy_r_r2;
CPyL2: ;
    cpy_r_r3 = PyBytes_Check(cpy_r_value);
    if (!cpy_r_r3) goto CPyL18;
    cpy_r_r4 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'postgres' */
    cpy_r_r5 = CPyStr_EqualLiteral(cpy_r_provider, cpy_r_r4, 8);
    if (!cpy_r_r5) goto CPyL8;
    cpy_r_r6 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* "'" */
    CPy_INCREF(cpy_r_value);
    if (likely(PyBytes_Check(cpy_r_value) || PyByteArray_Check(cpy_r_value)))
        cpy_r_r7 = cpy_r_value;
    else {
        CPy_TypeErrorTraceback("y/_db/utils/stringify.py", "stringify_column_value", 53, CPyStatic_stringify___globals, "bytes", cpy_r_value);
        goto CPyL48;
    }
    cpy_r_r8 = CPy_DecodeUTF8(cpy_r_r7);
    CPy_DECREF(cpy_r_r7);
    if (unlikely(cpy_r_r8 == NULL)) {
        CPy_AddTraceback("y/_db/utils/stringify.py", "stringify_column_value", DIFFCHECK_PLACEHOLDER, CPyStatic_stringify___globals);
        goto CPyL48;
    }
    cpy_r_r9 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* "'::bytea" */
    cpy_r_r10 = CPyStr_Build(3, cpy_r_r6, cpy_r_r8, cpy_r_r9);
    CPy_DECREF(cpy_r_r8);
    if (unlikely(cpy_r_r10 == NULL)) {
        CPy_AddTraceback("y/_db/utils/stringify.py", "stringify_column_value", DIFFCHECK_PLACEHOLDER, CPyStatic_stringify___globals);
        goto CPyL48;
    }
    return cpy_r_r10;
CPyL8: ;
    cpy_r_r11 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'sqlite' */
    cpy_r_r12 = CPyStr_EqualLiteral(cpy_r_provider, cpy_r_r11, 6);
    if (!cpy_r_r12) goto CPyL14;
    cpy_r_r13 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* "X'" */
    CPy_INCREF(cpy_r_value);
    if (likely(PyBytes_Check(cpy_r_value) || PyByteArray_Check(cpy_r_value)))
        cpy_r_r14 = cpy_r_value;
    else {
        CPy_TypeErrorTraceback("y/_db/utils/stringify.py", "stringify_column_value", 55, CPyStatic_stringify___globals, "bytes", cpy_r_value);
        goto CPyL48;
    }
    cpy_r_r15 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'hex' */
    PyObject *cpy_r_r16[1] = {cpy_r_r14};
    cpy_r_r17 = (PyObject **)&cpy_r_r16;
    cpy_r_r18 = PyObject_VectorcallMethod(cpy_r_r15, cpy_r_r17, 9223372036854775809ULL, 0);
    if (unlikely(cpy_r_r18 == NULL)) {
        CPy_AddTraceback("y/_db/utils/stringify.py", "stringify_column_value", DIFFCHECK_PLACEHOLDER, CPyStatic_stringify___globals);
        goto CPyL49;
    }
    CPy_DECREF(cpy_r_r14);
    if (likely(PyUnicode_Check(cpy_r_r18)))
        cpy_r_r19 = cpy_r_r18;
    else {
        CPy_TypeErrorTraceback("y/_db/utils/stringify.py", "stringify_column_value", 55, CPyStatic_stringify___globals, "str", cpy_r_r18);
        goto CPyL48;
    }
    cpy_r_r20 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* "'" */
    cpy_r_r21 = CPyStr_Build(3, cpy_r_r13, cpy_r_r19, cpy_r_r20);
    CPy_DECREF(cpy_r_r19);
    if (unlikely(cpy_r_r21 == NULL)) {
        CPy_AddTraceback("y/_db/utils/stringify.py", "stringify_column_value", DIFFCHECK_PLACEHOLDER, CPyStatic_stringify___globals);
        goto CPyL48;
    }
    return cpy_r_r21;
CPyL14: ;
    cpy_r_r22 = CPyModule_builtins;
    cpy_r_r23 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'NotImplementedError' */
    cpy_r_r24 = CPyObject_GetAttr(cpy_r_r22, cpy_r_r23);
    if (unlikely(cpy_r_r24 == NULL)) {
        CPy_AddTraceback("y/_db/utils/stringify.py", "stringify_column_value", DIFFCHECK_PLACEHOLDER, CPyStatic_stringify___globals);
        goto CPyL48;
    }
    PyObject *cpy_r_r25[1] = {cpy_r_provider};
    cpy_r_r26 = (PyObject **)&cpy_r_r25;
    cpy_r_r27 = PyObject_Vectorcall(cpy_r_r24, cpy_r_r26, 1, 0);
    CPy_DECREF(cpy_r_r24);
    if (unlikely(cpy_r_r27 == NULL)) {
        CPy_AddTraceback("y/_db/utils/stringify.py", "stringify_column_value", DIFFCHECK_PLACEHOLDER, CPyStatic_stringify___globals);
        goto CPyL48;
    }
    CPy_Raise(cpy_r_r27);
    CPy_DECREF(cpy_r_r27);
    if (unlikely(!0)) {
        CPy_AddTraceback("y/_db/utils/stringify.py", "stringify_column_value", DIFFCHECK_PLACEHOLDER, CPyStatic_stringify___globals);
        goto CPyL48;
    }
    CPy_Unreachable();
CPyL18: ;
    cpy_r_r28 = PyUnicode_Check(cpy_r_value);
    if (!cpy_r_r28) goto CPyL22;
    cpy_r_r29 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* "'" */
    CPy_INCREF(cpy_r_value);
    if (likely(PyUnicode_Check(cpy_r_value)))
        cpy_r_r30 = cpy_r_value;
    else {
        CPy_TypeErrorTraceback("y/_db/utils/stringify.py", "stringify_column_value", 58, CPyStatic_stringify___globals, "str", cpy_r_value);
        goto CPyL48;
    }
    cpy_r_r31 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* "'" */
    cpy_r_r32 = CPyStr_Build(3, cpy_r_r29, cpy_r_r30, cpy_r_r31);
    CPy_DECREF(cpy_r_r30);
    if (unlikely(cpy_r_r32 == NULL)) {
        CPy_AddTraceback("y/_db/utils/stringify.py", "stringify_column_value", DIFFCHECK_PLACEHOLDER, CPyStatic_stringify___globals);
        goto CPyL48;
    }
    return cpy_r_r32;
CPyL22: ;
    cpy_r_r33 = (PyObject *)&PyLong_Type;
    cpy_r_r34 = CPyStatic_stringify___globals;
    cpy_r_r35 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'Decimal' */
    cpy_r_r36 = CPyDict_GetItem(cpy_r_r34, cpy_r_r35);
    if (unlikely(cpy_r_r36 == NULL)) {
        CPy_AddTraceback("y/_db/utils/stringify.py", "stringify_column_value", DIFFCHECK_PLACEHOLDER, CPyStatic_stringify___globals);
        goto CPyL48;
    }
    CPy_INCREF(cpy_r_r33);
    cpy_r_r37.f0 = cpy_r_r33;
    cpy_r_r37.f1 = cpy_r_r36;
    cpy_r_r38 = PyTuple_New(2);
    if (unlikely(cpy_r_r38 == NULL))
        CPyError_OutOfMemory();
    PyObject *__tmp96 = cpy_r_r37.f0;
    PyTuple_SET_ITEM(cpy_r_r38, 0, __tmp96);
    PyObject *__tmp97 = cpy_r_r37.f1;
    PyTuple_SET_ITEM(cpy_r_r38, 1, __tmp97);
    cpy_r_r39 = PyObject_IsInstance(cpy_r_value, cpy_r_r38);
    CPy_DECREF(cpy_r_r38);
    cpy_r_r40 = cpy_r_r39 >= 0;
    if (unlikely(!cpy_r_r40)) {
        CPy_AddTraceback("y/_db/utils/stringify.py", "stringify_column_value", DIFFCHECK_PLACEHOLDER, CPyStatic_stringify___globals);
        goto CPyL48;
    }
    cpy_r_r41 = cpy_r_r39;
    if (!cpy_r_r41) goto CPyL27;
    cpy_r_r42 = PyObject_Str(cpy_r_value);
    if (unlikely(cpy_r_r42 == NULL)) {
        CPy_AddTraceback("y/_db/utils/stringify.py", "stringify_column_value", DIFFCHECK_PLACEHOLDER, CPyStatic_stringify___globals);
        goto CPyL48;
    }
    return cpy_r_r42;
CPyL27: ;
    cpy_r_r43 = CPyStatic_stringify___globals;
    cpy_r_r44 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'datetime' */
    cpy_r_r45 = CPyDict_GetItem(cpy_r_r43, cpy_r_r44);
    if (unlikely(cpy_r_r45 == NULL)) {
        CPy_AddTraceback("y/_db/utils/stringify.py", "stringify_column_value", DIFFCHECK_PLACEHOLDER, CPyStatic_stringify___globals);
        goto CPyL48;
    }
    cpy_r_r46 = PyObject_IsInstance(cpy_r_value, cpy_r_r45);
    CPy_DECREF(cpy_r_r45);
    cpy_r_r47 = cpy_r_r46 >= 0;
    if (unlikely(!cpy_r_r47)) {
        CPy_AddTraceback("y/_db/utils/stringify.py", "stringify_column_value", DIFFCHECK_PLACEHOLDER, CPyStatic_stringify___globals);
        goto CPyL48;
    }
    cpy_r_r48 = cpy_r_r46;
    if (!cpy_r_r48) goto CPyL44;
    cpy_r_r49 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* "'" */
    cpy_r_r50 = CPyStatic_stringify___UTC;
    if (likely(cpy_r_r50 != NULL)) goto CPyL33;
    PyErr_SetString(PyExc_NameError, "value for final name \"UTC\" was not set");
    cpy_r_r51 = 0;
    if (unlikely(!cpy_r_r51)) {
        CPy_AddTraceback("y/_db/utils/stringify.py", "stringify_column_value", DIFFCHECK_PLACEHOLDER, CPyStatic_stringify___globals);
        goto CPyL48;
    }
    CPy_Unreachable();
CPyL33: ;
    cpy_r_r52 = CPyStatic_stringify___astimezone;
    if (likely(cpy_r_r52 != NULL)) goto CPyL36;
    PyErr_SetString(PyExc_NameError, "value for final name \"astimezone\" was not set");
    cpy_r_r53 = 0;
    if (unlikely(!cpy_r_r53)) {
        CPy_AddTraceback("y/_db/utils/stringify.py", "stringify_column_value", DIFFCHECK_PLACEHOLDER, CPyStatic_stringify___globals);
        goto CPyL48;
    }
    CPy_Unreachable();
CPyL36: ;
    PyObject *cpy_r_r54[2] = {cpy_r_value, cpy_r_r50};
    cpy_r_r55 = (PyObject **)&cpy_r_r54;
    cpy_r_r56 = PyObject_Vectorcall(cpy_r_r52, cpy_r_r55, 2, 0);
    if (unlikely(cpy_r_r56 == NULL)) {
        CPy_AddTraceback("y/_db/utils/stringify.py", "stringify_column_value", DIFFCHECK_PLACEHOLDER, CPyStatic_stringify___globals);
        goto CPyL48;
    }
    cpy_r_r57 = CPyStatic_stringify___isoformat;
    if (unlikely(cpy_r_r57 == NULL)) {
        goto CPyL50;
    } else
        goto CPyL40;
CPyL38: ;
    PyErr_SetString(PyExc_NameError, "value for final name \"isoformat\" was not set");
    cpy_r_r58 = 0;
    if (unlikely(!cpy_r_r58)) {
        CPy_AddTraceback("y/_db/utils/stringify.py", "stringify_column_value", DIFFCHECK_PLACEHOLDER, CPyStatic_stringify___globals);
        goto CPyL48;
    }
    CPy_Unreachable();
CPyL40: ;
    PyObject *cpy_r_r59[1] = {cpy_r_r56};
    cpy_r_r60 = (PyObject **)&cpy_r_r59;
    cpy_r_r61 = PyObject_Vectorcall(cpy_r_r57, cpy_r_r60, 1, 0);
    if (unlikely(cpy_r_r61 == NULL)) {
        CPy_AddTraceback("y/_db/utils/stringify.py", "stringify_column_value", DIFFCHECK_PLACEHOLDER, CPyStatic_stringify___globals);
        goto CPyL51;
    }
    CPy_DECREF(cpy_r_r56);
    if (likely(PyUnicode_Check(cpy_r_r61)))
        cpy_r_r62 = cpy_r_r61;
    else {
        CPy_TypeErrorTraceback("y/_db/utils/stringify.py", "stringify_column_value", 62, CPyStatic_stringify___globals, "str", cpy_r_r61);
        goto CPyL48;
    }
    cpy_r_r63 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* "'" */
    cpy_r_r64 = CPyStr_Build(3, cpy_r_r49, cpy_r_r62, cpy_r_r63);
    CPy_DECREF(cpy_r_r62);
    if (unlikely(cpy_r_r64 == NULL)) {
        CPy_AddTraceback("y/_db/utils/stringify.py", "stringify_column_value", DIFFCHECK_PLACEHOLDER, CPyStatic_stringify___globals);
        goto CPyL48;
    }
    return cpy_r_r64;
CPyL44: ;
    cpy_r_r65 = CPy_TYPE(cpy_r_value);
    cpy_r_r66 = CPyModule_builtins;
    cpy_r_r67 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'NotImplementedError' */
    cpy_r_r68 = CPyObject_GetAttr(cpy_r_r66, cpy_r_r67);
    if (unlikely(cpy_r_r68 == NULL)) {
        CPy_AddTraceback("y/_db/utils/stringify.py", "stringify_column_value", DIFFCHECK_PLACEHOLDER, CPyStatic_stringify___globals);
        goto CPyL52;
    }
    PyObject *cpy_r_r69[2] = {cpy_r_r65, cpy_r_value};
    cpy_r_r70 = (PyObject **)&cpy_r_r69;
    cpy_r_r71 = PyObject_Vectorcall(cpy_r_r68, cpy_r_r70, 2, 0);
    CPy_DECREF(cpy_r_r68);
    if (unlikely(cpy_r_r71 == NULL)) {
        CPy_AddTraceback("y/_db/utils/stringify.py", "stringify_column_value", DIFFCHECK_PLACEHOLDER, CPyStatic_stringify___globals);
        goto CPyL52;
    }
    CPy_DECREF(cpy_r_r65);
    CPy_Raise(cpy_r_r71);
    CPy_DECREF(cpy_r_r71);
    if (unlikely(!0)) {
        CPy_AddTraceback("y/_db/utils/stringify.py", "stringify_column_value", DIFFCHECK_PLACEHOLDER, CPyStatic_stringify___globals);
        goto CPyL48;
    }
    CPy_Unreachable();
CPyL48: ;
    cpy_r_r72 = NULL;
    return cpy_r_r72;
CPyL49: ;
    CPy_DecRef(cpy_r_r14);
    goto CPyL48;
CPyL50: ;
    CPy_DecRef(cpy_r_r56);
    goto CPyL38;
CPyL51: ;
    CPy_DecRef(cpy_r_r56);
    goto CPyL48;
CPyL52: ;
    CPy_DecRef(cpy_r_r65);
    goto CPyL48;
}

PyObject *CPyPy_stringify___stringify_column_value(PyObject *self, PyObject *const *args, size_t nargs, PyObject *kwnames) {
    static const char * const kwlist[] = {"value", "provider", 0};
    static CPyArg_Parser parser = {"OO:stringify_column_value", kwlist, 0};
    PyObject *obj_value;
    PyObject *obj_provider;
    if (!CPyArg_ParseStackAndKeywordsSimple(args, nargs, kwnames, &parser, &obj_value, &obj_provider)) {
        return NULL;
    }
    PyObject *arg_value = obj_value;
    PyObject *arg_provider;
    if (likely(PyUnicode_Check(obj_provider)))
        arg_provider = obj_provider;
    else {
        CPy_TypeError("str", obj_provider); 
        goto fail;
    }
    PyObject *retval = CPyDef_stringify___stringify_column_value(arg_value, arg_provider);
    return retval;
fail: ;
    CPy_AddTraceback("y/_db/utils/stringify.py", "stringify_column_value", DIFFCHECK_PLACEHOLDER, CPyStatic_stringify___globals);
    return NULL;
}

PyObject *CPyDef_stringify___build_row(PyObject *cpy_r_row, PyObject *cpy_r_provider) {
    PyObject *cpy_r_r0;
    PyObject *cpy_r_r1;
    PyObject *cpy_r_r2;
    PyObject *cpy_r_r3;
    PyObject *cpy_r_r4;
    PyObject *cpy_r_r5;
    int32_t cpy_r_r6;
    char cpy_r_r7;
    char cpy_r_r8;
    PyObject *cpy_r_r9;
    PyObject *cpy_r_r10;
    PyObject *cpy_r_r11;
    PyObject *cpy_r_r12;
    cpy_r_r0 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* '(' */
    cpy_r_r1 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* ',' */
    cpy_r_r2 = PyList_New(0);
    if (unlikely(cpy_r_r2 == NULL)) {
        CPy_AddTraceback("y/_db/utils/stringify.py", "build_row", DIFFCHECK_PLACEHOLDER, CPyStatic_stringify___globals);
        goto CPyL9;
    }
    cpy_r_r3 = PyObject_GetIter(cpy_r_row);
    if (unlikely(cpy_r_r3 == NULL)) {
        CPy_AddTraceback("y/_db/utils/stringify.py", "build_row", DIFFCHECK_PLACEHOLDER, CPyStatic_stringify___globals);
        goto CPyL10;
    }
CPyL2: ;
    cpy_r_r4 = PyIter_Next(cpy_r_r3);
    if (cpy_r_r4 == NULL) goto CPyL11;
    cpy_r_r5 = CPyDef_stringify___stringify_column_value(cpy_r_r4, cpy_r_provider);
    CPy_DECREF(cpy_r_r4);
    if (unlikely(cpy_r_r5 == NULL)) {
        CPy_AddTraceback("y/_db/utils/stringify.py", "build_row", DIFFCHECK_PLACEHOLDER, CPyStatic_stringify___globals);
        goto CPyL12;
    }
    cpy_r_r6 = PyList_Append(cpy_r_r2, cpy_r_r5);
    CPy_DECREF(cpy_r_r5);
    cpy_r_r7 = cpy_r_r6 >= 0;
    if (unlikely(!cpy_r_r7)) {
        CPy_AddTraceback("y/_db/utils/stringify.py", "build_row", DIFFCHECK_PLACEHOLDER, CPyStatic_stringify___globals);
        goto CPyL12;
    } else
        goto CPyL2;
CPyL5: ;
    cpy_r_r8 = CPy_NoErrOccurred();
    if (unlikely(!cpy_r_r8)) {
        CPy_AddTraceback("y/_db/utils/stringify.py", "build_row", DIFFCHECK_PLACEHOLDER, CPyStatic_stringify___globals);
        goto CPyL10;
    }
    cpy_r_r9 = PyUnicode_Join(cpy_r_r1, cpy_r_r2);
    CPy_DECREF_NO_IMM(cpy_r_r2);
    if (unlikely(cpy_r_r9 == NULL)) {
        CPy_AddTraceback("y/_db/utils/stringify.py", "build_row", DIFFCHECK_PLACEHOLDER, CPyStatic_stringify___globals);
        goto CPyL9;
    }
    cpy_r_r10 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* ')' */
    cpy_r_r11 = CPyStr_Build(3, cpy_r_r0, cpy_r_r9, cpy_r_r10);
    CPy_DECREF(cpy_r_r9);
    if (unlikely(cpy_r_r11 == NULL)) {
        CPy_AddTraceback("y/_db/utils/stringify.py", "build_row", DIFFCHECK_PLACEHOLDER, CPyStatic_stringify___globals);
        goto CPyL9;
    }
    return cpy_r_r11;
CPyL9: ;
    cpy_r_r12 = NULL;
    return cpy_r_r12;
CPyL10: ;
    CPy_DecRef(cpy_r_r2);
    goto CPyL9;
CPyL11: ;
    CPy_DECREF(cpy_r_r3);
    goto CPyL5;
CPyL12: ;
    CPy_DecRef(cpy_r_r2);
    CPy_DecRef(cpy_r_r3);
    goto CPyL9;
}

PyObject *CPyPy_stringify___build_row(PyObject *self, PyObject *const *args, size_t nargs, PyObject *kwnames) {
    static const char * const kwlist[] = {"row", "provider", 0};
    static CPyArg_Parser parser = {"OO:build_row", kwlist, 0};
    PyObject *obj_row;
    PyObject *obj_provider;
    if (!CPyArg_ParseStackAndKeywordsSimple(args, nargs, kwnames, &parser, &obj_row, &obj_provider)) {
        return NULL;
    }
    PyObject *arg_row = obj_row;
    PyObject *arg_provider;
    if (likely(PyUnicode_Check(obj_provider)))
        arg_provider = obj_provider;
    else {
        CPy_TypeError("str", obj_provider); 
        goto fail;
    }
    PyObject *retval = CPyDef_stringify___build_row(arg_row, arg_provider);
    return retval;
fail: ;
    CPy_AddTraceback("y/_db/utils/stringify.py", "build_row", DIFFCHECK_PLACEHOLDER, CPyStatic_stringify___globals);
    return NULL;
}

PyObject *CPyDef_stringify___build_query(PyObject *cpy_r_provider_name, PyObject *cpy_r_entity_name, PyObject *cpy_r_columns, PyObject *cpy_r_items) {
    PyObject *cpy_r_r0;
    PyObject *cpy_r_r1;
    PyObject *cpy_r_r2;
    PyObject *cpy_r_r3;
    PyObject *cpy_r_r4;
    int32_t cpy_r_r5;
    char cpy_r_r6;
    char cpy_r_r7;
    PyObject *cpy_r_r8;
    PyObject *cpy_r_r9;
    char cpy_r_r10;
    PyObject *cpy_r_r11;
    PyObject *cpy_r_r12;
    PyObject *cpy_r_r13;
    PyObject *cpy_r_r14;
    PyObject *cpy_r_r15;
    PyObject *cpy_r_r16;
    PyObject *cpy_r_r17;
    char cpy_r_r18;
    PyObject *cpy_r_r19;
    PyObject *cpy_r_r20;
    PyObject *cpy_r_r21;
    PyObject *cpy_r_r22;
    PyObject *cpy_r_r23;
    PyObject *cpy_r_r24;
    PyObject *cpy_r_r25;
    PyObject *cpy_r_r26;
    PyObject *cpy_r_r27;
    PyObject *cpy_r_r28;
    PyObject **cpy_r_r30;
    PyObject *cpy_r_r31;
    PyObject *cpy_r_r32;
    cpy_r_r0 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* ',' */
    cpy_r_r1 = PyList_New(0);
    if (unlikely(cpy_r_r1 == NULL)) {
        CPy_AddTraceback("y/_db/utils/stringify.py", "build_query", DIFFCHECK_PLACEHOLDER, CPyStatic_stringify___globals);
        goto CPyL19;
    }
    cpy_r_r2 = PyObject_GetIter(cpy_r_items);
    if (unlikely(cpy_r_r2 == NULL)) {
        CPy_AddTraceback("y/_db/utils/stringify.py", "build_query", DIFFCHECK_PLACEHOLDER, CPyStatic_stringify___globals);
        goto CPyL20;
    }
CPyL2: ;
    cpy_r_r3 = PyIter_Next(cpy_r_r2);
    if (cpy_r_r3 == NULL) goto CPyL21;
    cpy_r_r4 = CPyDef_stringify___build_row(cpy_r_r3, cpy_r_provider_name);
    CPy_DECREF(cpy_r_r3);
    if (unlikely(cpy_r_r4 == NULL)) {
        CPy_AddTraceback("y/_db/utils/stringify.py", "build_query", DIFFCHECK_PLACEHOLDER, CPyStatic_stringify___globals);
        goto CPyL22;
    }
    cpy_r_r5 = PyList_Append(cpy_r_r1, cpy_r_r4);
    CPy_DECREF(cpy_r_r4);
    cpy_r_r6 = cpy_r_r5 >= 0;
    if (unlikely(!cpy_r_r6)) {
        CPy_AddTraceback("y/_db/utils/stringify.py", "build_query", DIFFCHECK_PLACEHOLDER, CPyStatic_stringify___globals);
        goto CPyL22;
    } else
        goto CPyL2;
CPyL5: ;
    cpy_r_r7 = CPy_NoErrOccurred();
    if (unlikely(!cpy_r_r7)) {
        CPy_AddTraceback("y/_db/utils/stringify.py", "build_query", DIFFCHECK_PLACEHOLDER, CPyStatic_stringify___globals);
        goto CPyL20;
    }
    cpy_r_r8 = PyUnicode_Join(cpy_r_r0, cpy_r_r1);
    CPy_DECREF_NO_IMM(cpy_r_r1);
    if (unlikely(cpy_r_r8 == NULL)) {
        CPy_AddTraceback("y/_db/utils/stringify.py", "build_query", DIFFCHECK_PLACEHOLDER, CPyStatic_stringify___globals);
        goto CPyL19;
    }
    cpy_r_r9 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'sqlite' */
    cpy_r_r10 = CPyStr_EqualLiteral(cpy_r_provider_name, cpy_r_r9, 6);
    if (!cpy_r_r10) goto CPyL11;
    cpy_r_r11 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'insert or ignore into ' */
    cpy_r_r12 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* ' (' */
    cpy_r_r13 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* ',' */
    cpy_r_r14 = PyUnicode_Join(cpy_r_r13, cpy_r_columns);
    if (unlikely(cpy_r_r14 == NULL)) {
        CPy_AddTraceback("y/_db/utils/stringify.py", "build_query", DIFFCHECK_PLACEHOLDER, CPyStatic_stringify___globals);
        goto CPyL23;
    }
    cpy_r_r15 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* ') values ' */
    cpy_r_r16 = CPyStr_Build(6, cpy_r_r11, cpy_r_entity_name, cpy_r_r12, cpy_r_r14, cpy_r_r15, cpy_r_r8);
    CPy_DECREF(cpy_r_r14);
    CPy_DECREF(cpy_r_r8);
    if (unlikely(cpy_r_r16 == NULL)) {
        CPy_AddTraceback("y/_db/utils/stringify.py", "build_query", DIFFCHECK_PLACEHOLDER, CPyStatic_stringify___globals);
        goto CPyL19;
    }
    return cpy_r_r16;
CPyL11: ;
    cpy_r_r17 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'postgres' */
    cpy_r_r18 = CPyStr_EqualLiteral(cpy_r_provider_name, cpy_r_r17, 8);
    if (!cpy_r_r18) goto CPyL24;
    cpy_r_r19 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'insert into ' */
    cpy_r_r20 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* ' (' */
    cpy_r_r21 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* ',' */
    cpy_r_r22 = PyUnicode_Join(cpy_r_r21, cpy_r_columns);
    if (unlikely(cpy_r_r22 == NULL)) {
        CPy_AddTraceback("y/_db/utils/stringify.py", "build_query", DIFFCHECK_PLACEHOLDER, CPyStatic_stringify___globals);
        goto CPyL23;
    }
    cpy_r_r23 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* ') values ' */
    cpy_r_r24 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* ' on conflict do nothing' */
    cpy_r_r25 = CPyStr_Build(7, cpy_r_r19, cpy_r_entity_name, cpy_r_r20, cpy_r_r22, cpy_r_r23, cpy_r_r8, cpy_r_r24);
    CPy_DECREF(cpy_r_r22);
    CPy_DECREF(cpy_r_r8);
    if (unlikely(cpy_r_r25 == NULL)) {
        CPy_AddTraceback("y/_db/utils/stringify.py", "build_query", DIFFCHECK_PLACEHOLDER, CPyStatic_stringify___globals);
        goto CPyL19;
    }
    return cpy_r_r25;
CPyL15: ;
    cpy_r_r26 = CPyModule_builtins;
    cpy_r_r27 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'NotImplementedError' */
    cpy_r_r28 = CPyObject_GetAttr(cpy_r_r26, cpy_r_r27);
    if (unlikely(cpy_r_r28 == NULL)) {
        CPy_AddTraceback("y/_db/utils/stringify.py", "build_query", DIFFCHECK_PLACEHOLDER, CPyStatic_stringify___globals);
        goto CPyL19;
    }
    PyObject *cpy_r_r29[1] = {cpy_r_provider_name};
    cpy_r_r30 = (PyObject **)&cpy_r_r29;
    cpy_r_r31 = PyObject_Vectorcall(cpy_r_r28, cpy_r_r30, 1, 0);
    CPy_DECREF(cpy_r_r28);
    if (unlikely(cpy_r_r31 == NULL)) {
        CPy_AddTraceback("y/_db/utils/stringify.py", "build_query", DIFFCHECK_PLACEHOLDER, CPyStatic_stringify___globals);
        goto CPyL19;
    }
    CPy_Raise(cpy_r_r31);
    CPy_DECREF(cpy_r_r31);
    if (unlikely(!0)) {
        CPy_AddTraceback("y/_db/utils/stringify.py", "build_query", DIFFCHECK_PLACEHOLDER, CPyStatic_stringify___globals);
        goto CPyL19;
    }
    CPy_Unreachable();
CPyL19: ;
    cpy_r_r32 = NULL;
    return cpy_r_r32;
CPyL20: ;
    CPy_DecRef(cpy_r_r1);
    goto CPyL19;
CPyL21: ;
    CPy_DECREF(cpy_r_r2);
    goto CPyL5;
CPyL22: ;
    CPy_DecRef(cpy_r_r1);
    CPy_DecRef(cpy_r_r2);
    goto CPyL19;
CPyL23: ;
    CPy_DecRef(cpy_r_r8);
    goto CPyL19;
CPyL24: ;
    CPy_DECREF(cpy_r_r8);
    goto CPyL15;
}

PyObject *CPyPy_stringify___build_query(PyObject *self, PyObject *const *args, size_t nargs, PyObject *kwnames) {
    static const char * const kwlist[] = {"provider_name", "entity_name", "columns", "items", 0};
    static CPyArg_Parser parser = {"OOOO:build_query", kwlist, 0};
    PyObject *obj_provider_name;
    PyObject *obj_entity_name;
    PyObject *obj_columns;
    PyObject *obj_items;
    if (!CPyArg_ParseStackAndKeywordsSimple(args, nargs, kwnames, &parser, &obj_provider_name, &obj_entity_name, &obj_columns, &obj_items)) {
        return NULL;
    }
    PyObject *arg_provider_name;
    if (likely(PyUnicode_Check(obj_provider_name)))
        arg_provider_name = obj_provider_name;
    else {
        CPy_TypeError("str", obj_provider_name); 
        goto fail;
    }
    PyObject *arg_entity_name;
    if (likely(PyUnicode_Check(obj_entity_name)))
        arg_entity_name = obj_entity_name;
    else {
        CPy_TypeError("str", obj_entity_name); 
        goto fail;
    }
    PyObject *arg_columns = obj_columns;
    PyObject *arg_items = obj_items;
    PyObject *retval = CPyDef_stringify___build_query(arg_provider_name, arg_entity_name, arg_columns, arg_items);
    return retval;
fail: ;
    CPy_AddTraceback("y/_db/utils/stringify.py", "build_query", DIFFCHECK_PLACEHOLDER, CPyStatic_stringify___globals);
    return NULL;
}

char CPyDef_stringify_____top_level__(void) {
    PyObject *cpy_r_r0;
    PyObject *cpy_r_r1;
    char cpy_r_r2;
    PyObject *cpy_r_r3;
    PyObject *cpy_r_r4;
    PyObject *cpy_r_r5;
    PyObject *cpy_r_r6;
    PyObject *cpy_r_r7;
    PyObject *cpy_r_r8;
    PyObject *cpy_r_r9;
    PyObject *cpy_r_r10;
    PyObject *cpy_r_r11;
    PyObject *cpy_r_r12;
    PyObject *cpy_r_r13;
    PyObject *cpy_r_r14;
    PyObject *cpy_r_r15;
    PyObject *cpy_r_r16;
    PyObject *cpy_r_r17;
    PyObject *cpy_r_r18;
    PyObject *cpy_r_r19;
    PyObject *cpy_r_r20;
    PyObject *cpy_r_r21;
    PyObject *cpy_r_r22;
    PyObject *cpy_r_r23;
    int32_t cpy_r_r24;
    char cpy_r_r25;
    PyObject *cpy_r_r26;
    PyObject *cpy_r_r27;
    PyObject *cpy_r_r28;
    PyObject *cpy_r_r29;
    PyObject *cpy_r_r30;
    PyObject *cpy_r_r31;
    PyObject *cpy_r_r32;
    int32_t cpy_r_r33;
    char cpy_r_r34;
    PyObject *cpy_r_r35;
    PyObject *cpy_r_r36;
    PyObject *cpy_r_r37;
    PyObject *cpy_r_r38;
    PyObject *cpy_r_r39;
    PyObject *cpy_r_r40;
    PyObject *cpy_r_r41;
    int32_t cpy_r_r42;
    char cpy_r_r43;
    char cpy_r_r44;
    cpy_r_r0 = CPyModule_builtins;
    cpy_r_r1 = (PyObject *)&_Py_NoneStruct;
    cpy_r_r2 = cpy_r_r0 != cpy_r_r1;
    if (cpy_r_r2) goto CPyL3;
    cpy_r_r3 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'builtins' */
    cpy_r_r4 = PyImport_Import(cpy_r_r3);
    if (unlikely(cpy_r_r4 == NULL)) {
        CPy_AddTraceback("y/_db/utils/stringify.py", "<module>", -1, CPyStatic_stringify___globals);
        goto CPyL16;
    }
    CPyModule_builtins = cpy_r_r4;
    CPy_INCREF(CPyModule_builtins);
    CPy_DECREF(cpy_r_r4);
CPyL3: ;
    cpy_r_r5 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* ('datetime', 'timezone') */
    cpy_r_r6 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'datetime' */
    cpy_r_r7 = CPyStatic_stringify___globals;
    cpy_r_r8 = CPyImport_ImportFromMany(cpy_r_r6, cpy_r_r5, cpy_r_r5, cpy_r_r7);
    if (unlikely(cpy_r_r8 == NULL)) {
        CPy_AddTraceback("y/_db/utils/stringify.py", "<module>", DIFFCHECK_PLACEHOLDER, CPyStatic_stringify___globals);
        goto CPyL16;
    }
    CPyModule_datetime = cpy_r_r8;
    CPy_INCREF(CPyModule_datetime);
    CPy_DECREF(cpy_r_r8);
    cpy_r_r9 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* ('Decimal',) */
    cpy_r_r10 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'decimal' */
    cpy_r_r11 = CPyStatic_stringify___globals;
    cpy_r_r12 = CPyImport_ImportFromMany(cpy_r_r10, cpy_r_r9, cpy_r_r9, cpy_r_r11);
    if (unlikely(cpy_r_r12 == NULL)) {
        CPy_AddTraceback("y/_db/utils/stringify.py", "<module>", DIFFCHECK_PLACEHOLDER, CPyStatic_stringify___globals);
        goto CPyL16;
    }
    CPyModule_decimal = cpy_r_r12;
    CPy_INCREF(CPyModule_decimal);
    CPy_DECREF(cpy_r_r12);
    cpy_r_r13 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* ('Any', 'Final', 'Iterable') */
    cpy_r_r14 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'typing' */
    cpy_r_r15 = CPyStatic_stringify___globals;
    cpy_r_r16 = CPyImport_ImportFromMany(cpy_r_r14, cpy_r_r13, cpy_r_r13, cpy_r_r15);
    if (unlikely(cpy_r_r16 == NULL)) {
        CPy_AddTraceback("y/_db/utils/stringify.py", "<module>", DIFFCHECK_PLACEHOLDER, CPyStatic_stringify___globals);
        goto CPyL16;
    }
    CPyModule_typing = cpy_r_r16;
    CPy_INCREF(CPyModule_typing);
    CPy_DECREF(cpy_r_r16);
    cpy_r_r17 = CPyStatic_stringify___globals;
    cpy_r_r18 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'timezone' */
    cpy_r_r19 = CPyDict_GetItem(cpy_r_r17, cpy_r_r18);
    if (unlikely(cpy_r_r19 == NULL)) {
        CPy_AddTraceback("y/_db/utils/stringify.py", "<module>", DIFFCHECK_PLACEHOLDER, CPyStatic_stringify___globals);
        goto CPyL16;
    }
    cpy_r_r20 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'utc' */
    cpy_r_r21 = CPyObject_GetAttr(cpy_r_r19, cpy_r_r20);
    CPy_DECREF(cpy_r_r19);
    if (unlikely(cpy_r_r21 == NULL)) {
        CPy_AddTraceback("y/_db/utils/stringify.py", "<module>", DIFFCHECK_PLACEHOLDER, CPyStatic_stringify___globals);
        goto CPyL16;
    }
    CPyStatic_stringify___UTC = cpy_r_r21;
    CPy_INCREF(CPyStatic_stringify___UTC);
    cpy_r_r22 = CPyStatic_stringify___globals;
    cpy_r_r23 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'UTC' */
    cpy_r_r24 = CPyDict_SetItem(cpy_r_r22, cpy_r_r23, cpy_r_r21);
    CPy_DECREF(cpy_r_r21);
    cpy_r_r25 = cpy_r_r24 >= 0;
    if (unlikely(!cpy_r_r25)) {
        CPy_AddTraceback("y/_db/utils/stringify.py", "<module>", DIFFCHECK_PLACEHOLDER, CPyStatic_stringify___globals);
        goto CPyL16;
    }
    cpy_r_r26 = CPyStatic_stringify___globals;
    cpy_r_r27 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'datetime' */
    cpy_r_r28 = CPyDict_GetItem(cpy_r_r26, cpy_r_r27);
    if (unlikely(cpy_r_r28 == NULL)) {
        CPy_AddTraceback("y/_db/utils/stringify.py", "<module>", DIFFCHECK_PLACEHOLDER, CPyStatic_stringify___globals);
        goto CPyL16;
    }
    cpy_r_r29 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'astimezone' */
    cpy_r_r30 = CPyObject_GetAttr(cpy_r_r28, cpy_r_r29);
    CPy_DECREF(cpy_r_r28);
    if (unlikely(cpy_r_r30 == NULL)) {
        CPy_AddTraceback("y/_db/utils/stringify.py", "<module>", DIFFCHECK_PLACEHOLDER, CPyStatic_stringify___globals);
        goto CPyL16;
    }
    CPyStatic_stringify___astimezone = cpy_r_r30;
    CPy_INCREF(CPyStatic_stringify___astimezone);
    cpy_r_r31 = CPyStatic_stringify___globals;
    cpy_r_r32 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'astimezone' */
    cpy_r_r33 = CPyDict_SetItem(cpy_r_r31, cpy_r_r32, cpy_r_r30);
    CPy_DECREF(cpy_r_r30);
    cpy_r_r34 = cpy_r_r33 >= 0;
    if (unlikely(!cpy_r_r34)) {
        CPy_AddTraceback("y/_db/utils/stringify.py", "<module>", DIFFCHECK_PLACEHOLDER, CPyStatic_stringify___globals);
        goto CPyL16;
    }
    cpy_r_r35 = CPyStatic_stringify___globals;
    cpy_r_r36 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'datetime' */
    cpy_r_r37 = CPyDict_GetItem(cpy_r_r35, cpy_r_r36);
    if (unlikely(cpy_r_r37 == NULL)) {
        CPy_AddTraceback("y/_db/utils/stringify.py", "<module>", DIFFCHECK_PLACEHOLDER, CPyStatic_stringify___globals);
        goto CPyL16;
    }
    cpy_r_r38 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'isoformat' */
    cpy_r_r39 = CPyObject_GetAttr(cpy_r_r37, cpy_r_r38);
    CPy_DECREF(cpy_r_r37);
    if (unlikely(cpy_r_r39 == NULL)) {
        CPy_AddTraceback("y/_db/utils/stringify.py", "<module>", DIFFCHECK_PLACEHOLDER, CPyStatic_stringify___globals);
        goto CPyL16;
    }
    CPyStatic_stringify___isoformat = cpy_r_r39;
    CPy_INCREF(CPyStatic_stringify___isoformat);
    cpy_r_r40 = CPyStatic_stringify___globals;
    cpy_r_r41 = CPyStatics[DIFFCHECK_PLACEHOLDER]; /* 'isoformat' */
    cpy_r_r42 = CPyDict_SetItem(cpy_r_r40, cpy_r_r41, cpy_r_r39);
    CPy_DECREF(cpy_r_r39);
    cpy_r_r43 = cpy_r_r42 >= 0;
    if (unlikely(!cpy_r_r43)) {
        CPy_AddTraceback("y/_db/utils/stringify.py", "<module>", DIFFCHECK_PLACEHOLDER, CPyStatic_stringify___globals);
        goto CPyL16;
    }
    return 1;
CPyL16: ;
    cpy_r_r44 = 2;
    return cpy_r_r44;
}

int CPyGlobalsInit(void)
{
    static int is_initialized = 0;
    if (is_initialized) return 0;
    
    CPy_Init();
    CPyModule_y____db___brownie = Py_None;
    CPyModule_builtins = Py_None;
    CPyModule_hashlib = Py_None;
    CPyModule_json = Py_None;
    CPyModule_asyncio = Py_None;
    CPyModule_pathlib = Py_None;
    CPyModule_typing = Py_None;
    CPyModule_aiosqlite = Py_None;
    CPyModule_a_sync = Py_None;
    CPyModule_aiosqlite___context = Py_None;
    CPyModule_brownie____config = Py_None;
    CPyModule_brownie___exceptions = Py_None;
    CPyModule_brownie___network___contract = Py_None;
    CPyModule_brownie___project___build = Py_None;
    CPyModule_functools = Py_None;
    CPyModule_sqlite3 = Py_None;
    CPyModule_y___datatypes = Py_None;
    CPyModule_y____db___utils___stringify = Py_None;
    CPyModule_builtins = Py_None;
    CPyModule_datetime = Py_None;
    CPyModule_decimal = Py_None;
    CPyModule_typing = Py_None;
    if (CPyStatics_Initialize(CPyStatics, CPyLit_Str, CPyLit_Bytes, CPyLit_Int, CPyLit_Float, CPyLit_Complex, CPyLit_Tuple, CPyLit_FrozenSet) < 0) {
        return -1;
    }
    is_initialized = 1;
    return 0;
}

PyObject *CPyStatics[DIFFCHECK_PLACEHOLDER];
const char * const CPyLit_Str[] = {
    "\005\021already connected\fRuntimeError\t__aexit__\n__aenter__\aconnect",
    "\004\017isolation_level\aexecute\rGeneratorExit\rStopIteration",
    "\006\023NotImplementedError\bfetchone\001[\001{\023SELECT * FROM chain\006CONFIG",
    "\003\016active_network\achainid\bKeyError",
    "\0010Functionality not available in local environment",
    "\001\027BrownieEnvironmentError",
    "\0029Passed both params address and alias, should be only one!\nValueError",
    "\004\020_resolve_address\020 WHERE address=\'\001\'\016 WHERE alias=\'",
    "\006\025_get_select_statement\020OperationalError\003zip\005paths\003pop\016allSourcePaths",
    "\005\005pcMap\'SELECT source FROM sources WHERE hash=\?\bbuiltins\ahashlib\004json",
    "\b\020y/_db/brownie.py\b<module>\004Lock\aasyncio\004Path\apathlib\003Any\bCallable",
    "\t\tContainer\004Dict\005Final\aLiteral\bOptional\005Tuple\004cast\005final\006typing",
    "\005\taiosqlite\024SmartProcessingQueue\006a_sync\006Result\021aiosqlite.context",
    "\003\020_get_data_folder\017brownie._config\022brownie.exceptions",
    "\003\030brownie.network.contract\017DEPLOYMENT_KEYS\025brownie.project.build",
    "\006\tlru_cache\tfunctools\016InterfaceError\asqlite3\aAddress\vy.datatypes",
    "\b\aaddress\005alias\003abi\003ast\bbytecode\bcompiler\fcontractName\020deployedBytecode",
    "\a\021deployedSourceMap\blanguage\anatspec\aopcodes\tsourceMap\004type\tSourceKey",
    "\006\tBuildJson\aSources\vSOURCE_KEYS\vcoverageMap\023DISCARD_SOURCE_KEYS\004sha1",
    "\a\005dumps\005loads\vsqlite_lock\ry._db.brownie\017__mypyc_attrs__\t_filename\003_db",
    "\006\n_connected\b_execute\vAsyncCursor\016deployments.db\bjoinpath\003cur",
    "\t\vnum_workers\amaxsize\004null\bpostgres\b\'::bytea\006sqlite\002X\'\003hex\aDecimal",
    "\b\bdatetime\001(\001,\001)\026insert or ignore into \002 (\t) values \finsert into ",
    "\a\027 on conflict do nothing\btimezone\adecimal\bIterable\003utc\003UTC\nastimezone",
    "\001\tisoformat",
    "",
};
const char * const CPyLit_Bytes[] = {
    "",
};
const char * const CPyLit_Int[] = {
    "\0021\00032",
    "",
};
const double CPyLit_Float[] = {0};
const double CPyLit_Complex[] = {0};
const int CPyLit_Tuple[] = {
    23, 1, 8, 3, 38, 38, 38, 3, 39, 39, 39, 2, 136, 137, 1, 42, 1, 44,
    10, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 3, 57, 57, 57, 1, 142, 1,
    58, 1, 60, 2, 17, 62, 1, 22, 1, 25, 1, 66, 1, 68, 2, 70, 30, 1, 72, 1,
    108, 1, 109, 2, 117, 126, 1, 116, 3, 46, 50, 128
};
const int CPyLit_FrozenSet[] = {0};
CPyModule *CPyModule_y____db___brownie__internal = NULL;
CPyModule *CPyModule_y____db___brownie;
PyObject *CPyStatic_brownie___globals;
CPyModule *CPyModule_builtins;
CPyModule *CPyModule_hashlib;
CPyModule *CPyModule_json;
CPyModule *CPyModule_asyncio;
CPyModule *CPyModule_pathlib;
CPyModule *CPyModule_typing;
CPyModule *CPyModule_aiosqlite;
CPyModule *CPyModule_a_sync;
CPyModule *CPyModule_aiosqlite___context;
CPyModule *CPyModule_brownie____config;
CPyModule *CPyModule_brownie___exceptions;
CPyModule *CPyModule_brownie___network___contract;
CPyModule *CPyModule_brownie___project___build;
CPyModule *CPyModule_functools;
CPyModule *CPyModule_sqlite3;
CPyModule *CPyModule_y___datatypes;
CPyModule *CPyModule_y____db___utils___stringify__internal = NULL;
CPyModule *CPyModule_y____db___utils___stringify;
PyObject *CPyStatic_stringify___globals;
CPyModule *CPyModule_datetime;
CPyModule *CPyModule_decimal;
tuple_T16OOOOOOOOOOOOOOOO CPyStatic_brownie___SOURCE_KEYS = { NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL };
tuple_T8OOOOOOOO CPyStatic_brownie___DISCARD_SOURCE_KEYS = { NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL };
PyObject *CPyStatic_brownie___sha1 = NULL;
PyObject *CPyStatic_brownie___dumps = NULL;
PyObject *CPyStatic_brownie___loads = NULL;
PyObject *CPyStatic_brownie___sqlite_lock = NULL;
PyObject *CPyStatic_brownie___cur = NULL;
PyObject *CPyStatic_brownie___fetchone = NULL;
PyObject *CPyStatic_brownie___y____db___brownie____get_deployment___skip_source_keys = NULL;
PyTypeObject *CPyType_brownie___AsyncCursor;
PyObject *CPyDef_brownie___AsyncCursor(PyObject *cpy_r_filename);
PyTypeObject *CPyType_brownie___connect_AsyncCursor_gen;
PyObject *CPyDef_brownie___connect_AsyncCursor_gen(void);
CPyThreadLocal y____db___brownie___connect_AsyncCursor_genObject *brownie___connect_AsyncCursor_gen_free_instance;
PyTypeObject *CPyType_brownie___insert_AsyncCursor_gen;
PyObject *CPyDef_brownie___insert_AsyncCursor_gen(void);
CPyThreadLocal y____db___brownie___insert_AsyncCursor_genObject *brownie___insert_AsyncCursor_gen_free_instance;
PyTypeObject *CPyType_brownie___fetchone_AsyncCursor_gen;
PyObject *CPyDef_brownie___fetchone_AsyncCursor_gen(void);
CPyThreadLocal y____db___brownie___fetchone_AsyncCursor_genObject *brownie___fetchone_AsyncCursor_gen_free_instance;
PyTypeObject *CPyType_brownie____get_deployment_gen;
PyObject *CPyDef_brownie____get_deployment_gen(void);
CPyThreadLocal y____db___brownie____get_deployment_genObject *brownie____get_deployment_gen_free_instance;
PyTypeObject *CPyType_brownie_____fetch_source_for_hash_gen;
PyObject *CPyDef_brownie_____fetch_source_for_hash_gen(void);
CPyThreadLocal y____db___brownie_____fetch_source_for_hash_genObject *brownie_____fetch_source_for_hash_gen_free_instance;
char CPyDef_brownie___AsyncCursor_____init__(PyObject *cpy_r_self, PyObject *cpy_r_filename);
PyObject *CPyPy_brownie___AsyncCursor_____init__(PyObject *self, PyObject *args, PyObject *kw);
PyObject *CPyDef_brownie___connect_AsyncCursor_gen_____mypyc_generator_helper__(PyObject *cpy_r___mypyc_self__, PyObject *cpy_r_type, PyObject *cpy_r_value, PyObject *cpy_r_traceback, PyObject *cpy_r_arg, PyObject **cpy_r_stop_iter_ptr);
PyObject *CPyDef_brownie___connect_AsyncCursor_gen_____next__(PyObject *cpy_r___mypyc_self__);
PyObject *CPyPy_brownie___connect_AsyncCursor_gen_____next__(PyObject *self, PyObject *const *args, size_t nargs, PyObject *kwnames);
PyObject *CPyDef_brownie___connect_AsyncCursor_gen___send(PyObject *cpy_r___mypyc_self__, PyObject *cpy_r_arg);
PyObject *CPyPy_brownie___connect_AsyncCursor_gen___send(PyObject *self, PyObject *const *args, size_t nargs, PyObject *kwnames);
PyObject *CPyDef_brownie___connect_AsyncCursor_gen_____iter__(PyObject *cpy_r___mypyc_self__);
PyObject *CPyPy_brownie___connect_AsyncCursor_gen_____iter__(PyObject *self, PyObject *const *args, size_t nargs, PyObject *kwnames);
PyObject *CPyDef_brownie___connect_AsyncCursor_gen___throw(PyObject *cpy_r___mypyc_self__, PyObject *cpy_r_type, PyObject *cpy_r_value, PyObject *cpy_r_traceback);
PyObject *CPyPy_brownie___connect_AsyncCursor_gen___throw(PyObject *self, PyObject *const *args, size_t nargs, PyObject *kwnames);
PyObject *CPyDef_brownie___connect_AsyncCursor_gen___close(PyObject *cpy_r___mypyc_self__);
PyObject *CPyPy_brownie___connect_AsyncCursor_gen___close(PyObject *self, PyObject *const *args, size_t nargs, PyObject *kwnames);
PyObject *CPyDef_brownie___connect_AsyncCursor_gen_____await__(PyObject *cpy_r___mypyc_self__);
PyObject *CPyPy_brownie___connect_AsyncCursor_gen_____await__(PyObject *self, PyObject *const *args, size_t nargs, PyObject *kwnames);
PyObject *CPyDef_brownie___AsyncCursor___connect(PyObject *cpy_r_self);
PyObject *CPyPy_brownie___AsyncCursor___connect(PyObject *self, PyObject *const *args, size_t nargs, PyObject *kwnames);
PyObject *CPyDef_brownie___insert_AsyncCursor_gen_____mypyc_generator_helper__(PyObject *cpy_r___mypyc_self__, PyObject *cpy_r_type, PyObject *cpy_r_value, PyObject *cpy_r_traceback, PyObject *cpy_r_arg, PyObject **cpy_r_stop_iter_ptr);
PyObject *CPyDef_brownie___insert_AsyncCursor_gen_____next__(PyObject *cpy_r___mypyc_self__);
PyObject *CPyPy_brownie___insert_AsyncCursor_gen_____next__(PyObject *self, PyObject *const *args, size_t nargs, PyObject *kwnames);
PyObject *CPyDef_brownie___insert_AsyncCursor_gen___send(PyObject *cpy_r___mypyc_self__, PyObject *cpy_r_arg);
PyObject *CPyPy_brownie___insert_AsyncCursor_gen___send(PyObject *self, PyObject *const *args, size_t nargs, PyObject *kwnames);
PyObject *CPyDef_brownie___insert_AsyncCursor_gen_____iter__(PyObject *cpy_r___mypyc_self__);
PyObject *CPyPy_brownie___insert_AsyncCursor_gen_____iter__(PyObject *self, PyObject *const *args, size_t nargs, PyObject *kwnames);
PyObject *CPyDef_brownie___insert_AsyncCursor_gen___throw(PyObject *cpy_r___mypyc_self__, PyObject *cpy_r_type, PyObject *cpy_r_value, PyObject *cpy_r_traceback);
PyObject *CPyPy_brownie___insert_AsyncCursor_gen___throw(PyObject *self, PyObject *const *args, size_t nargs, PyObject *kwnames);
PyObject *CPyDef_brownie___insert_AsyncCursor_gen___close(PyObject *cpy_r___mypyc_self__);
PyObject *CPyPy_brownie___insert_AsyncCursor_gen___close(PyObject *self, PyObject *const *args, size_t nargs, PyObject *kwnames);
PyObject *CPyDef_brownie___insert_AsyncCursor_gen_____await__(PyObject *cpy_r___mypyc_self__);
PyObject *CPyPy_brownie___insert_AsyncCursor_gen_____await__(PyObject *self, PyObject *const *args, size_t nargs, PyObject *kwnames);
PyObject *CPyDef_brownie___AsyncCursor___insert(PyObject *cpy_r_self, PyObject *cpy_r_table, PyObject *cpy_r_values);
PyObject *CPyPy_brownie___AsyncCursor___insert(PyObject *self, PyObject *const *args, size_t nargs, PyObject *kwnames);
PyObject *CPyDef_brownie___fetchone_AsyncCursor_gen_____mypyc_generator_helper__(PyObject *cpy_r___mypyc_self__, PyObject *cpy_r_type, PyObject *cpy_r_value, PyObject *cpy_r_traceback, PyObject *cpy_r_arg, PyObject **cpy_r_stop_iter_ptr);
PyObject *CPyDef_brownie___fetchone_AsyncCursor_gen_____next__(PyObject *cpy_r___mypyc_self__);
PyObject *CPyPy_brownie___fetchone_AsyncCursor_gen_____next__(PyObject *self, PyObject *const *args, size_t nargs, PyObject *kwnames);
PyObject *CPyDef_brownie___fetchone_AsyncCursor_gen___send(PyObject *cpy_r___mypyc_self__, PyObject *cpy_r_arg);
PyObject *CPyPy_brownie___fetchone_AsyncCursor_gen___send(PyObject *self, PyObject *const *args, size_t nargs, PyObject *kwnames);
PyObject *CPyDef_brownie___fetchone_AsyncCursor_gen_____iter__(PyObject *cpy_r___mypyc_self__);
PyObject *CPyPy_brownie___fetchone_AsyncCursor_gen_____iter__(PyObject *self, PyObject *const *args, size_t nargs, PyObject *kwnames);
PyObject *CPyDef_brownie___fetchone_AsyncCursor_gen___throw(PyObject *cpy_r___mypyc_self__, PyObject *cpy_r_type, PyObject *cpy_r_value, PyObject *cpy_r_traceback);
PyObject *CPyPy_brownie___fetchone_AsyncCursor_gen___throw(PyObject *self, PyObject *const *args, size_t nargs, PyObject *kwnames);
PyObject *CPyDef_brownie___fetchone_AsyncCursor_gen___close(PyObject *cpy_r___mypyc_self__);
PyObject *CPyPy_brownie___fetchone_AsyncCursor_gen___close(PyObject *self, PyObject *const *args, size_t nargs, PyObject *kwnames);
PyObject *CPyDef_brownie___fetchone_AsyncCursor_gen_____await__(PyObject *cpy_r___mypyc_self__);
PyObject *CPyPy_brownie___fetchone_AsyncCursor_gen_____await__(PyObject *self, PyObject *const *args, size_t nargs, PyObject *kwnames);
PyObject *CPyDef_brownie___AsyncCursor___fetchone(PyObject *cpy_r_self, PyObject *cpy_r_cmd, PyObject *cpy_r_args);
PyObject *CPyPy_brownie___AsyncCursor___fetchone(PyObject *self, PyObject *const *args, size_t nargs, PyObject *kwnames);
PyObject *CPyDef_brownie____get_select_statement(void);
PyObject *CPyPy_brownie____get_select_statement(PyObject *self, PyObject *const *args, size_t nargs, PyObject *kwnames);
PyObject *CPyDef_brownie____get_deployment_gen_____mypyc_generator_helper__(PyObject *cpy_r___mypyc_self__, PyObject *cpy_r_type, PyObject *cpy_r_value, PyObject *cpy_r_traceback, PyObject *cpy_r_arg, PyObject **cpy_r_stop_iter_ptr);
PyObject *CPyDef_brownie____get_deployment_gen_____next__(PyObject *cpy_r___mypyc_self__);
PyObject *CPyPy_brownie____get_deployment_gen_____next__(PyObject *self, PyObject *const *args, size_t nargs, PyObject *kwnames);
PyObject *CPyDef_brownie____get_deployment_gen___send(PyObject *cpy_r___mypyc_self__, PyObject *cpy_r_arg);
PyObject *CPyPy_brownie____get_deployment_gen___send(PyObject *self, PyObject *const *args, size_t nargs, PyObject *kwnames);
PyObject *CPyDef_brownie____get_deployment_gen_____iter__(PyObject *cpy_r___mypyc_self__);
PyObject *CPyPy_brownie____get_deployment_gen_____iter__(PyObject *self, PyObject *const *args, size_t nargs, PyObject *kwnames);
PyObject *CPyDef_brownie____get_deployment_gen___throw(PyObject *cpy_r___mypyc_self__, PyObject *cpy_r_type, PyObject *cpy_r_value, PyObject *cpy_r_traceback);
PyObject *CPyPy_brownie____get_deployment_gen___throw(PyObject *self, PyObject *const *args, size_t nargs, PyObject *kwnames);
PyObject *CPyDef_brownie____get_deployment_gen___close(PyObject *cpy_r___mypyc_self__);
PyObject *CPyPy_brownie____get_deployment_gen___close(PyObject *self, PyObject *const *args, size_t nargs, PyObject *kwnames);
PyObject *CPyDef_brownie____get_deployment_gen_____await__(PyObject *cpy_r___mypyc_self__);
PyObject *CPyPy_brownie____get_deployment_gen_____await__(PyObject *self, PyObject *const *args, size_t nargs, PyObject *kwnames);
PyObject *CPyDef_brownie____get_deployment(PyObject *cpy_r_address, PyObject *cpy_r_alias, PyObject *cpy_r_skip_source_keys);
PyObject *CPyPy_brownie____get_deployment(PyObject *self, PyObject *const *args, size_t nargs, PyObject *kwnames);
PyObject *CPyDef_brownie_____fetch_source_for_hash_gen_____mypyc_generator_helper__(PyObject *cpy_r___mypyc_self__, PyObject *cpy_r_type, PyObject *cpy_r_value, PyObject *cpy_r_traceback, PyObject *cpy_r_arg, PyObject **cpy_r_stop_iter_ptr);
PyObject *CPyDef_brownie_____fetch_source_for_hash_gen_____next__(PyObject *cpy_r___mypyc_self__);
PyObject *CPyPy_brownie_____fetch_source_for_hash_gen_____next__(PyObject *self, PyObject *const *args, size_t nargs, PyObject *kwnames);
PyObject *CPyDef_brownie_____fetch_source_for_hash_gen___send(PyObject *cpy_r___mypyc_self__, PyObject *cpy_r_arg);
PyObject *CPyPy_brownie_____fetch_source_for_hash_gen___send(PyObject *self, PyObject *const *args, size_t nargs, PyObject *kwnames);
PyObject *CPyDef_brownie_____fetch_source_for_hash_gen_____iter__(PyObject *cpy_r___mypyc_self__);
PyObject *CPyPy_brownie_____fetch_source_for_hash_gen_____iter__(PyObject *self, PyObject *const *args, size_t nargs, PyObject *kwnames);
PyObject *CPyDef_brownie_____fetch_source_for_hash_gen___throw(PyObject *cpy_r___mypyc_self__, PyObject *cpy_r_type, PyObject *cpy_r_value, PyObject *cpy_r_traceback);
PyObject *CPyPy_brownie_____fetch_source_for_hash_gen___throw(PyObject *self, PyObject *const *args, size_t nargs, PyObject *kwnames);
PyObject *CPyDef_brownie_____fetch_source_for_hash_gen___close(PyObject *cpy_r___mypyc_self__);
PyObject *CPyPy_brownie_____fetch_source_for_hash_gen___close(PyObject *self, PyObject *const *args, size_t nargs, PyObject *kwnames);
PyObject *CPyDef_brownie_____fetch_source_for_hash_gen_____await__(PyObject *cpy_r___mypyc_self__);
PyObject *CPyPy_brownie_____fetch_source_for_hash_gen_____await__(PyObject *self, PyObject *const *args, size_t nargs, PyObject *kwnames);
PyObject *CPyDef_brownie_____fetch_source_for_hash(PyObject *cpy_r_hashval);
PyObject *CPyPy_brownie_____fetch_source_for_hash(PyObject *self, PyObject *const *args, size_t nargs, PyObject *kwnames);
char CPyDef_brownie_____top_level__(void);
PyObject *CPyStatic_stringify___UTC = NULL;
PyObject *CPyStatic_stringify___astimezone = NULL;
PyObject *CPyStatic_stringify___isoformat = NULL;
PyObject *CPyDef_stringify___stringify_column_value(PyObject *cpy_r_value, PyObject *cpy_r_provider);
PyObject *CPyPy_stringify___stringify_column_value(PyObject *self, PyObject *const *args, size_t nargs, PyObject *kwnames);
PyObject *CPyDef_stringify___build_row(PyObject *cpy_r_row, PyObject *cpy_r_provider);
PyObject *CPyPy_stringify___build_row(PyObject *self, PyObject *const *args, size_t nargs, PyObject *kwnames);
PyObject *CPyDef_stringify___build_query(PyObject *cpy_r_provider_name, PyObject *cpy_r_entity_name, PyObject *cpy_r_columns, PyObject *cpy_r_items);
PyObject *CPyPy_stringify___build_query(PyObject *self, PyObject *const *args, size_t nargs, PyObject *kwnames);
char CPyDef_stringify_____top_level__(void);

static int exec_ypricemagic__mypyc(PyObject *module)
{
    int res;
    PyObject *capsule;
    PyObject *tmp;
    
    extern PyObject *CPyInit_y____db___brownie(void);
    capsule = PyCapsule_New((void *)CPyInit_y____db___brownie, "ypricemagic__mypyc.init_y____db___brownie", NULL);
    if (!capsule) {
        goto fail;
    }
    res = PyObject_SetAttrString(module, "init_y____db___brownie", capsule);
    Py_DECREF(capsule);
    if (res < 0) {
        goto fail;
    }
    
    extern PyObject *CPyInit_y____db___utils___stringify(void);
    capsule = PyCapsule_New((void *)CPyInit_y____db___utils___stringify, "ypricemagic__mypyc.init_y____db___utils___stringify", NULL);
    if (!capsule) {
        goto fail;
    }
    res = PyObject_SetAttrString(module, "init_y____db___utils___stringify", capsule);
    Py_DECREF(capsule);
    if (res < 0) {
        goto fail;
    }
    
    return 0;
    fail:
    return -1;
}
static PyModuleDef module_def_ypricemagic__mypyc = {
    PyModuleDef_HEAD_INIT,
    .m_name = "ypricemagic__mypyc",
    .m_doc = NULL,
    .m_size = -1,
    .m_methods = NULL,
};
PyMODINIT_FUNC PyInit_ypricemagic__mypyc(void) {
    static PyObject *module = NULL;
    if (module) {
        Py_INCREF(module);
        return module;
    }
    module = PyModule_Create(&module_def_ypricemagic__mypyc);
    if (!module) {
        return NULL;
    }
    if (exec_ypricemagic__mypyc(module) < 0) {
        Py_DECREF(module);
        return NULL;
    }
    return module;
}
