#!/usr/bin/env python
# encoding: utf8

from setuptools import setup, find_packages
import os

here = os.path.dirname(os.path.abspath(__file__))

def readme():
    "Falls back to just file().read() on any error, because the conversion to rst is only really relevant when uploading the package to pypi"
    from subprocess import CalledProcessError
    try:
        from subprocess import check_output
        return check_output(['pandoc', '--from', 'markdown', '--to', 'rst', 'README.md']).decode('utf-8')
    except (ImportError, OSError, CalledProcessError) as error:
        print('pandoc is required to get the description as rst (as required to get nice rendering in pypi) - using the original markdown instead.',
              'See http://johnmacfarlane.net/pandoc/')
    return open(path.join(here, 'README.md')).read().decode('utf-8')



setup(
    name='pyexpect',
    version='1.0.16',
    description='Python expectaton library',
    long_description=readme(),
    author='Martin Häcker',
    author_email='spamfaenger@gmx.de',
    license='ISC',
    url='https://bitbucket.org/dwt/pyexpect',
    packages=find_packages(),
    include_package_data=True,
    test_suite="tests",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Testing',
        'Topic :: Software Development :: Quality Assurance',
    ],
)
