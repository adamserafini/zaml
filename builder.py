import os
import platform
from setuptools.command.build_ext import build_ext
import sysconfig

class ZigBuilder(build_ext):
    def build_extension(self, ext):
        assert len(ext.sources) == 1

        if not os.path.exists(self.build_lib):
            os.makedirs(self.build_lib)
        mode = "Debug" if self.debug else "ReleaseFast"
        windows = platform.system() == "Windows"
        self.spawn(
            [
                "zig",
                "build-lib",
                "-O",
                mode,
                "-lc",
                *(["-target", "x86_64-windows-msvc"] if windows else []),
                f"-femit-bin={self.get_ext_fullpath(ext.name)}",
                "-fallow-shlib-undefined",
                "-dynamic",
                *[f"-I{d}" for d in self.include_dirs],
                *([f"-L{sysconfig.get_config_var('installed_base')}\Libs", "-lpython3"] if windows else []),
                ext.sources[0],
            ]
        )
