import os

from setuptools.command.build_ext import build_ext
from setuptools._distutils.ccompiler import gen_lib_options
from setuptools._distutils import log


class ZigCompiler:
    """
    distutils doesn't provide us anyway of 'hooking' alternative compiler classes into the extension compilation steps.
    At the same time, we need info that only the initialised compiler class (subclass of CCompiler) has.

    Solution: a "subclass" ZigCompiler that overrides two methods: CCompiler.compile and CCompiler.link_shared_object.
    However instead of actually "subclassing" (which is not currently possible), we replace the methods at runtime,
    after the original compiler instance has been initialised with the relevant info (see 'build_extension' for this
    trick).
    """

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
        """
        Matches signature of distutils.CCompiler.compile
        """
        # This "initialize" step is exclusive to MSVC
        msvc = hasattr(self, "initialize")
        if msvc and not self.initialized:
            self.initialize()

        # Log level >= warn guarantees the output won't get swallowed
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
        # deduped_ppopts = []
        # for ppopt in pp_opts:
        #     if ppopt.lower() not in [p.lower() for p in deduped_ppopts]:
        #         deduped_ppopts.append(ppopt)

        cc_args = self._get_cc_args(pp_opts, debug, extra_preargs)
        log.warn("_get_cc_args returned %s", cc_args)
        for obj in objects:
            src, _ = build[obj]
            target = ["-target", "x86_64-windows-msvc"] if msvc else []
            self.spawn(
                [
                    "zig",
                    "build-obj",
                    "-O",
                    "ReleaseSafe",
                    *target,
                    "--library",
                    "c",
                    "-static",
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
        """
        Matches signature of distutils.CCompiler.compile
        """
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
        if hasattr(self, "linker_so"):
            log.warn("self.linker_so is %s", str(self.linker_so))
        self.mkpath(os.path.dirname(output_filename))

        # This "initialize" step is exclusive to MSVC
        msvc = hasattr(self, "initialize")
        # if msvc and not self.initialized:
        #     self.initialize()

        target = ["-target", "x86_64-windows-msvc"] if msvc else []

        lib_opts = [opt.replace("/LIBPATH:", "-L", 1) for opt in lib_opts]

        self.spawn(
            [
                "zig",
                "build-lib",
                "-O",
                "ReleaseSafe",
                *target,
                f"-femit-bin={output_filename}",
                "-fdll-export-fns",
                # The library dirs
                *[opt for opt in lib_opts if opt.startswith("-L")],
                *objects,
                *self.objects,
            ]
        )


class ZigBuilder(build_ext):
    def build_extension(self, ext):
        def override_instance_method(instance, method_name, target_class):
            """
            A trick to switch a method of an instance to an alternative implementation in another class at run time.
            """
            class_method = getattr(target_class, method_name)

            def new_method(*args, **kwargs):
                return class_method(instance, *args, **kwargs)

            setattr(instance, method_name, new_method)

        override_instance_method(self.compiler, "compile", ZigCompiler)
        # override_instance_method(self.compiler, "link_shared_object", ZigCompiler)
        self.compiler.src_extensions.append(".zig")
        super().build_extension(ext)
