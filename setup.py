from distutils.core import setup, Extension

module1 = Extension("zaml", sources=["zamlmodule.c"])

setup(
    name="zaml",
    version="0.0.1",
    description="Fast YAML 1.2 Parser for Python 3.10.x",
    ext_modules=[module1],
)
