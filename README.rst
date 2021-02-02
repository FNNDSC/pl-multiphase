pl-multiphase
================================

.. image:: https://travis-ci.org/FNNDSC/multiphase.svg?branch=master
    :target: https://travis-ci.org/FNNDSC/multiphase

.. image:: https://img.shields.io/badge/python-3.8%2B-blue.svg
    :target: https://github.com/FNNDSC/pl-multiphase/blob/master/setup.py

.. contents:: Table of Contents


Abstract
--------

This ChRIS plugin simply runs/execs other apps (these must be in the container) multiple times, each time with a slightly different set of CLI. 


Description
-----------

``multiphase`` is a ChRIS-based application that...


Usage
-----

.. code::

    python multiphase.py
        [-h|--help]
        [--json] [--man] [--meta]
        [--savejson <DIR>]
        [-v|--verbosity <level>]
        [--version]
        <inputDir> <outputDir>


Arguments
~~~~~~~~~

.. code::

    [-h] [--help]
    If specified, show help message and exit.
    
    [--json]
    If specified, show json representation of app and exit.
    
    [--man]
    If specified, print (this) man page and exit.

    [--meta]
    If specified, print plugin meta data and exit.
    
    [--savejson <DIR>] 
    If specified, save json representation file to DIR and exit. 
    
    [-v <level>] [--verbosity <level>]
    Verbosity level for app. Not used currently.
    
    [--version]
    If specified, print version number and exit. 


Getting inline help is:

.. code:: bash

    docker run --rm fnndsc/pl-multiphase multiphase --man

Run
~~~

You need you need to specify input and output directories using the `-v` flag to `docker run`.


.. code:: bash

    docker run --rm -u $(id -u)                             \
        -v $(pwd)/in:/incoming -v $(pwd)/out:/outgoing      \
        fnndsc/pl-multiphase multiphase                        \
        /incoming /outgoing


Development
-----------

Build the Docker container:

.. code:: bash

    docker build -t local/pl-multiphase .

Examples
--------

Put some examples here!


.. image:: https://raw.githubusercontent.com/FNNDSC/cookiecutter-chrisapp/master/doc/assets/badge/light.png
    :target: https://chrisstore.co
