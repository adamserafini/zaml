import re
from functools import partial

from setuptools.command.build_ext import build_ext
from setuptools._distutils import log


def zig_spawn(original_spawn, cmd):
    cmd_str = ' '.join(cmd)
    log.warn('original spawned command: %s', cmd_str)

    if cmd[0].endswith('clang'):
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
        compile_step = ' -c ' in cmd_str
        link_step = not compile_step
        original_spawn([
            "zig",
            "build-obj" if compile_step else "build-lib",
            "-O",
            "ReleaseSafe",
            f"-femit-bin={re.search(r'-o (.+)$', cmd_str).group(1)}",
            *(["-fallow-shlib-undefined"] if link_step else []),
            *(["-dynamic"] if link_step else []),
            *re.findall(r'(-[IL][^\s]+)', cmd_str),
            re.search(r" (\S+) -o", cmd_str).group(1)
        ])
    else:
        raise Exception("Unrecognized C compiler, cannot translate to zig CLI flags")


class ZigBuilder(build_ext):
    def build_extension(self, ext):
        original_spawn = self.compiler.spawn

        self.compiler.spawn = partial(zig_spawn, original_spawn)
        self.compiler.src_extensions.append('.zig')
        try:
            super().build_extension(ext)
        finally:
            self.compiler.zig_spawn = original_spawn
