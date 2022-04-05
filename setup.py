import os
from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext

zaml = Extension("zaml", sources=["zamlmodule.zig"])


class ZigBuilder(build_ext):
    def build_extension(self, ext):
        assert len(ext.sources) == 1

        if not os.path.exists(self.build_lib):
            os.mkdir(self.build_lib)
        self.spawn(
            [
                "zig",
                "build-lib",
                f"-femit-bin={self.get_ext_fullpath(ext.name)}",
                "-fallow-shlib-undefined",
                "-dynamic",
                *[f"-I{d}" for d in self.include_dirs],
                ext.sources[0],
            ]
        )


setup(
    name="zaml",
    version="0.0.1",
    description="Fast YAML 1.2 Parser for Python 3.10.x",
    ext_modules=[zaml],
    cmdclass={"build_ext": ZigBuilder},
)
