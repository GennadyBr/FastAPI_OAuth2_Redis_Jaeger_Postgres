import os
import sys

current = os.path.dirname(os.path.realpath(__file__))
sys.path.append(current)

pytest_plugins = "functional.fixtures.common"
