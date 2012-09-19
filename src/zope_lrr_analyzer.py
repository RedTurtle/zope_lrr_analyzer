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

version = "0.2"
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
p.add_option('--keep-request-id', '-r', dest="keep_req_id", default=False, action="store_true",
             help="Use request and thread ids to handle every match as a different entry")


logger = logging.getLogger("zope_lrr_analyzer")

PATTERN = """^------$
^(?P<date>\d{4}-\d{2}-\d{2})T(?P<time>\d\d\:\d\d\:\d\d).*?$
^Request (?P<reqid>\d*?) "(?P<path>.*?)" running in thread (?P<threadid>\d*?) since (?P<reqtime>\d*?\.\d*?)s$
.*?
^$"""

PATH_PARRENT = """^(?P<path>.*?)(?:\?.*?)?$"""

reqLine = re.compile(PATTERN, re.M|re.S)
pathLine = re.compile(PATH_PARRENT, re.M|re.S)

stats = {}
stat_data = {'count': 0, 'totaltime': 0, 'req-thread-ids': [], 'start': None, 'end': None}

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
            threadid = data.get('threadid')
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
                # default case: store a record for every different path
                if not options.keep_req_id:
                    path = match.groups()[0]
                # alternative case: store a record for request/thread id
                else:
                    path = "%s|%s|%s" % (match.groups()[0], reqid, threadid)
                if not stats.get(path):
                    stats[path] = {}

                if not stats[path].get("%s-%s" % (reqid, threadid)):
                    stats[path]["%s-%s" % (reqid, threadid)] = {'reqtime': 0, 'start': d, 'end': None}
                stats[path]["%s-%s" % (reqid, threadid)]['reqtime'] = reqtime
                stats[path]["%s-%s" % (reqid, threadid)]['end'] = d
            else:
                logger.error("Line %s does not match" % rpath)
    
    ### Step 2. get stats
    unordered_stats = {}
    for path, tempstat in stats.items():
        unordered_stats[path] = stat_data.copy()
        request_data = tempstat.values()
        unordered_stats[path]['count'] = len(tempstat.keys()) 
        unordered_stats[path]['totaltime'] = sum([float(x['reqtime']) for x in request_data])
        unordered_stats[path]['req-thread-ids'] = tempstat.keys()
        if options.keep_req_id:
            unordered_stats[path]['start'] = request_data[0]['start']
            unordered_stats[path]['end'] = request_data[0]['end']
    
    ### Step 3. final results
    final_stats = OrderedDict(sorted(unordered_stats.items(), key=lambda t: float(t[1]['totaltime'])))
    
    print "Stats from %s to %s\n" % (min_date, max_date)
    logset = final_stats.items()
    if options.log_size is not None and len(logset)>options.log_size:
        logset = logset[-options.log_size:]
    
    cnt = len(logset)
    for k,v in logset:
        if not options.keep_req_id:
            print "----\n%s %s\n    %d - %s (%s)\n" % (cnt, k, v['count'], v['totaltime'], timedelta(seconds=float(v['totaltime'])))
        else:
            path, reqid, threadid = k.split('|')
            print "----\n%s %s (request %s/thread %s)\n    %s (%s) - from %s to %s\n" % (cnt, path, reqid, threadid, v['totaltime'],
                                                                                         timedelta(seconds=float(v['totaltime'])),
                                                                                         v['start'], v['end'],
                                                                                         )
        if cnt:
            cnt-=1

if __name__ == '__main__':
    main()
