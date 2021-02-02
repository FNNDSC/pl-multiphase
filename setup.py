from os import path
from setuptools import setup

with open(path.join(path.dirname(path.abspath(__file__)), 'README.rst')) as f:
    readme = f.read()

setup(
    name             = 'multiphase',
    version          = '1.0.2',
    description      = 'This ChRIS plugin simply runs/execs other apps (these must be in the container) multiple times, each time with a slightly different set of CLI. ',
    long_description = readme,
    author           = 'FNNDSC / Rudolph Pienaar',
    author_email     = 'dev@babymri.org',
    url              = 'https://github.com/FNNDSC/pl-multiphase',
    packages         = ['multiphase'],
    install_requires = ['chrisapp'],
    test_suite       = 'nose.collector',
    tests_require    = ['nose'],
    license          = 'MIT',
    zip_safe         = False,
    python_requires  = '>=3.8',
    entry_points     = {
        'console_scripts': [
            'multiphase = multiphase.__main__:main'
            ]
        }
)
