#include <Python.h>

PyMODINIT_FUNC
PyInit_stringify(void)
{
    PyObject *tmp;
    if (!(tmp = PyImport_ImportModule("e48b665766e5f62102a4__mypyc"))) return NULL;
    PyObject *capsule = PyObject_GetAttrString(tmp, "init_y____db___utils___stringify");
    Py_DECREF(tmp);
    if (capsule == NULL) return NULL;
    void *init_func = PyCapsule_GetPointer(capsule, "e48b665766e5f62102a4__mypyc.init_y____db___utils___stringify");
    Py_DECREF(capsule);
    if (!init_func) {
        return NULL;
    }
    return ((PyObject *(*)(void))init_func)();
}

// distutils sometimes spuriously tells cl to export CPyInit___init__,
// so provide that so it chills out
PyMODINIT_FUNC PyInit___init__(void) { return PyInit_stringify(); }
