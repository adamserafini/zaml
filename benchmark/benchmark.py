import subprocess

# Test the benchmark installs
failed = subprocess.call(["python", "setup.py", "develop"])
assert not failed

import yaml as pyyaml
import benchmark as zaml
import time

# Test it returns correct results:
assert zaml.load("a0: b1") == {"a0": "b1"}

print("\nRunning benchmarks...\n")

# One million line YAML string:
big_yaml = pyyaml.dump(
    {"a" + str(i): "b" + str(i + 1) for i in range(1000000)}, Dumper=pyyaml.CSafeDumper
)

# Parsing with PyYAML:
start = time.time()
pyyaml_result = pyyaml.load(big_yaml, Loader=pyyaml.CSafeLoader)
print(f"Benchmark results:\nPyYAML took {(time.time() - start):.2f} seconds")

# Parsing with zaml: Prototype YAML parser written in Zig:
start = time.time()
zaml_result = zaml.load(big_yaml)
print(f"zaml took {(time.time() - start):.2f} seconds")

assert pyyaml_result == zaml_result
