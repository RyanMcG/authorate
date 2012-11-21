#from distutils.core import setup
from setuptools import setup
import os

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as \
        description_file:
    long_description = description_file.read()
with open(os.path.join(os.path.dirname(__file__), 'requirements.txt')) as \
        requirements_file:
    requirements = [line.rstrip() for line in requirements_file]

name = 'authorate'

setup(name=name,
      version='0.1.0-SNAPSHOT',
      author='Ryan McGowan',
      author_email='ryan@ryanmcg.com',
      description="",
      long_description=long_description,
      url='https://github.com/RyanMcG/' + name,
      install_requires=requirements,
      py_modules=['authorate'],
      entry_points={
          'console_scripts': [
              'authorate = authorate:main'
          ]
      },
      classifiers=['Development Status :: 4 - Beta',
                   'Programming Language :: Python',
                   'Programming Language :: Python :: 2']
      )
