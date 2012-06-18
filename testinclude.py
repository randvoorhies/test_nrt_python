#!/usr/bin/env python
import nrtlib

def parameters():
  nrtlib.addParameter('radparam', default=99, description='A truly radical parameter')

def loaders():
  nrtlib.addLoader(name='auxilliary', host='localhost', user='rand')

def includes():
  pass

def modules():
  pass
