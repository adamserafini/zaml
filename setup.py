import os
import platform
import sysconfig
from pathlib import Path
from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext


class ZigBuilder(build_ext):
    def build_extension(self, ext):
        assert len(ext.sources) == 1

        if not os.path.exists(self.build_lib):
            os.makedirs(self.build_lib)
        windows = platform.system() == "Windows"
        self.spawn(
            [
                "zig",
                "build-lib",
                "-O",
                "ReleaseFast",
                "-lc",
                *(["-target", "x86_64-windows-msvc"] if windows else []),
                f"-femit-bin={self.get_ext_fullpath(ext.name)}",
                "-fallow-shlib-undefined",
                "-dynamic",
                *[f"-I{d}" for d in self.include_dirs],
                *(
                    [
                        f"-L{sysconfig.get_config_var('installed_base')}\Libs",
                        "-lpython3",
                    ]
                    if windows
                    else []
                ),
                ext.sources[0],
            ]
        )


zaml = Extension("zaml", sources=["zamlmodule.zig"])

setup(
    name="zaml",
    version="0.0.9",
    url="https://github.com/adamserafini/zaml",
    description="Fast YAML 1.2 Parser for Python 3.6+",
    ext_modules=[zaml],
    cmdclass={"build_ext": ZigBuilder},
    long_description=(Path(__file__).parent / "README.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    py_modules=["builder"],
)
