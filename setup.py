#!/usr/bin/env python
# encoding: utf8

from setuptools import setup

def readme():
    "Falls back to just file().read() on any error, because the conversion to rst is only really relevant when uploading the package to pypi"
    from subprocess import CalledProcessError
    try:
        from subprocess import check_output
        return check_output(['pandoc', '--from', 'markdown', '--to', 'rst', 'README.md'])
    except (ImportError, OSError, CalledProcessError) as error:
        print('python2.6 and pandoc is required to get the description as rst - using the original markdown instead.',
              'See http://johnmacfarlane.net/pandoc/')
    return file('README.md').read()

setup(
    name='pyexpect',
    version='1.0.6',
    description='Python expectaton library',
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
