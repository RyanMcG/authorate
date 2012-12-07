=========
authorate
=========
----------------------------
Find out who you write like.
----------------------------


Introduction
============

*authorate* is a smart tool that uses machine learning algorithms to determine
what famous author you write like the most.

Setup
=====

Firstly, you'll need to install some system level dependencies

**Ubuntu**
::
    sudo apt-get install python-numpy python-scipy
    # Or if you are installing for development . . .
    sudo apt-get install gfortran gcc liblapack3 liblapack-dev libblas3 libblas-dev

To install authorate from source: ::

    git clone git://github.com/RyanMcG/authorate.git
    cd authorate
    python setup.py install
    # Or if you want to develop
    python setup.py develop

If you want to use authorate directly without installing it be sure to install
the python dependencies first. ::

    # Assuming you are already in the authorate directory
    pip install -r requirements.txt

In any case, after installing normally or in development mode you must grab the
extra nltk packages. ::

    # Install nltk extras
    python setup_nltk.py

If you encounter an error regarding `numpy.distribute` not being found then you
may have forgotten to install numpy and scipy (see above) or you might have to
do so separately (if, for instance, you are installing this inside of a
virtualenv): ::

    pip install numpy
    pip install scipy

Usage
=====

Typical usage consists of three steps.

1.  Select authors to compare against.
2.  Load snippets from those authors
3.  Process them for metrics and build a model to use for classification.
4.  Classify given snippets.

1.  Select authors
------------------

You can select whatever authors you want with the restriction that they exist in
the calibre database you are loading snippets from (*authorate* uses local
calibre database to find books by the given authors).  A simple text file with
one author per line is all that is necessary once your authors are selected.

For an example see authors.sample.txt_.

2.  Load snippets
-----------------

To load snippets simply use the ``load`` subcommand. ::

    authorate load authors.sample.txt

This command creates a sqlite3 database called ``snippets.db``. This database is
used by all other subcommands.

3.  Process snippets & Construct model
--------------------------------------

Using the database mentioned above process extracts features from all snippets
in the database and trains a bunch of classifiers (see
authorate.classify.classifier_types_). The trained classifiers are then saved in a
newly created ``classifiers`` directory. ::

    authorate process

4.  Classify user snippet
-------------------------

Classification is easy as long as you have a ``classifiers`` directory full of
classifiers (see above for instructions on how to get one).  Classify can read
from stdin or a file. ::

    echo "Text to be classified" | authorate classify
    authorate classify snippet-to-calssify.txt

License
~~~~~~~

Copyright 2012

:Ryan McGowan: ryan@ryanmcg.com
:Chris Powers: powers.240@osu.edu
:Alex Burkhart: saterus@gmail.com

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

.. _authors.sample.txt: https://github.com/RyanMcG/authorate/blob/master/authors.sample.txt
.. _authorate.classify.classifier_types: https://github.com/RyanMcG/authorate/blob/master/authorate/classify.py#L78
