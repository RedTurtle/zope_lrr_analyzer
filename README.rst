.. contents:: **Table of contents**

Introduction
============

This project adds to your system a new utility command: ``zope_lrr_analyzer``. This utility only works with
Zope instance logs with `haufe.requestmonitoring`__ installed.

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
      -r, --keep-request-id
                            Use request and thread ids to handle every match as a
                            different entry

Results
=======

Let's explain the results::

    Stats from 2012-04-27 00:02:07 to 2012-04-27 16:55:41
    ...
    ----    
    2 /VirtualHostBase/http/yoursite.com:80/siteid/VirtualHostRoot/foo/foo
        15 - 171.913325071 (0:02:51.913325)
        
    ----
    1  /VirtualHostBase/http/yoursite.com:80/siteid/VirtualHostRoot/foo/another
        3 - 1350.58498883 (0:22:30.584989)

You'll get a rank of slowest request paths (top one is fastest, last one is slowest).
The order is done by collecting all request's performed to the same path and then getting the total time.

This mean that a request called only once that needs 30 seconds is faster that another path
that only requires 10 seconds, but is called ten times (30x1 < 10x10).

If you use also the ``--keep-request-id`` option, every request is count as a separate entry,
so the output change a little::

    Stats from 2012-04-27 00:02:07 to 2012-04-27 16:55:41
    ...
    ----
    2 /VirtualHostBase/http/yoursite.com:80/siteid/VirtualHostRoot/foo/foo
        1510.2860291 (0:25:10.286029) - from 2012-09-19 08:36:27 to 2012-09-19 09:01:22
    
    ----
    1 /VirtualHostBase/http/yoursite.com:80/siteid/VirtualHostRoot/foo/another
        1750.49365091 (0:29:10.493651) - from 2012-09-19 08:30:34 to 2012-09-19 09:00:58

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

When ``--keep-request-id`` used::

    Entry position                       Called path
         |                                   |
         1 /VirtualHostBase/http/yoursite.com:80/siteid/VirtualHostRoot/...
             1750.49365091 (0:29:10.493651) - from 2012-09-19 08:30:34 to 2012-09-19 09:00:58
                |               |                           |                      |
    Time needed (in seconds)    |                 slow request start date          |
                                |                                                  |
                       Time needed (human readable)                       slow request end date

Authors
=======

This product was developed by RedTurtle Technology team.

.. image:: http://www.redturtle.it/redturtle_banner.png
   :alt: RedTurtle Technology Site
   :target: http://www.redturtle.it/

