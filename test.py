#!/usr/bin/env python
import nrtlib

def parameters():
  nrtlib.addParameter('local', default=True, description='Run this script locally')

def loaders():
  nrtlib.addLoader(name='main', host='localhost', user='rand')

def includes():
  nrtlib.addInclude('${TEST_WORKSPACE}/testinclude.py')

def modules():
  pass

