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
import colorama
from colorama import Fore, Style

import argparse
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

import threading

class CommandExecutor(threading.Thread):
    """executes a command on demand"""
    def __init__(self, working_dir, command):
        super(CommandExecutor, self).__init__()
        self.working_dir = working_dir
        self.command = command
        
        self.daemon = True
        self._shutdown = False
        self._event = threading.Event()
    
    def trigger(self):
        self._event.set()
    
    def run(self):
        logging.debug("in run_command")
        while not self._shutdown:
            time.sleep(0.5)
            
            if self._event.is_set():
                # clear the screen
                print '%s2J' % (colorama.ansi.CSI,)
                
                print '%s==>%s Running: %s%s' % (Fore.YELLOW, Fore.CYAN, " ".join(self.command), Style.RESET_ALL)
                
                try:
                    subprocess.check_call(self.command, cwd = self.working_dir)
                    
                    print '%s==>%s SUCCESS%s' % (Fore.YELLOW, Fore.GREEN, Style.RESET_ALL)
                
                except subprocess.CalledProcessError, e:
                    logging.error(e)
                    print '%s==>%s FAILURE%s' % (Fore.YELLOW + Style.BRIGHT, Fore.RED, Style.RESET_ALL)
                
                except OSError, e:
                    raise RuntimeError("Unable to invoke %s: %s" % (" ".join(self.command), e))
                
                # wait a sec and then clear the event; this keeps the build command
                # from triggering another build (if it changed files, which is likely)
                time.sleep(2)
                self._event.clear()
                
                print '%s==>%s ready%s' % (Fore.YELLOW, Fore.BLUE, Style.RESET_ALL)


class EventHandler(FileSystemEventHandler):
    """FileSystemEventHandler with custom dispatch logic"""
    def __init__(self, commandExecutor):
        super(EventHandler, self).__init__()
        self.commandExecutor = commandExecutor
    
    def dispatch(self, event):
        if "/.git" not in event.src_path:
            self.commandExecutor.trigger()

def main():
    parser = argparse.ArgumentParser(description="the simplest CI you ever did see")
    parser.add_argument("watch_dir", help="directory to watch")
    parser.add_argument("command_and_args", nargs="+", help="command to execute")
    
    parsed_args = parser.parse_args()

    colorama.init(autoreset=False)
    sys.stdin.close()
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] - %(message)s",
    )
    
    watchDir = os.path.abspath(parsed_args.watch_dir)
    
    commandExecutor = CommandExecutor(watchDir, parsed_args.command_and_args)
    eventHandler = EventHandler(commandExecutor)

    observer = Observer()
    observer.schedule(eventHandler, watchDir, recursive=True)

    observer.start()
    commandExecutor.start()
    
    logging.info("ready")
    commandExecutor.trigger()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    
    observer.join()

if __name__ == '__main__':
    main()

