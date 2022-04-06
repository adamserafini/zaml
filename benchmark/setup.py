from setuptools import setup, Extension
from builder import ZigBuilder

benchmark = Extension("benchmark", sources=["benchmark.zig"])

setup(
    name="benchmark",
    version="0.0.1",
    description="Benchmark of Fast YAML 1.2 Parser for Python 3.10.x",
    ext_modules=[benchmark],
    cmdclass={"build_ext": ZigBuilder},
    setup_requires=["cython"],  # Required by pyyaml
    install_requires=["pyyaml"],
)
