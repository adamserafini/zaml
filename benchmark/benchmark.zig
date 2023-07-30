const py = @cImport({
    @cDefine("PY_SSIZE_T_CLEAN", {});
    @cInclude("Python.h");
});

const std = @import("std");

// Zig library for parsing yaml
// https://github.com/kubkon/zig-yaml
const yaml = @import("libs/zig-yaml/src/yaml.zig");

const PyArg_ParseTuple = py.PyArg_ParseTuple;
const PyObject = py.PyObject;
const PyDict_New = py.PyDict_New;
const PyMethodDef = py.PyMethodDef;
const PyModuleDef = py.PyModuleDef;
const PyModuleDef_Base = py.PyModuleDef_Base;
const PyModule_Create = py.PyModule_Create;
const PyDict_SetItem = py.PyDict_SetItem;
const Py_BuildValue = py.Py_BuildValue;
const METH_VARARGS = py.METH_VARARGS;

// Would not use "testing" allocator for production
const test_allocator = std.testing.allocator;

// Don't think about using this in production, it probably has bugs + memory leaks
fn benchmark_load(self: [*c]PyObject, args: [*c]PyObject) callconv(.C) [*]PyObject {
    _ = self;

    var string: [*:0]const u8 = undefined;
    // TODO: handle errors / unexpected input. Probably not a good idea to silently ignore them.
    _ = PyArg_ParseTuple(args, "s", &string);

    // "catch unreachable" tells Zig compiler this can't possibly fail
    // Of course, it might fail: this is just a benchmark.
    // Did I mention not to use this in production?
    var untyped = yaml.Yaml.load(std.testing.allocator, std.mem.sliceTo(string, 0)) catch unreachable;
    // Free all memory at the end of the current scope
    defer untyped.deinit();

    // Our friend "catch unreachable" again :)
    var map = untyped.docs.items[0].asMap() catch unreachable;

    var dict = PyDict_New();

    const keys = map.keys();

    for (keys) |key| {
        const value = map.get(key) orelse unreachable;
        var pyKey = Py_BuildValue("s#", @ptrCast([*]const u8, key), key.len);
        var valueStr = value.asString() catch unreachable;
        const pyValue = Py_BuildValue("s#", @ptrCast([*]const u8, valueStr), valueStr.len);

        // TODO: again, we just ignore the potential errors that could happen here.
        // Don't do that in real life!
        _ = PyDict_SetItem(dict, pyKey, pyValue);
    }


    return Py_BuildValue("O", dict);
}

var BenchmarkMethods = [_]PyMethodDef{
    PyMethodDef{
        .ml_name = "load",
        .ml_meth = benchmark_load,
        .ml_flags = METH_VARARGS,
        .ml_doc = "Load some tasty YAML.",
    },
    PyMethodDef{
        .ml_name = null,
        .ml_meth = null,
        .ml_flags = 0,
        .ml_doc = null,
    },
};

var benchmarkmodule = PyModuleDef{
    .m_base = PyModuleDef_Base{
        .ob_base = PyObject{
            .ob_refcnt = 1,
            .ob_type = null,
        },
        .m_init = null,
        .m_index = 0,
        .m_copy = null,
    },
    .m_name = "benchmark",
    .m_doc = null,
    .m_size = -1,
    .m_methods = &BenchmarkMethods,
    .m_slots = null,
    .m_traverse = null,
    .m_clear = null,
    .m_free = null,
};

pub export fn PyInit_benchmark() [*]PyObject {
    return PyModule_Create(&benchmarkmodule);
}

