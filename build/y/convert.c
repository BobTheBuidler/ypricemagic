#include <Python.h>

PyMODINIT_FUNC
PyInit_convert(void)
{
    PyObject *tmp;
    if (!(tmp = PyImport_ImportModule("66d5967dfa0c4007d77b__mypyc"))) return NULL;
    PyObject *capsule = PyObject_GetAttrString(tmp, "init_y___convert");
    Py_DECREF(tmp);
    if (capsule == NULL) return NULL;
    void *init_func = PyCapsule_GetPointer(capsule, "66d5967dfa0c4007d77b__mypyc.init_y___convert");
    Py_DECREF(capsule);
    if (!init_func) {
        return NULL;
    }
    return ((PyObject *(*)(void))init_func)();
}

// distutils sometimes spuriously tells cl to export CPyInit___init__,
// so provide that so it chills out
PyMODINIT_FUNC PyInit___init__(void) { return PyInit_convert(); }
