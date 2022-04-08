import subprocess

failed = subprocess.call(["pip", "install", "-e", "."])
assert not failed

import zaml

assert zaml.load() == 1
