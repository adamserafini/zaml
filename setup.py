from setuptools import setup, Extension
from wheel.bdist_wheel import bdist_wheel
from pathlib import Path

from builder import ZigBuilder


class bdist_wheel_abi3(bdist_wheel):
    def get_tag(self):
        python, abi, plat = super().get_tag()

        if python.startswith("cp"):
            # on CPython, our wheels are abi3 and compatible back to 3.6
            return "cp36", "abi3", plat

        return python, abi, plat


zaml = Extension("zaml", sources=["zamlmodule.zig"], py_limited_api=True)

setup(
    name="zaml",
    version="0.0.8",
    url="https://github.com/adamserafini/zaml",
    description="Fast YAML 1.2 Parser for Python 3.6+",
    ext_modules=[zaml],
    cmdclass={"build_ext": ZigBuilder, "bdist_wheel": bdist_wheel_abi3},
    long_description=(Path(__file__).parent / "README.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    py_modules=["builder"],
)
