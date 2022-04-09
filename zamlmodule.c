#define PY_SSIZE_T_CLEAN
#include <Python.h>

static PyObject *
zaml_load(PyObject *self, PyObject *args)
{
    return Py_BuildValue("i", 1);
}

static PyMethodDef ZamlMethods[] = {
    {.ml_name = "load",
     .ml_meth = zaml_load,
     .ml_flags = METH_VARARGS,
     .ml_doc = "Load some tasty YAML."},

    {.ml_name = NULL,
     .ml_meth = NULL,
     .ml_flags = 0,
     .ml_doc = NULL}        /* Sentinel */
};

static struct PyModuleDef zamlmodule = {
    .m_base = PyModuleDef_HEAD_INIT,
    .m_name = "spam",  /* name of module */
    .m_doc = NULL,     /* module documentation, may be NULL */
    .m_size = -1,      /* size of per-interpreter state of the module,
                         or -1 if the module keeps state in global variables. */
    .m_methods = ZamlMethods,
    .m_slots = NULL,
    .m_traverse = NULL,
    .m_clear = NULL,
    .m_free = NULL,
};

PyMODINIT_FUNC
PyInit_zaml(void)
{
    return PyModule_Create(&zamlmodule);
}
