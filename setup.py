from setuptools import setup, Extension
import os
import platform
from setuptools.command.build_ext import build_ext
import sysconfig
from pathlib import Path

zaml = Extension("zaml", sources=["zamlmodule.zig"])


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


setup(
    name="zaml",
    version="0.0.5",
    description="Fast YAML 1.2 Parser for Python 3.6+",
    ext_modules=[zaml],
    cmdclass={"build_ext": ZigBuilder},
    long_description=(Path(__file__).parent / "README.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
)
