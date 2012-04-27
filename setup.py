# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import sys, os

install_requires =[
          'setuptools'
          ]

if sys.version_info < (2, 7):
    install_requires.append('ordereddict')

setup(name='zope_lrr_analyzer',
      version="0.1",
      description="Analyze Zope instance log with haufe.requestmonitoring entries",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=["Development Status :: 4 - Beta",
                   "Intended Audience :: System Administrators",
                   "License :: OSI Approved :: GNU General Public License (GPL)",
                   "Operating System :: OS Independent",
                   "Programming Language :: Python",
                   "Programming Language :: Python :: 2.6",
                   "Programming Language :: Python :: 2.7",
                   "Framework :: Zope2",
                   "Topic :: Utilities",
                   "Topic :: Internet :: Log Analysis",
                   ], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='file log process-time analyser access lrr zope',
      author='RedTurtle Technology',
      author_email='sviluppoplone@redturtle.it',
      url='https://github.com/RedTurtle/zope_lrr_analyzer',
      license='GPL',
      # packages=find_packages('src', exclude=['ez_setup',]),
      py_modules=['zope_lrr_analyzer',],
      package_dir = {'': 'src'},
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires,
      entry_points={'console_scripts': ['zope_lrr_analyzer = zope_lrr_analyzer:main', ]}
      )

