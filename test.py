#!/usr/bin/env python

import nrtlib

def parameters():
  nrtlib.addParameter('testparam', default=4,     description='A test parameter')
  nrtlib.addParameter('local',     default=False, description='Run this script locally')

def loaders():
  nrtlib.startLoader(name='gpu', host='localhost', username='rand')
  nrtlib.startLoader(name='cpu', host='localhost', username='rand')

def modules():
  print 'modules'

