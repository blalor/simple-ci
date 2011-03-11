#!/usr/bin/env python
# encoding: utf-8
"""
dir_watcher.py

Created by Brian Lalor <blalor@bravo5.org> on 2011-03-11.
"""

import sys, os
import logging
import subprocess
import time

from FSEvents import \
    FSEventStreamCreate, \
    FSEventStreamStart, \
    FSEventStreamScheduleWithRunLoop, \
    kFSEventStreamEventIdSinceNow, \
    kCFRunLoopDefaultMode, \
    kFSEventStreamEventFlagMustScanSubDirs, \
    kFSEventStreamEventFlagUserDropped, \
    kFSEventStreamEventFlagKernelDropped

from PyObjCTools import AppHelper

from Cocoa import \
    CFRunLoopAddTimer, \
    NSRunLoop, \
    CFRunLoopTimerCreate, \
    CFAbsoluteTimeGetCurrent, \
    kCFRunLoopCommonModes


import threading

# ========= # ========= # ========= # ========= # ========= # ========= #
SUBPROCESS_ARGS = None
WORKING_DIR = None

DO_SHUTDOWN = False
DO_CALL_EVT = threading.Event()

def start_fs_events(path_to_monitor):
    stream_ref = FSEventStreamCreate(
        None,                               # Use the default CFAllocator
        fsevent_callback,
        None,                               # We don't need a FSEventStreamContext
        [path_to_monitor],
        kFSEventStreamEventIdSinceNow,      # We only want events which happen in the future
        1.0,                                # Process events within 1 second
        0                                   # We don't need any special flags for our stream
    )
    
    if not stream_ref:
        raise RuntimeError("FSEventStreamCreate() failed!")
    
    FSEventStreamScheduleWithRunLoop(stream_ref, NSRunLoop.currentRunLoop().getCFRunLoop(), kCFRunLoopDefaultMode)
    
    if not FSEventStreamStart(stream_ref):
        raise RuntimeError("Unable to start FSEvent stream!")
    


def fsevent_callback(stream_ref, full_path, event_count, paths, masks, ids):
    """Process an FSEvent (consult the Cocoa docs) and call each of our handlers which monitors that path or a parent"""
    
    for i in range(event_count):
        path = os.path.dirname(paths[i])
        
        if masks[i] & kFSEventStreamEventFlagMustScanSubDirs:
            recursive = True
        
        if masks[i] & kFSEventStreamEventFlagUserDropped:
            logging.error("We were too slow processing FSEvents and some events were dropped")
            recursive = True
        
        if masks[i] & kFSEventStreamEventFlagKernelDropped:
            logging.error("The kernel was too slow processing FSEvents and some events were dropped!")
            recursive = True
        else:
            recursive = False
        
        logging.debug("FSEvent: %s: for path %s (recursive: %s)" % (i, path, str(recursive)))
        
        DO_CALL_EVT.set()
    


def timer_callback(*args):
    # logging.debug(str(args))
    pass


def run_command():
    logging.debug("in run_command")
    while not DO_SHUTDOWN:
        if DO_CALL_EVT.is_set():
            logging.debug("got event")
            
            # with open("/dev/null", "r") as dev_null:
            try:
                subprocess.check_call(
                    SUBPROCESS_ARGS,
                    cwd = WORKING_DIR,
                    # shell=True,
                    # stdin=dev_null,
                )
            except subprocess.CalledProcessError, e:
                logging.error(e)
            except OSError, e:
                raise RuntimeError("Unable to invoke %s: %s" % (" ".join(SUBPROCESS_ARGS), e))
            
            time.sleep(5)
            logging.debug("clearing event")
            DO_CALL_EVT.clear()
            
    


def main():
    global SUBPROCESS_ARGS, WORKING_DIR, DO_SHUTDOWN
    
    sys.stdin.close()
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] - %(message)s",
    )
    
    path_to_monitor = os.path.abspath(sys.argv[1])
    WORKING_DIR = path_to_monitor
    SUBPROCESS_ARGS = sys.argv[2:]
    
    start_fs_events(path_to_monitor)
    
    # NOTE: This timer is basically a kludge around the fact that we can't reliably get
    #       signals or Control-C inside a runloop. This wakes us up often enough to
    #       appear tolerably responsive:
    CFRunLoopAddTimer(
        NSRunLoop.currentRunLoop().getCFRunLoop(),
        CFRunLoopTimerCreate(None, CFAbsoluteTimeGetCurrent(), 2.0, 0, 0, timer_callback, None),
        kCFRunLoopCommonModes
    )
    
    
    worker = threading.Thread(target = run_command)
    worker.daemon = True
    worker.start()
    
    logging.info("ready")
    
    try:
        AppHelper.runConsoleEventLoop(installInterrupt=True)
    except KeyboardInterrupt:
        logging.info("KeyboardInterrupt received, exiting")
    
    DO_SHUTDOWN = True
    sys.exit(0)
    


if __name__ == '__main__':
    main()

