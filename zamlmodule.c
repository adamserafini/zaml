#define PY_SSIZE_T_CLEAN
#include <Python.h>

static PyObject *
zaml_load(PyObject *self, PyObject *args)
{
    return PyList_New(0);
}

static PyMethodDef ZamlMethods[] = {
    {"load", zaml_load, METH_VARARGS,
     "Load some tasty YAML."},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

static struct PyModuleDef zamlmodule = {
    PyModuleDef_HEAD_INIT,
    "spam",   /* name of module */
    NULL,     /* module documentation, may be NULL */
    -1,       /* size of per-interpreter state of the module,
                 or -1 if the module keeps state in global variables. */
    ZamlMethods
};

PyMODINIT_FUNC
PyInit_zaml(void)
{
    return PyModule_Create(&zamlmodule);
}
