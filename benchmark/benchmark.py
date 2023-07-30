import subprocess

# Test the benchmark installs
failed = subprocess.call(["pip", "install", "-e", "."])
assert not failed

import yaml as pyyaml
import benchmark as zaml
from ruamel.yaml import YAML
import time

# Test it returns correct results:
assert zaml.load("a0: b1") == {"a0": "b1"}

print("\nRunning benchmarks...\n")

# One million line YAML string:
big_yaml = pyyaml.dump(
    {"a" + str(i): "b" + str(i + 1) for i in range(1000000)}, Dumper=pyyaml.CSafeDumper
)

# Parsing with zaml: Prototype YAML parser written in Zig:
start = time.perf_counter()
zaml_result = zaml.load(big_yaml)
print(f"Benchmark results:\nzaml took {(time.perf_counter() - start):.4f} seconds")

# Parsing with PyYAML in C:
start = time.perf_counter()
pyyaml_c_result = pyyaml.load(big_yaml, Loader=pyyaml.CSafeLoader)
print(f"PyYAML CSafeLoader took {(time.perf_counter() - start):.4f} seconds")

# Parsing with ruamel:
start = time.perf_counter()
yaml = YAML(typ="safe")
yaml.load(big_yaml)
rueaml_result = yaml.load(big_yaml)
print(f"ruamel took {(time.perf_counter() - start):.4f} seconds")

# Parsing with PyYAML:
start = time.perf_counter()
pyyaml_result = pyyaml.load(big_yaml, Loader=pyyaml.SafeLoader)
print(f"PyYAML SafeLoader took {(time.perf_counter() - start):.4f} seconds")


assert zaml_result == pyyaml_result == pyyaml_c_result == rueaml_result
