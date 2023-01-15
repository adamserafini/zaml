# 🚀 zaml
Fast YAML 1.2 parsing library for Python 3.6+ 🐍

## What's This?

Proof-of-concept for my PyCon DE 2022 [talk](https://2022.pycon.de/program/DFWSQR/), 
[video](https://www.youtube.com/watch?v=O0MmmZxdct4), 
**Speeding Up Python with Zig**, not yet recommended for production use!

Library with the following objectives:
 - [x] Written in pure Zig, importing `Python.h` headers directly, no FFI, `ctypes` or `cffi`.
 - [x] Compiled using the Zig toolchain / CLI, no other tool (eg. `clang`) required.
 - [x] Tested to be compatible with mac OSX, Linux and Windows.
 - [x] Installable via PyPI
 - [ ] Should not require Zig toolchain locally in order to install and use.
 - [ ] Fastest available YAML 1.2 parser for Python.

Help wanted to achieve the full objectives, PRs welcome.

### Installation

```
pip install zaml
```

**Note**: currently source distribution only, ie. `sdist` - no binary `wheels` (yet), therefore requires Zig 0.10.0 
installed locally. Any other Zig version is untested.

### Installing Locally

Some pre-requisites (linting etc.), `pyenv` also recommended:
```bash
pre-commit install
pre-commit run --all-files
```

The simplest possible extension module is a module with one function, that takes no arguments and returns an integer. 
This repo demonstrates a pure Zig module that does exactly that:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

### Tests

Tests that the most basic possible Zig extension can in-fact be installed and returns the expected result:

```bash
python test.py
```

### Benchmark

To run a benchmark of the current `zaml` prototype (also runs in CI and asserts that the YAML structure is correctly 
parsed):
```bash
cd benchmark
python benchmark.py
```

Results on my 2,3 GHz Quad-Core Intel Core i7 Mac:

```bash
Running benchmarks...

Benchmark results:
zaml took 0.89 seconds
PyYAML CSafeLoader took 13.36 seconds
ruamel took 38.86 seconds
PyYAML SafeLoader took 81.78 seconds
```

### Credits

Would not exist without [kubkon's](https://github.com/kubkon), `zig-yaml`: https://github.com/kubkon/zig-yaml

### Cross-platform Local Testing

#### Linux

To test in Linux, the easiest way is probably to use Docker:

```bash
docker run --name zaml -v $PWD:/root/zaml -it fedora
```

This kicks you into a shell in a running a container with this library mounted in
the `/root/zaml` directory. Changes you make on your host machine will be immediately
reflected in the container.

Install Python 3 headers, zig and test the library:

```bash
dnf install zig python3-devel
cd /root/zaml
python3 -m venv .venvlinux
source .venvlinux/bin/activate
pip install -e .
```

To re-attach to the container after exiting:

```bash
docker start -ia zaml
```

#### Windows

To test in Windows from a Mac, the easiest way I have found is to use [Parallels](https://www.parallels.com/).

#### MacOSX

I am writing this `README` on a Mac. Consequently, I have not attempted testing this library in MacOSX from another
operating system host. If you manage this, please do add documentation about it here.

### Publishing to PyPI
 
**Note**: Temporary instructions (until full CI setup).

You may need to upgrade `build` and `twine` (with your `virtualenv` activated):

```
python -m pip install --upgrade build
python -m pip install --upgrade twine
```

Then:

```
rm -rf dist
python3 -m build --sdist
python3 -m twine upload --repository pypi dist/*
```
