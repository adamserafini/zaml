# 🚀 zaml
Fast YAML 1.2 parsing library for Python 3.10.x.

## What's This?

Proof-of-concept for my PyCon DE 2022 [talk](https://2022.pycon.de/program/DFWSQR/), 
**Speeding Up Python with Zig**, not yet recommended for production use!

Library with the following objectives:
 - [ ] Written in pure Zig, importing `Python.h` headers directly, no FFI, `ctypes` or `cffi`.
 - [ ] Compiled using the Zig toolchain / CLI, no other tool (eg. `clang`) required.
 - [ ] Tested to be compatible with mac OSX, Linux and Windows.
 - [ ] Installable via PyPI, end-user should not require Zig toolchain locally in order to use.
 - [ ] Fastest available YAML 1.2 parser for Python.

Currently, it doesn't meet *any* of those objectives! 😂 Watch this space...

### Installing Locally

Some pre-requisites (linting etc.), `pyenv` also recommended:
```bash
pre-commit install
pre-commit run --all-files
```

The simplest possible extension module is a module with one function, that takes no arguments and returns an 
empty list. So let's get that working first in C, cross platform, and distributable and then translate it to Zig!

```bash
python -m venv .venv
source .venv/bin/activate
python setup.py install
```

### Tests

```
python test.py
```
