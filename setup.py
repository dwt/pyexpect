#!/usr/bin/env python
# encoding: utf8

from setuptools import setup

def readme():
    "Falls back to just file().read() on any error, because the conversion to rst is only really relevant when uploading the package to pypi"
    from subprocess import CalledProcessError
    try:
        from subprocess import check_output
        return str(check_output(['pandoc', '--from', 'markdown', '--to', 'rst', 'README.md']))
    except (ImportError, OSError, CalledProcessError) as error:
        print('python2.6 and pandoc is required to get the description as rst (as required to get nice rendering in pypi) - using the original markdown instead.',
              'See http://johnmacfarlane.net/pandoc/')
    return str(open('README.md').read())

setup(
    name='pyexpect',
    version='1.0.10',
    description='Python expectaton library',
    long_description=readme(),
    author='Martin Häcker',
    author_email='spamfaenger@gmx.de',
    url='https://bitbucket.org/dwt/pyexpect',
    py_modules=['pyexpect'],
    test_suite="tests",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Topic :: Software Development :: Testing',
        'Topic :: Software Development :: Quality Assurance',
    ],
)
