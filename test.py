#!/usr/bin/env python

import nrtlib

def parameters():
  nrtlib.addParameter('testparam', default='hello', description='A test parameter')

def loaders():
  print 'loaders'

def modules():
  print 'modules'




