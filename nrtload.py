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
def makeSkeleton():
  return """#!/usr/bin/env python
import nrtlib

def parameters():
  # Add parameters that will accessible to this loading script.
  # Any parameters added here can be accessed in any of the other methods by calling:
  #   nrtlib.getParameter('paramname')
  # Notes:
  #  - You cannot call getParameter(...) inside of the parameters() method.
  #  - You must specify either a dataType, or a default (in which case the dataType is inferred).
  #  - If you don't specify a default (or specify it as None), then the parameter will be 'required'
  nrtlib.addParameter('paramname', default=4.2, description='A demo parameter', dataType=float)

def loaders():
  # Add an nrtLoader to this loading script. The loader will be launched on the 
  # requested host when this script is executed.
  nrtlib.addLoader(name='loadername', host='hostname', user='yourname')

def includes():
  # Read in another load file. If it adds parameters in its parameters() method, then 
  # you can set those here. 
  nrtlib.addInclude('includefile.py',
      parameters = {'param1' : 1.0,
                    'param2' : 'hello, world'})

def modules():
  # Add a module to a particular loader.
  nrtlib.addModule(
    loader='loadername',
    path='path/to/your/module',
    instancename = 'MyCoolModule1',
    parameters = {'moduleparam1' : 'param1value',
                  'moduleparam2' : 99.99 },
    subscribertopicfilters = {'subscriberportname' : 'interestingtopics.*'},
    checkertopicfilters = {'checkerportname' : 'asynctopics[0-9]*'},
    postertopics = {'posterportname1' : 'mycoolpostertopic'},
    position = (0,0))"""

######################################################################
def inspect(scriptFilename):
  print 'Parameters:'
  for paramname in nrtlib.__parameters:
    parameter = nrtlib.__parameters[paramname]
    if parameter['sourcefile'] == scriptFilename:
      print '  ' + paramname + ' (' + parameter['description'] + ')'
      print '    ' + ' default: [' + str(parameter['default']) + '],',
      print 'current: [' + str(parameter['value']) + ']'

  print 'Loaders:'
  for loadername in nrtlib.__loaders:
    loader = nrtlib.__loaders[loadername]
    print '  ' + loadername + ': ' + loader['user'] + '@' + loader['host'] + ' (added by ' + loader['source'] + ')'

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
      help="verbose output", action="store_true") 
  parser.add_option("-i", "--inspect", dest="inspect",
      help="display information (parameters, loaders, etc) and exit", action="store_true") 
  parser.add_option("-s", "--skeleton", dest="skeleton",
      help="create a skeleton load file and exit", action="store_true") 

  (options, args) = parser.parse_args()
  if len(args) < 1 and not options.skeleton:
    parser.error("No loadfile specified")

  # Are we just making a skeleton?
  if options.skeleton:
    if len(args) < 1:
      print makeSkeleton()
    else:
      filename = args[0]
      if os.path.exists(filename):
        parser.error("Cannot overwrite a file when creating a skeleton. Please specify a new filename (or no filename at all.")
      with open(filename, 'w') as f:
        f.write(makeSkeleton())
    exit(0)

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
  nrtlib.__topLevelFilename = loadfilename
  loadfile = nrtlib.addInclude(loadfilename, parameters)

  # If we're just inspecting, print out some info and exit
  if nrtlib.__inspectMode:
    inspect(loadfilename)
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

