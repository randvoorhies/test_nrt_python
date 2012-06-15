#!/usr/bin/env python

import nrtlib
from optparse import OptionParser
import logging

def showParameters():
  for parameter in nrtlib.__parameters:
    print parameter['name'], '\t', parameter['description'], '[', parameter['default'], ']'

usage = "usage: %prog [options] loadfile.py [-- loadfileoptions]"
parser = OptionParser(usage=usage)

parser.add_option("-v", "--verbose", dest="verbose",
    help="Verbose output", action="store_true") 

parser.add_option("-p", "--parameters", dest="parameters",
    help="List all parameters of the loading script and exit", action="store_true") 

(options, args) = parser.parse_args()
if len(args) < 1:
  parser.error("No loadfile specified")

if options.verbose:
  logging.basicConfig(level=logging.DEBUG)

loadfilename = args[0]

loadfile = nrtlib.loadScript(loadfilename)

loadfile.parameters()

if options.parameters:
  showParameters()
  exit(0)


loadfile.loaders()
loadfile.modules()


