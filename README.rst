.. contents:: **Table of contents**

Introduction
============

This project adds to your system a new utility command: ``zope_lrr_analyzer``. This utility only works with
Zope instance logs with `haufe.requestmonitoring`__ installed (and where the
`monitoring long running requests hook`__ is enabled).

__ http://pypi.python.org/pypi/haufe.requestmonitoring
__ http://pypi.python.org/pypi/haufe.requestmonitoring#monitoring-long-running-requests

Your *instance.log* will be populated by entries like this::

    ------
    2012-03-27T15:58:19 WARNING RequestMonitor.DumpTrace Long running request
    Request 28060 "/VirtualHostBase/http/www.mysite.com:80/mysiteid/VirtualHostRoot/myrequest/..." running in thread 1133545792 since 10.7206499577s
    Python call stack (innermost first)
      ...
      lot of lines, depends on Python traceback
      ...
      Module ZPublisherEventsBackport.patch, line 80, in publish
      Module ZPublisher.Publish, line 202, in publish_module_standard
      Module ZPublisher.Publish, line 401, in publish_module
      Module ZServer.PubCore.ZServerPublisher, line 25, in __init__
    <BLANKLINE>

The utility will help you to parse long running request collecting some statistical data.

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
      -t TRACEBACK_INCLUDE_REGEX, --traceback-include=TRACEBACK_INCLUDE_REGEX
                            a regexp expression that the Python traceback must
                            match or will be discarded. Can be called multiple
                            times, expanding the set
      -r, --keep-request-id
                            Use request and thread ids to handle every match as a
                            different entry

Results
=======

Let's explain the results::

    Stats from 2012-11-14 00:02:07 to 2012-11-15 09:55:41
    ...
    ----
    2 /VirtualHostBase/http/yoursite.com:80/siteid/VirtualHostRoot/foo/bar
        25 - 3654.05561542 (1:00:54.055615) - from 2012-11-15 07:48:10 to 2012-11-15 08:45:29
    
    ----
    1 /VirtualHostBase/http/yoursite.com:80/siteid/VirtualHostRoot/baz
        77 - 16029.3731236 (4:27:09.373124) - from 2012-11-15 07:43:55 to 2012-11-15 08:45:30

You'll get a rank of slowest request paths (top one is fastest, last one is slowest).
The order is done by collecting all request's performed to the same path and then getting the total time.

This mean that a request called only once that needs 30 seconds is faster that another path
that only requires 10 seconds, but is called ten times (30x1 < 10x10).

If you use also the ``--keep-request-id`` option, every request is count as a separate entry,
so the output change a little::

    Stats from 2012-04-27 00:02:07 to 2012-04-27 16:55:41
    ...
    ----
    2 /VirtualHostBase/http/yoursite.com:80/siteid/VirtualHostRoot/foo/bar
        1510.2860291 (0:25:10.286029) - from 2012-09-19 08:36:27 to 2012-09-19 09:01:22
    
    ----
    1 /VirtualHostBase/http/yoursite.com:80/siteid/VirtualHostRoot/baz
        1750.49365091 (0:29:10.493651) - from 2012-09-19 08:30:34 to 2012-09-19 09:00:58

Single entry meaning
--------------------

Every entry gives that kind of data::

    Entry position                       Called path
         |                                   |
         1 /VirtualHostBase/http/yoursite.com:80/siteid/VirtualHostRoot/...
             15 - 171.913325071 (0:02:51.913325) - from 2012-09-19 08:30:34 to 2012-09-19 09:00:58
             |         |                |                       |                       |
         Times called  |      Time needed (human readable)      |                       |
                       |                                        |              Slow request end date
              Time needed (in seconds)                Slow request start date

When ``--keep-request-id`` used::

    Entry position                       Called path
         |                                   |
         1 /VirtualHostBase/http/yoursite.com:80/siteid/VirtualHostRoot/...
             1750.49365091 (0:29:10.493651) - from 2012-09-19 08:30:34 to 2012-09-19 09:00:58
                 |              |                           |                      |
     Time needed (in seconds)   |                 Slow request start date          |
                                |                                                  |
                       Time needed (human readable)                       Slow request end date


Please note that the "*Time needed*" info is machine computation time.

Authors
=======

This product was developed by RedTurtle Technology team.

.. image:: http://www.redturtle.it/redturtle_banner.png
   :alt: RedTurtle Technology Site
   :target: http://www.redturtle.it/

