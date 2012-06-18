#!/usr/bin/env python

import nrtlib
from optparse import OptionParser
import logging
import time
import os
import signal

######################################################################
def shutdown(exitstatus):
  nrtlib.cleanUpAndExit(exitstatus)

######################################################################
def signal_handler(signal, frame):
  logging.display('Shutdown requested...')
  shutdown(0)

######################################################################
def inspect():
  print 'Parameters:'
  for paramname in nrtlib.__parameters:
    parameter = nrtlib.__parameters[paramname]
    print '  ' + paramname + ' (' + parameter['description'] + ')'
    print '    ' + ' default: [' + str(parameter['default']) + '],',
    print 'current: [' + str(parameter['value']) + ']'

  print 'Loaders:'
  for loadername in nrtlib.__loaders:
    loader = nrtlib.__loaders[loadername]
    print '  ' + loadername + ': ' + loader['user'] + '@' + loader['host']

######################################################################
def parseScriptParameters(args):
  parameters = {}
  for p in args:
    split = p.split('=')
    if len(split) == 2:
      parameters[split[0]] = split[1]
    else:
      logging.fatal('Error parsing parameter "' + p + '". Parameters must be specified as name=value')
      nrtlib.cleanUpAndExit(-1)
  return parameters

######################################################################
if __name__ == '__main__':
  signal.signal(signal.SIGINT, signal_handler)

  usage = "usage: %prog [options] loadfile.py [-- loadfileoptions]"
  parser = OptionParser(usage=usage)
  parser.add_option("-v", "--verbose", dest="verbose",
      help="Verbose output", action="store_true") 
  parser.add_option("-i", "--inspect", dest="inspect",
      help="Display information (parameters, loaders, etc) and exit.", action="store_true") 

  (options, args) = parser.parse_args()
  if len(args) < 1:
    parser.error("No loadfile specified")

  # Should we just inspect the script?
  nrtlib.__inspectMode = options.inspect

  # Set up message logging
  logging.DISPLAY = 60
  logging.addLevelName(logging.DISPLAY, 'NRTLOAD')
  logging.addLevelName(logging.FATAL, 'FATAL')
  logging.display = lambda *kargs: logging.log(logging.DISPLAY, *kargs)
  if options.verbose:
    loglevel = logging.INFO
  else:
    loglevel = logging.WARN
  logging.basicConfig(level=loglevel, format="%(levelname)s %(message)s")

  # Set up loader logging
  if not nrtlib.__inspectMode:
    nrtlib.__logdirectory = os.path.expanduser('~/.nrt/logs/')
    try:
      os.makedirs(nrtlib.__logdirectory)
    except OSError as e:
      if e[1] != 'File exists':
        logging.fatal('Could not access logging directory "' + nrtlib.__logdirectory + '" : ' + str(e))
        nrtlib.cleanUpAndExit(-1)

    logging.display('Logging loader outputs to ' + os.path.join(nrtlib.__logdirectory, '*.log'))

  # Grab the parameters from the command line
  parameters = parseScriptParameters(args[1:])

  # Load the file
  loadfilename = args[0]
  loadfile = nrtlib.addInclude(loadfilename, parameters)

  # If we're just inspecting, print out some info and exit
  if nrtlib.__inspectMode:
    inspect()
    exit(0)

  # Wait for everyone to finish
  logging.display('Network loaded - waiting... (Press ctrl-c to close network)')
  while(True):
    numRunning = [loader['channel'].exit_status_ready() for loader in nrtlib.__loaders.values()].count(False)
    if numRunning == 0:
      exit_status = 0
      if [loader['channel'].exit_status for loader in nrtlib.__loaders.values()].count(0) != len(nrtlib.__loaders):
        exit_status = -1
      logging.display('All loaders have exited (with minimum exit status ' + str(exit_status) + ')')
      shutdown(exit_status)

    nrtlib.__processLogs()
    time.sleep(0.1)

