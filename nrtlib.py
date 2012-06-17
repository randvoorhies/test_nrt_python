#!/usr/bin/env
import sys
import os
import logging
import paramiko
import socket
import time

__parameters = {}
__loaders = {}
__logdirectory = None
__inspectMode = False

######################################################################
def cleanUpAndExit(exitcode):
  """Close down all loaders cleanly, and exit with the given exitcode.
  
  This is the prefered way to exit from a script if you detect some error.
  """
  logging.info('Cleaning up and exiting with error code ' + str(exitcode))

  # Close down all of the loaders
  for loadername in __loaders:
    __loaders[loadername]['sshclient'].close()

  # Keep dumping logs for another few seconds
  maxtime = time.time() + 3
  while __processLogs() == True and time.time() < maxtime: pass

  exit(exitcode)

######################################################################
def addLoader(name, host, user=None, password=None):
  """Request a loader with the given name to be started on the given host.
  
  Loaders should only be added inside of the "loaders()" method of a loading script.
  """
  if name in __loaders:
    if __loaders[name]['host'] == host:
      logging.info('Skipping loader "' + name +'"')
    else:
      logging.fatal('Duplicate loader name found ("' + name + '")' +
      ' with different hosts ("' + host + '", "' + __loaders[name]['host'] + '")')
      cleanUpAndExit(-1)
    return
  else:
    logging.info('Adding loader "' + name +'" on host "' + host + '"')

  nrtloader = '/Users/rand/Desktop/spin'


  __loaders[name] = {}
  __loaders[name]['host'] = host
  __loaders[name]['user'] = user

  if not __inspectMode:
    try:
      __loaders[name]['sshclient'] = paramiko.SSHClient()
      __loaders[name]['sshclient'].load_system_host_keys()
      __loaders[name]['sshclient'].set_missing_host_key_policy(paramiko.AutoAddPolicy())
      __loaders[name]['sshclient'].connect(host, username=user, password=password)
      __loaders[name]['transport'] = __loaders[name]['sshclient'].get_transport()
      __loaders[name]['channel'] = __loaders[name]['transport'].open_session()
      __loaders[name]['channel'].settimeout(0.1)
      __loaders[name]['channel'].exec_command(nrtloader)

      stdout_logname = os.path.join(__logdirectory, name) + '_stdout.log'
      logging.info('Opening logfile "' + stdout_logname + '"')
      __loaders[name]['stdout'] = open(stdout_logname, 'w')

      stderr_logname = os.path.join(__logdirectory, name) + '_stderr.log'
      logging.info('Opening logfile "' + stderr_logname + '"')
      __loaders[name]['stderr'] = open(stderr_logname, 'w')
    except socket.gaierror as e:
      logging.fatal('Could not add loader "' + name + '" on host "' + host + '" (' + e.strerror + ')')
      del __loaders[name]
      cleanUpAndExit(-1)

######################################################################
def addParameter(name, default=None, description='', dataType=None):
  """Add a parameter to your loading script. 
  
  Parameters should only be added inside of the "parameters()" method of a loading script.
  """
  if dataType is None:
    if default is not None:
      dataType = type(default)
    else:
      dataType = str
  
  logging.info('Registering parameter "' + name + '" ' + str(dataType))

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
  """Get the value of a parameter that was added with the addParameter method"""
  logging.info('Getting parameter "' + name + '"')
  if name not in __parameters:
    logging.fatal('No parameter named "' + name + '"')
    cleanUpAndExit(-1)
  return __parameters[name]['value']

######################################################################
def __processLogs():
  """Write any buffered output from loaders to their respective log files."""
  moreData = False
  maxtime = 0.1
  for name in __loaders:
    try:
      timeout = time.time() + maxtime
      while time.time() < timeout:
        __loaders[name]['stdout'].write(__loaders[name]['channel'].recv(1028))
        __loaders[name]['stdout'].flush()
      if __loaders[name]['channel'].recv_ready():
        moreData = True
    except socket.timeout: pass

    try:
      timeout = time.time() + maxtime
      while time.time() < timeout:
        __loaders[name]['stderr'].write(__loaders[name]['channel'].recv_stderr(1028))
        __loaders[name]['stderr'].flush()
      if __loaders[name]['channel'].recv_stderr_ready():
        moreData = True
    except socket.timeout: pass

  return moreData


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
  logging.info('Setting Parameters')

  for paramname in parameters:
    if paramname not in __parameters:
      logging.fatal('No parameter named "' + paramname + '". Use the --help option to learn how to list parameters.')
      cleanUpAndExit(-1)

    try:
      paramvalue = __stringToParamValue(parameters[paramname], __parameters[paramname]['dataType'])
      logging.info('Setting parameter "' + paramname + '" to value [' + str(paramvalue) + ']')
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
  logging.info('Loading file [' + filename + ']')
  directory = os.path.dirname(filename)
  sys.path.insert(0, directory)

  module_name = os.path.basename(filename)
  if module_name[-3:] == '.py':
    module_name = module_name[:-3]
  return __import__(module_name)


