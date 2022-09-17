import re
import os

from setuptools.command.build_ext import build_ext
from setuptools._distutils.ccompiler import CCompiler, gen_lib_options
from setuptools._distutils import log


def zig_spawn(original_spawn, cmd):
    cmd_str = " ".join(cmd)
    log.warn("original spawned command: %s", cmd_str)

    gcc_or_clang = cmd[0] == "clang" or cmd[0] == "gcc"
    if gcc_or_clang:
        """
        Example of compile step in clang:

        clang -Wno-unused-result -Wsign-compare -Wunreachable-code -DNDEBUG -g -fwrapv -O3 -Wall
        -I/Library/Developer/CommandLineTools/SDKs/MacOSX10.15.sdk/usr/include
        -I/Library/Developer/CommandLineTools/SDKs/MacOSX10.15.sdk/usr/include
        -I/Users/a.serafini/Projects/zaml/.venv/include
        -I/Users/a.serafini/.pyenv/versions/3.10.2/include/python3.10
        -c zamlmodule.zig
        -o build/temp.macosx-10.15-x86_64-3.10/zamlmodule.o

        Example of link step in clang:

        clang -bundle -undefined dynamic_lookup
        -L/usr/local/opt/readline/lib
        -L/Users/a.serafini/.pyenv/versions/3.10.2/lib
        -L/usr/local/opt/readline/lib
        -L/usr/local/opt/readline/lib
        -L/Users/a.serafini/.pyenv/versions/3.10.2/lib
        build/temp.macosx-10.15-x86_64-3.10/zamlmodule.o
        -o build/lib.macosx-10.15-x86_64-3.10/zaml.cpython-310-darwin.so
        """
        compile_step = " -c " in cmd_str
        if compile_step:
            original_spawn(
                [
                    "zig",
                    "build-obj",
                    "-O",
                    "ReleaseSafe",
                    f"-femit-bin={re.search(r' -o (.+)$', cmd_str).group(1)}",
                    *re.findall(
                        r"(-[I][^\s]+)", cmd_str
                    ),  # pass the -I/include/dirs to Zig
                    re.search(r" -c (\S+) -o ", cmd_str).group(
                        1
                    ),  # the Zig source file(s) to compile
                ]
            )
        else:
            # link step
            original_spawn(
                [
                    "zig",
                    "build-obj",
                    "-O",
                    "ReleaseSafe",
                    f"-femit-bin={re.search(r' -o (.+)$', cmd_str).group(1)}",
                    "-fallow-shlib-undefined",
                    "-dynamic",
                    re.search(r" dynamic_lookup (.+) -o ", cmd_str).group(
                        1
                    ),  # pass the -L/lib/dirs and object files to Zig
                ]
            )
    else:
        raise Exception("Unrecognized C compiler, cannot translate to zig CLI flags")


class ZigCompiler:
    def compile(
        self,
        sources,
        output_dir=None,
        macros=None,
        include_dirs=None,
        debug=0,
        extra_preargs=None,
        extra_postargs=None,
        depends=None,
    ):
        log.warn(
            "compile called with: sources: %s, output_dir: %s, macros: %s, include_dirs: %s, debug: %s, extra_preargs: %s, extra_postargs: %s, depends: %s",
            sources,
            output_dir,
            macros,
            include_dirs,
            debug,
            extra_preargs,
            extra_postargs,
            depends,
        )
        macros, objects, extra_postargs, pp_opts, build = self._setup_compile(
            output_dir, macros, include_dirs, sources, depends, extra_postargs
        )

        log.warn(
            "_setup_compile returned: macros: %s, objects: %s, extra_postargs: %s, pp_opts: %s, build: %s",
            macros,
            objects,
            extra_postargs,
            pp_opts,
            build,
        )
        cc_args = self._get_cc_args(pp_opts, debug, extra_preargs)
        log.warn("_get_cc_args returned %s", cc_args)
        for obj in objects:
            src, _ = build[obj]
            self.spawn(
                [
                    "zig",
                    "build-obj",
                    "-O",
                    "ReleaseSafe",
                    f"-femit-bin={obj}",
                    *pp_opts,
                    src,
                ]
            )

        return objects

    def link_shared_object(
        self,
        objects,
        output_filename,
        output_dir=None,
        libraries=None,
        library_dirs=None,
        runtime_library_dirs=None,
        export_symbols=None,
        debug=0,
        extra_preargs=None,
        extra_postargs=None,
        build_temp=None,
        target_lang=None,
    ):
        log.warn(
            "link_shared_object called with objects: %s, output_filename: %s, output_dir: %s, libraries: %s, library_dirs: %s, runtime_lirary_dirs: %s, export_symbols: %s, debug: %s, extra_preargs: %s, extra_postargs: %s, build_temp: %s, target_lang: %s",
            objects,
            output_filename,
            output_dir,
            libraries,
            library_dirs,
            runtime_library_dirs,
            export_symbols,
            debug,
            extra_preargs,
            extra_postargs,
            build_temp,
            target_lang,
        )
        objects, output_dir = self._fix_object_args(objects, output_dir)
        libraries, library_dirs, runtime_library_dirs = self._fix_lib_args(
            libraries, library_dirs, runtime_library_dirs
        )
        lib_opts = gen_lib_options(self, library_dirs, runtime_library_dirs, libraries)

        log.warn(
            "_fix_object_args returned objects: %s, output_dir: %s", objects, output_dir
        )
        log.warn(
            "_fix_lib_args returned libraries: %s, library_dirs: %s, runtime_library_dirs: %s",
            libraries,
            library_dirs,
            runtime_library_dirs,
        )
        log.warn("_need_link returned %s", self._need_link(objects, output_filename))
        log.warn("self.objects is %s", self.objects)
        log.warn("lib_opts is %s", lib_opts)
        log.warn("self.linker_so is %s", str(self.linker_so))
        self.mkpath(os.path.dirname(output_filename))
        self.spawn(
            [
                "zig",
                "build-lib",
                "-O",
                "ReleaseSafe",
                f"-femit-bin={output_filename}",
                "-fallow-shlib-undefined",
                "-dynamic",
                *[opt for opt in lib_opts if opt.startswith("-L/")],
                *objects,
                *self.objects,
            ]
        )


class ZigBuilder(build_ext):
    def build_extension(self, ext):
        # log.warn("compiler type is %s", type(self.compiler))
        print("what")
        print("compiler bases is", self.compiler.__class__.__bases__)
        self.compiler.src_extensions.append(".zig")
        super().build_extension(ext)

    def build_extensions(self):
        # Yep, this is crazy ;-)
        print("compiler bases is", self.compiler.__class__.__bases__)
        self.compiler.__class__.__bases__ = (
            ZigCompiler,
        ) + self.compiler.__class__.__bases__
        print("compiler bases is", self.compiler.__class__.__bases__)
        super().build_extensions()
        print("compiler bases is", self.compiler.__class__.__bases__)

    def swig_sources(self, *args, **kwargs):
        print("compiler bases is", self.compiler.__class__.__bases__)
        super().swig_sources(*args, **kwargs)
        print("compiler bases is", self.compiler.__class__.__bases__)

    def __getattribute__(self, name):
        import inspect

        returned = object.__getattribute__(self, name)
        if inspect.isfunction(returned) or inspect.ismethod(returned):
            print("called ", returned.__name__)
        return returned
