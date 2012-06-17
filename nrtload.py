#!/usr/bin/env python

import nrtlib
from optparse import OptionParser
import logging
import time
import os
import signal

######################################################################
def signal_handler(signal, frame):
  logging.display('Shutting down cleanly')
  nrtlib.cleanUpAndExit(0)

######################################################################
def showParameters():
  print 'Parameters:'
  for paramname in nrtlib.__parameters:
    parameter = nrtlib.__parameters[paramname]
    print '  ' + paramname + '\t' + parameter['description']
    print '\t\t' + ' default: [' + str(parameter['default']) + ']\n'

######################################################################
if __name__ == '__main__':
  signal.signal(signal.SIGINT, signal_handler)

  usage = "usage: %prog [options] loadfile.py [-- loadfileoptions]"
  parser = OptionParser(usage=usage)

  parser.add_option("-v", "--verbose", dest="verbose",
      help="Verbose output", action="store_true") 

  parser.add_option("-p", "--parameters", dest="parameters",
      help="List all parameters of the loading script and exit", action="store_true") 

  (options, args) = parser.parse_args()
  if len(args) < 1:
    parser.error("No loadfile specified")

  logging.DISPLAY = 60
  logging.addLevelName(logging.DISPLAY, 'NRTLOAD')
  logging.display = lambda *kargs: logging.log(logging.DISPLAY, *kargs)
  # Set up verbosity
  if options.verbose:
    loglevel = logging.DEBUG
  else:
    loglevel = logging.WARN
  logging.basicConfig(level=loglevel, format="%(levelname)s %(message)s")

  # Load the script
  loadfilename = args[0]
  loadfile = nrtlib.__loadScript(loadfilename)

  # Handle the script parameters
  loadfile.parameters()
  if options.parameters:
    showParameters()
    nrtlib.cleanUpAndExit(0)
  parameters = {}
  for p in args[1:]:
    split = p.split('=')
    if len(split) == 2:
      parameters[split[0]] = split[1]
    else:
      logging.fatal('Error parsing parameter "' + p + '". Parameters must be specified as name=value')
      nrtlib.cleanUpAndExit(-1)
  nrtlib.__setParameters(parameters)

  # Set up logging
  nrtlib.__logdirectory = os.path.expanduser('~/.nrt/logs/')
  try:
    os.makedirs(nrtlib.__logdirectory)
  except OSError as e:
    if e[1] != 'File exists':
      logging.fatal('Could not access logging directory "' + nrtlib.__logdirectory + '" : ' + str(e))
      nrtlib.cleanUpAndExit(-1)

  logging.display('Logging loader outputs to ' + os.path.join(nrtlib.__logdirectory, '*.log'))

  # Start up the loaders
  loadfile.loaders()

  # Load the modules
  loadfile.modules()

  logging.display('Network loaded - waiting... (Press ctrl-c to close network)')
  # Wait for everyone to finish
  while(True):
    numRunning = [loader['channel'].exit_status_ready() for loader in nrtlib.__loaders.values()].count(False)
    if numRunning == 0:
      exit_status = 0
      if [loader['channel'].exit_status for loader in nrtlib.__loaders.values()].count(0) != len(nrtlib.__loaders):
        exit_status = -1
      logging.debug('All loaders have exited (with minimum exit status ' + str(exit_status) + ')')
      nrtlib.cleanUpAndExit(exit_status)

    nrtlib.__processLogs()
    time.sleep(0.1)



