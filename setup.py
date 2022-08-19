# -*- coding: utf-8 -*-
"""Instructions for setuptools / pip"""
import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='isodbtools',
    version='0.1.0',
    author='Daniel W. Siderius',
    author_email='daniel.siderius@nist.gov',
    description='A small example package',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/NIST-ISODB/isodbtools',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: Public Domain',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
