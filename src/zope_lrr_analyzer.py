#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Log requests like this:

    ------
    2012-03-27T15:58:19 WARNING RequestMonitor.DumpTrace Long running request
    Request 28060 "/VirtualHostBase/http/www.mysite.com:80/mysiteid/VirtualHostRoot/myrequest/..." running in thread 1133545792 since 10.7206499577s
    Python call stack (innermost first)
      Module ZPublisher.HTTPResponse, line 385, in setBody
      Module ZServer.HTTPResponse, line 262, in setBody
      Module ZPublisherEventsBackport.patch, line 80, in publish
      Module ZPublisher.Publish, line 202, in publish_module_standard
      Module ZPublisher.Publish, line 401, in publish_module
      Module ZServer.PubCore.ZServerPublisher, line 25, in __init__
    <BLANKLINE>
"""

import sys
import re
import logging
import optparse
from datetime import datetime, timedelta
try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

version = "0.1"
description = "Analyze Zope instance log with haufe.requestmonitoring entries"

usage = "usage: %prog [options] logfile [logfile...]"
p = optparse.OptionParser(usage=usage, version="%prog " + version, description=description,
                          prog="zope_lrr_analyzer")

p.add_option('--start', '-s', type="string", dest="start_from", default=None,
             help='start analysis after a given date/time (format like "YYYY-MM-DD HH:MM:SS")')
p.add_option('--end', '-e', type="string", dest="end_at", default=None,
             help='stop analysis at given date/time (format like "YYYY-MM-DD HH:MM:SS")')
p.add_option('--log-size', '-l', type="int", dest="log_size", default=None,
             help='keep only an amount of slow requests. Default is: no limit.')
p.add_option('--include', '-i', dest="includes", default=[], action="append", metavar="INCLUDE_REGEX",
             help="a regexp expression that a calling path must match or will be discarded. "
                  "Can be called multiple times, expanding the set")

logger = logging.getLogger("zope_lrr_analyzer")

PATTERN = """^------$
^(?P<date>\d{4}-\d{2}-\d{2})T(?P<time>\d\d\:\d\d\:\d\d).*?$
^Request (?P<reqid>\d*?) "(?P<path>.*?)" running in thread .*? since (?P<reqtime>\d*?\.\d*?)s$
.*?
^$"""

PATH_PARRENT = """^(?P<path>.*?)(?:\?.*?)?$"""

reqLine = re.compile(PATTERN, re.M|re.S)
pathLine = re.compile(PATH_PARRENT, re.M|re.S)

stats = {}
stat_data = {'count': 0, 'totaltime': 0, 'reqids': []}


def main():
    options, arguments = p.parse_args(sys.argv[1:])
    
    min_date = max_date = None
    start_from = None
    end_at = None
    if options.start_from:
        start_from = datetime.strptime(options.start_from, "%Y-%m-%d %H:%M:%S")
    if options.end_at:
        end_at = datetime.strptime(options.end_at, "%Y-%m-%d %H:%M:%S")
    
    if not arguments:
        print p.format_help()
        sys.exit(1)
    
    ### Step 1. collect raw data
    for param in arguments:
        f = open(param)
        log = f.read()
        f.close()
        
        matches = reqLine.finditer(log)
        for m in matches:
            data = m.groupdict()
            rpath = data.get('path')
            reqtime = data.get('reqtime')
            reqid = data.get('reqid')
            rdate = data.get('date')
            rtime = data.get('time')
    
            d = datetime.strptime("%s %s" % (rdate, rtime), "%Y-%m-%d %H:%M:%S")
    
            if start_from and d<start_from:
                continue
            if end_at and d>end_at:
                break
    
            # include only...
            stop = False
            if options.includes:
                stop = True
                for i in options.includes:
                    if re.search(i, rpath, re.IGNORECASE) is not None:
                        stop = False
                        break
            if stop:
                continue
            
            if not min_date or d<min_date:
                min_date = d
            if not max_date or d>min_date:
                max_date = d        
    
            match = pathLine.match(rpath)
            if match:
                path = match.groups()[0]
                if not stats.get(path):
                    stats[path] = {}
                stats[path][reqid] = reqtime
            else:
                logger.error("Line %s does not match" % rpath)
    
    ### Step 2. get stats
    unordered_stats = {}
    for path, tempstat in stats.items():
        unordered_stats[path] = stat_data.copy()
        unordered_stats[path]['count'] = len(tempstat.keys()) 
        unordered_stats[path]['totaltime'] = sum([float(x) for x in tempstat.values()])
        unordered_stats[path]['reqids'] = tempstat.keys()
    
    ### Step 3. final results
    final_stats = OrderedDict(sorted(unordered_stats.items(), key=lambda t: float(t[1]['totaltime'])))
    
    print "Stats from %s to %s\n" % (min_date, max_date)
    logset = final_stats.items()
    if options.log_size is not None and len(logset)>options.log_size:
        logset = logset[-options.log_size:]
    
    cnt = len(logset)
    for k,v in logset:
        print "----\n%s %s\n    %d - %s (%s)\n" % (cnt, k, v['count'], v['totaltime'], timedelta(seconds=float(v['totaltime'])))
        if cnt:
            cnt-=1

if __name__ == '__main__':
    main()
