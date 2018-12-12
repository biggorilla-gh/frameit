#!/usr/bin/env python
# -*- coding: utf-8 -*-
#test

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    "flask",
    "keras",
    "nltk",
    "numpy",
    "pandas",
    "scikit-learn",
    "scipy",
    "spacy==2.0.12",
    "tensorflow",
    "whoosh"]

setup(
    author="BigGorilla",
    author_email='thebiggorilla.team@gmail.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    description="FrameIt is a tool for defining frames and building SRLs",
    install_requires=requirements,
    license="Apache Software License 2.0",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='frameit',
    name='frameit',
    packages=find_packages(include=['frameit']),
    package_dir={'frameit': 'frameit'},
    setup_requires=requirements,
    test_suite='tests',
    tests_require=requirements,
    url='https://github.com/jengel-rit/frameit',
    version='0.1.0',
    zip_safe=False,
)
