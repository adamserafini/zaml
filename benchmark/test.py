import subprocess

failed = subprocess.call(["python", "setup.py", "develop"])
assert not failed

import benchmark

assert benchmark.load("a0: b1") == {"a0": "b1"}
