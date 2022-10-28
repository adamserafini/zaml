from setuptools import setup, Extension
from builder import ZigBuilder

zaml = Extension("zaml", sources=["zamlmodule.c"])

setup(
    name="zaml",
    version="0.0.1",
    description="Fast YAML 1.2 Parser for Python 3.10.x",
    ext_modules=[zaml],
    cmdclass={"build_ext": ZigBuilder},
)
