#!/usr/bin/env python
import nrtlib

def parameters():
  nrtlib.addParameter('local', default=True, description='Run this script locally')

def loaders():
  mainhost = 'ilab1.usc.edu'
  if nrtlib.getParameter('local'):
    mainhost = 'localhost'

  nrtlib.addLoader(name='main', host=mainhost, user='rand')

def includes():
  auxhost = 'ilab1'
  if nrtlib.getParameter('local'):
    auxhost = 'localhost'

  nrtlib.addInclude('${TEST_WORKSPACE}/testinclude.py',
      parameters = {'auxloader' : auxhost})

def modules():
  pass

