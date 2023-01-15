from setuptools import setup, Extension
from pathlib import Path

from builder import ZigBuilder

zaml = Extension("zaml", sources=["zamlmodule.zig"])

setup(
    name="zaml",
    version="0.0.8",
    url="https://github.com/adamserafini/zaml",
    description="Fast YAML 1.2 Parser for Python 3.6+",
    ext_modules=[zaml],
    cmdclass={"build_ext": ZigBuilder},
    long_description=(Path(__file__).parent / "README.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    py_modules=["builder"],
)
