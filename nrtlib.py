#!/usr/bin/env

import sys
import os
import logging

__parameters = []
def addParameter(name, default=None, description=''):
  logging.debug('Registering Parameter [' + name + ']')
  __parameters.append({
    'name' : name,
    'default' : default,
    'description' : description })
                     
######################################################################
def loadScript(filename):
  logging.debug('Loading file [' + filename + ']')
  directory = os.path.dirname(filename)
  sys.path.insert(0, directory)

  module_name = os.path.basename(filename)
  if module_name[-3:] == '.py':
    module_name = module_name[:-3]
  return __import__(module_name)





#def loadModule(path, loader, parameters = [],
#    subscribertopicfilters = [], checkertopicfilters = [], postertopics = [], 
#    instancename = 'NRT_AUTO_#', position = (0,0), namespace = None):
#    pass


######################################################################
#def loadMacroModule(path, instancename, parameters={},
#    subscribertopicfilters={}, checkertopicfilters={}, postertopics={}, position=(0,0)):
#  """ Load a MacroModule (an NRT python loading script) """
#
#  if len(logicalpath) == 0:
#    raise Exception('Empty logical path name requested from loadmacromodule')
#
#  if logicalpath[0] == '/':
#    logicalpath = logicalpath[1:]
#
#  if logicalpath[-3:] != '.py':
#    logicalpath = logicalpath + '.py'
#
#  originalpath = list(sys.path)
#  oldnamespace = currentNamespace()
#  newnamespace = os.path.join(oldnamespace, instancename)
#  setNamespace(newnamespace)
#  setQuietSuspend(True)
#
#  try:
#    if not os.environ.has_key('NRTMACROMODULEPATH'):
#      raise Exception('You must define a ${NRTMACROMODULEPATH} environment variable ' +
#                      'in order to load MacroModules')
#  
#    macromodulepaths = os.environ['NRTMACROMODULEPATH'].split(':')
#    abspath = ''
#    for macromodulepath in macromodulepaths:
#      if os.path.exists(os.path.join(macromodulepath, logicalpath)):
#        abspath = os.path.join(macromodulepath, logicalpath);
#        break;
#    if abspath == '':
#      raise Exception('Could not find macromodule ' + logicalpath + ' in NRTMACROMODULEPATH')
#  
#    directory, module_name = os.path.split(abspath)
#    module_name = os.path.splitext(module_name)[0]
#    sys.path.insert(0, directory)
#    module = None
#    module = __import__(module_name)
#
#    # Call the setup() method on the macromodule
#    module.setup()
#
#    # Set the parameters for this macromodules
#    for paramname, paramvalue in parameters.iteritems():
#      getMacroParameter(paramname).setValue(paramvalue)
#
#    # Call the load() method on the macromodule
#    module.load()
#
#    # Set the border connector subscriber topic filters
#    for conname, confilter in subscribertopicfilters.iteritems():
#      modifyConnectorTopic(namespace=newnamespace, portname=conname, topic=confilter,topicorfilter='filter')
#
#    # Set the border connector checker topic filters
#    for conname, confilter in checkertopicfilters.iteritems():
#      modifyConnectorTopic(namespace=newnamespace, portname=conname, topic=confilter,topicorfilter='filter')
#
#    # Set the border poster checker topics
#    for conname, contopic in postertopics.iteritems():
#      modifyConnectorTopic(namespace=newnamespace, portname=conname, topic=contopic,topicorfilter='topic')
#
#    # Set the position of the macromodule
#    __sendCommand__({'command' : 'setguidata',
#                     'key'     : 'n:' + newnamespace,
#                     'x'       : position[0],
#                     'y'       : position[1]})
#
#  finally:
#    sys.path[:] = originalpath
#    setNamespace(oldnamespace)
#    setQuietSuspend(False)
#
#
#
