#!/usr/bin/env python
# encoding: utf8

from setuptools import setup

setup(
    name='pyexpect',
    version='1.0.1',
    description='Python expectaton library',
    long_description=file('README.md').read(),
    author='Martin Häcker',
    author_email='spamfaenger@gmx.de',
    url='https://bitbucket.org/dwt/pyexpect',
    py_modules=['pyexpect'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'License :: OSI Approved :: Python Software Foundation License',
        'Programming Language :: Python',
        'Topic :: Software Development :: Testing',
        'Topic :: Software Development :: Quality Assurance',
    ],
)
