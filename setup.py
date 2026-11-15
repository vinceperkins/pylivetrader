#!/usr/bin/env python
# coding: utf-8
import os
from setuptools import setup, find_packages

from runpy import run_path
from pathlib import Path


VERSION = run_path(
    str(Path(__file__).parent) + '/pylivetrader/_version.py')['VERSION']


with open(str(Path(__file__).parent) + '/README.md') as readme_file:
    README = readme_file.read()

with open(os.path.join("requirements", "requirements.txt")) as reqs:
    REQUIREMENTS = reqs.readlines()

with open(os.path.join("requirements", "requirements_test.txt")) as reqs:
    REQUIREMENTS_TEST = reqs.readlines()

setup(
    name='pylivetrader',
    version=VERSION,
    description='simple live trading framework',
    long_description=README,
    long_description_content_type='text/markdown',
    license='Apache 2.0',
    author='Alpaca',
    author_email='oss@alpaca.markets',
    url='https://github.com/alpacahq/pylivetrader.git',
    keywords='financial,zipline,pipeline,stock,screening,api,trade',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Operating System :: OS Independent',
        'Topic :: Office/Business :: Financial',
    ],
    python_requires='>=3.9',
    packages=find_packages(),
    include_package_data=True,
    entry_points='''
    [console_scripts]
    pylivetrader=pylivetrader.__main__:main
    ''',
    install_requires=REQUIREMENTS,
    tests_require=REQUIREMENTS_TEST,
    extras_require={
        # pipeline-live is unmaintained and hard-pins ancient dependencies
        # (zipline==1.3.0, pandas==0.22.0, numpy==1.19.4) that no longer
        # build on modern Python, so it's optional rather than a hard
        # requirement. pipeline_output() already raises a clear
        # RuntimeError at runtime if it isn't installed.
        'pipeline': ['pipeline-live>=0.2.0'],
    },
    setup_requires=["flake8", "pytest-runner"]
)
