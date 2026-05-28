"""Legacy setuptools shim.

Project metadata, dependencies, and entry points live in pyproject.toml.
This file exists only for older tooling that still invokes setup.py.
"""

from setuptools import setup


setup()
