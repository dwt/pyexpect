#!/usr/bin/env python
# encoding: utf8

from setuptools import setup, find_packages
import os

here = os.path.dirname(os.path.abspath(__file__))
import codecs

setup_args = dict(
    name='pyexpect',
    version='1.0.21',
    description='Python expectaton library',
    long_description=codecs.open(os.path.join(here, 'README.md'), encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='Martin Häcker',
    author_email='spamfaenger@gmx.de',
    license='ISC',
    url='https://github.com/dwt/pyexpect',
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

if __name__ == '__main__':
    setup(**setup_args)
