#!/usr/bin/env python
import nrtlib

def parameters():
  nrtlib.addParameter('local', default=True, description='Run this script locally')

def loaders():
  if nrtlib.getParameter('local'): 
    nrtlib.addLoader(name='main', host='localhost', user='rand')
  else:
    nrtlib.addLoader(name='main', host='ilab21', user='rand')

def includes():
  auxhost = 'ilab1'
  if nrtlib.getParameter('local'):
    auxhost = 'localhost'

  nrtlib.addInclude('${TEST_WORKSPACE}/testinclude.py',
      parameters = {'auxloader' : auxhost,
                    'test' : 4})

def modules():
  pass

