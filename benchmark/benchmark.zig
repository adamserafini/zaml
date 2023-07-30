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

var general_purpose_allocator = std.heap.GeneralPurposeAllocator(.{}){};

// Don't think about using this in production, it probably has bugs + memory leaks
fn benchmark_load(self: [*c]PyObject, args: [*c]PyObject) callconv(.C) [*c]PyObject {
    _ = self;

    var string: [*:0]const u8 = undefined;
    if (PyArg_ParseTuple(args, "s", &string) == 0) return null;

    var arena = std.heap.ArenaAllocator.init(general_purpose_allocator.allocator());
    defer arena.deinit();
    const allocator = arena.allocator();

    // TODO: remove 'catch unreachable' by catching the YamlError
    // https://github.com/kubkon/zig-yaml/blob/3d3c7ae400243a37c6b422b6cba7173656984897/src/yaml.zig#L17-L22
    // define and set an appropriate error
    // https://docs.python.org/3.9/extending/extending.html#intermezzo-errors-and-exceptions
    // and return null as above
    var untyped = yaml.Yaml.load(allocator, std.mem.sliceTo(string, 0)) catch unreachable;

    // TODO: same as TODO on ln 50 but maybe assert on `docs` size
    // Our friend "catch unreachable" again :)
    var map = untyped.docs.items[0].asMap() catch unreachable;

    var dict = PyDict_New();

    for (map.keys(), map.values()) |key, value| {
        // TODO: `value` type can be any of https://github.com/kubkon/zig-yaml/blob/3d3c7ae400243a37c6b422b6cba7173656984897/src/yaml.zig#L28-L33
        // Suggestion to handle the type appropriately
        // 1. Pattern match on value type
        // 2. Build the corresponsing PyObject https://docs.python.org/3.9/extending/extending.html#building-arbitrary-values
        // 3. Return its pointer

        var value_str = value.asString() catch unreachable;

        // TODO: again, we just ignore the potential errors that could happen here.
        // Don't do that in real life!
        const py_key_ptr: [*]const u8 = @ptrCast(key);
        const py_value_ptr: [*]const u8 = @ptrCast(value_str);

        const py_key = Py_BuildValue("s#", py_key_ptr, key.len);
        const py_value = Py_BuildValue("s#", py_value_ptr, value_str.len);
        _ = PyDict_SetItem(dict, py_key, py_value);
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
