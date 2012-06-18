#!/usr/bin/env python
import nrtlib

def parameters():
  nrtlib.addParameter('auxloader', default='ilab21', description='The host for the auxiliary computations')
  nrtlib.addParameter('test', default=17, description='testparam')

def loaders():
  nrtlib.addLoader(name='auxiliary', host=nrtlib.getParameter('auxloader'), user='rand')

def includes():
  pass

def modules():
  pass
