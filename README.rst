.. contents:: **Table of contents**

Introduction
============

This project adds to your system a new utility command: ``zope_lrr_analyzer``. This utility only works with
Zope instance logs, where you also intalled `haufe.requestmonitoring`__.

__ http://pypi.python.org/pypi/haufe.requestmonitoring

It will help you to parse slow running request reports and collect some statistical data.

How to use
==========

    Usage: zope_lrr_analyzer [options] logfile [logfile...]
    
    Analyze Zope instance log with haufe.requestmonitoring entries
    
    Options:
      --version             show program's version number and exit
      -h, --help            show this help message and exit
      -s START_FROM, --start=START_FROM
                            start analysis after a given date/time (format like
                            "YYYY-MM-DD HH:MM:SS")
      -e END_AT, --end=END_AT
                            stop analysis at given date/time (format like "YYYY-
                            MM-DD HH:MM:SS")
      -l LOG_SIZE, --log-size=LOG_SIZE
                            keep only an amount of slow requests. Default is: no
                            limit.
      -i INCLUDE_REGEX, --include=INCLUDE_REGEX
                            a regexp expression that a calling path must match or
                            will be discarded. Can be called multiple times,
                            expanding the set

Results
=======

Let explain the given results::

    Stats from 2012-04-27 00:02:07 to 2012-04-27 16:55:41
    ...
    ----    
    2 /VirtualHostBase/http/yoursite.com:80/siteid/VirtualHostRoot/foo/foo
        15 - 171.913325071 (0:02:51.913325)
        
    ----
    1  /VirtualHostBase/http/yoursite.com:80/siteid/VirtualHostRoot/foo/another
        3 - 1350.58498883 (0:22:30.584989)

You'll get a ranking of slowest request paths (top one is faster, last one is slowest).
The order is not done collecting all request's done to the same path, getting the total time.

This mean that a request called only one time and that need 30 seconds is faster that another path
that only require 10 seconds, but is called ten times.

Single entry meaning
--------------------

Every entry gives that kind of data::

    Entry position                       Called path
         |                                   |
         1 /VirtualHostBase/http/yoursite.com:80/siteid/VirtualHostRoot/...
             15 - 171.913325071 (0:02:51.913325)
             |         |                |
         Times called  |      Time needed (human readable)
                       |
              Time needed (in seconds)
