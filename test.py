import subprocess

failed = subprocess.call(["python", "setup.py", "develop"])
assert not failed

import zaml

assert zaml.load() == 1
