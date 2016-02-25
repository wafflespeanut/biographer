# This is just a workaround for QPython in Android which looks for 'main.py' file, instead of '__main__.py'
import os
from src.utils import exec_path

execfile(os.path.join(os.path.dirname(exec_path), '__main__.py'))
