#!/usr/bin/env python
# encoding: utf8

from setuptools import setup

def readme():
    from subprocess import check_output, CalledProcessError
    try:
        return check_output(['pandoc', '--from', 'markdown', '--to', 'rst', 'README.md'])
    except (OSError, CalledProcessError) as error:
        raise AssertionError('pandoc is required to build this, see http://johnmacfarlane.net/pandoc/')

setup(
    name='pyexpect',
    version='1.0.3',
    description='Python expectaton library',
    # REFACT: convert the readme with 'pandoc --from markdown --to rst README.md' directly on reading
    long_description=readme(),
    author='Martin Häcker',
    author_email='spamfaenger@gmx.de',
    url='https://bitbucket.org/dwt/pyexpect',
    py_modules=['pyexpect'],
    test_suite="pyexpect",
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
