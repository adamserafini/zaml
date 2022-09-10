import subprocess

failed = subprocess.call(["pip", "install", "-e", ".", "--verbose"])
assert not failed

import zaml

assert zaml.load() == 1
