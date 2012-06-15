#!/usr/bin/env
import sys
import os
import logging
import paramiko

__parameters = {}
__loaders = {}

######################################################################
def cleanUpAndExit(exitcode):
  logging.debug('Cleaning up and exiting with error code ' + str(exitcode))

  for loadername in __loaders:
    loader = __loaders[loadername]
    loader['channel'].shutdown(2)

  # TODO: Print a stack trace if exit code is not 0
  exit(exitcode)

def startLoader(name, host, username=None, password=None):
  logging.debug('Starting loader "' + name +'" on host "' + host + '"')
  __loaders[name] = {}
  __loaders[name]['sshclient'] = paramiko.SSHClient()
  __loaders[name]['sshclient'].load_system_host_keys()
  __loaders[name]['sshclient'].set_missing_host_key_policy(paramiko.AutoAddPolicy())
  __loaders[name]['sshclient'].connect(host, username=username, password=password)
  __loaders[name]['transport'] = __loaders[name]['sshclient'].get_transport()
  __loaders[name]['channel'] = __loaders[name]['transport'].open_session()
  __loaders[name]['channel'].exec_command('/Users/rand/Desktop/spin')

######################################################################
def addParameter(name, default=None, description='', dataType=None):
  if dataType is None:
    if default is not None:
      dataType = type(default)
    else:
      dataType = str
  
  logging.debug('Registering parameter "' + name + '" ' + str(dataType))

  try:
    dataType(default)
  except ValueError:
    try:
      logging.fatal('Default value "' + str(default) +
          '" for parameter "' + name + '" cannot be converted into dataType ' + str(dataType) + '')
    except:
      logging.fatal('Default value for parameter "' + name +
          '" cannot be converted into dataType ' + str(dataType) + '')
    finally:
      cleanUpAndExit(-1)

  if name in __parameters:
    logging.warn('Duplicate parameters added: "' + name + '"')

  value = dataType(default)
  if default is None: value = None

  __parameters[name] = {
      'default'     : default,
      'description' : description,
      'value'       : value,
      'dataType'    : dataType
      }

######################################################################
def getParameter(name):
  logging.debug('Getting parameter "' + name + '"')
  if name not in __parameters:
    logging.fatal('No parameter named "' + name + '"')
    cleanUpAndExit(-1)
  return __parameters[name]['value']

######################################################################
def __stringToParamValue(value, dataType):
  if dataType is bool:
    if value.lower() == 'true' or value == '1' or value.lower() == 't':
      return True
    elif value.lower() == 'false' or value == '0' or value.lower() == 'f':
      return False
    else:
      raise ValueError
  else:
    return dataType(value)

######################################################################
def __setParameters(parameters):
  logging.debug('Setting Parameters')

  for paramname in parameters:
    if paramname not in __parameters:
      logging.fatal('No parameter named "' + paramname + '". Use the --help option to learn how to list parameters.')
      cleanUpAndExit(-1)

    try:
      paramvalue = __stringToParamValue(parameters[paramname], __parameters[paramname]['dataType'])
      logging.debug('Setting parameter "' + paramname + '" to value [' + str(paramvalue) + ']')
      __parameters[paramname]['value'] = paramvalue
    except ValueError:
      logging.fatal('Could not set parameter "' + paramname +
          '" to "' + parameters[paramname] + '" as ' + str(__parameters[paramname]['dataType']))
      cleanUpAndExit(-1)

  for paramname in __parameters:
    if __parameters[paramname]['value'] is None:
      logging.fatal('Parameter "' + paramname + '" was not set, and has no default value.')
      cleanUpAndExit(-1)
                     
######################################################################
def __loadScript(filename):
  logging.debug('Loading file [' + filename + ']')
  directory = os.path.dirname(filename)
  sys.path.insert(0, directory)

  module_name = os.path.basename(filename)
  if module_name[-3:] == '.py':
    module_name = module_name[:-3]
  return __import__(module_name)


