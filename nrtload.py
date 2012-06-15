#!/usr/bin/env python

import nrtlib
from optparse import OptionParser
import logging

######################################################################
def showParameters():
  print 'Parameters:'
  for paramname in nrtlib.__parameters:
    parameter = nrtlib.__parameters[paramname]
    print '  ' + paramname + '\t' + parameter['description']
    print '\t\t' + ' default: [' + str(parameter['default']) + ']\n'

######################################################################
if __name__ == '__main__':
  usage = "usage: %prog [options] loadfile.py [-- loadfileoptions]"
  parser = OptionParser(usage=usage)

  parser.add_option("-v", "--verbose", dest="verbose",
      help="Verbose output", action="store_true") 

  parser.add_option("-p", "--parameters", dest="parameters",
      help="List all parameters of the loading script and exit", action="store_true") 

  (options, args) = parser.parse_args()
  if len(args) < 1:
    parser.error("No loadfile specified")

  # Setup logging
  loglevel = logging.WARN
  if options.verbose:
    loglevel = logging.DEBUG
  logging.basicConfig(level=loglevel, format="%(levelname)s (%(module)s.%(funcName)s): %(message)s")

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


  loadfile.loaders()
  loadfile.modules()


