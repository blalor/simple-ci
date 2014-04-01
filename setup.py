#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from setuptools import setup, find_packages

## http://stackoverflow.com/questions/22313407/clang-error-unknown-argument-mno-fused-madd-python-package-installation-fa

setup(
    name="simple-ci",
    version="0.0.0",
    description="The world's simplest continuous integration system",
    author="Brian Lalor",
    author_email="brian@bravo5.org",
    url="http://github.com/blalor/simple-ci",
    packages=find_packages(),
    install_requires=[
        "watchdog >= 0.7.1, < 0.8.0",
        "colorama >= 0.2.5, < 0.3.0",
        "argparse >= 1.1",
    ],
    scripts=["bin/simple_ci.py"],
)
