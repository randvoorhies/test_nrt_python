#!/usr/bin/env
import sys
import os
import logging
import paramiko
import socket
import time
import traceback

__parameters       = {}
__loaders          = {}
__logdirectory     = None
__inspectMode      = False
__currFile         = ''
__paramsAvailable  = False
__topLevelFilename = ''

######################################################################
def __getLineNumber():
  for trace in traceback.extract_stack():
    if trace[0] == __currFile:
      return trace[1]
  return None

######################################################################
def fatal(message):
  tracemessage = ''
  lineno = __getLineNumber()
  if lineno is not None:
    tracemessage = '[' + __currFile + ':' + str(lineno) + '] '
  logging.fatal(tracemessage + message)
  cleanUpAndExit(-1)

######################################################################
def cleanUpAndExit(exitcode):
  """Close down all loaders cleanly, and exit with the given exitcode.
  
  This is the prefered way to exit from a script if you detect some error.
  """
  logging.info('Cleaning up and exiting with error code ' + str(exitcode))

  # Close down all of the loaders
  if not __inspectMode:
    for loadername in __loaders:
      __loaders[loadername]['sshclient'].close()

    # Keep dumping logs for another few seconds
    maxtime = time.time() + 3
    while __processLogs() == True and time.time() < maxtime: pass

  exit(exitcode)

######################################################################
def addLoader(name, host, user=None, password=None, key=None, key_filename=None):
  """Request a loader with the given name to be started on the given host.
  
  Loaders should only be added inside of the "loaders()" method of a loading script.
  """
  global __loaders
  if name in __loaders:
    if __loaders[name]['host'] == host:
      logging.info('Skipping loader "' + name +'"')
    else:
      fatal('Duplicate loader name found ("' + name + '")' +
      ' with different hosts ("' + host + '", "' + __loaders[name]['host'] + '")')
    return
  else:
    logging.info('Adding loader "' + name +'" on host "' + host + '"')

  nrtloader = '/Users/rand/Desktop/spin'

  __loaders[name] = {}
  __loaders[name]['host'] = host
  __loaders[name]['user'] = user
  __loaders[name]['source'] = __currFile

  if not __inspectMode:
    try:
      connectionTimeout = 10

      __loaders[name]['sshclient'] = paramiko.SSHClient()
      __loaders[name]['sshclient'].load_system_host_keys()
      __loaders[name]['sshclient'].set_missing_host_key_policy(paramiko.AutoAddPolicy())
      logging.info('Connecting to ' + host + '... (will timeout after ' + str(connectionTimeout) + 's)')
      __loaders[name]['sshclient'].connect(host, username=user, password=password,
          pkey=key, key_filename=key_filename, timeout=connectionTimeout)
      logging.info('Connected to ' + host)
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
      del __loaders[name]
      fatal('Could not add loader "' + name + '" on host "' + host + '" (' + e.strerror + ')')
    except socket.timeout as e:
      del __loaders[name]
      fatal('Timed out when connecting to host "' + host + '"')
    except paramiko.AuthenticationException:
      del __loaders[name]
      fatal('Failed to authenticate on host "' + host + '" with user="' + str(user) + '"')

######################################################################
def addInclude(filename, parameters = {}):
  global __currFile, __paramsAvailable
  filename = os.path.expandvars(filename)
  __currFile = filename

  logging.info('Adding included file "' + filename + '"')
  if not os.path.exists(filename):
    fatal('Could not find file: ' + filename)

  directory = os.path.dirname(filename)
  sys.path.insert(0, directory)

  # Get the module name
  module_name = os.path.basename(filename)
  if module_name[-3:] == '.py':
    module_name = module_name[:-3]
  loadfile = __import__(module_name)

  # Handle the script parameters
  __paramsAvailable = False
  if 'parameters' in loadfile.__dict__:
    loadfile.parameters()
    __processParameters(parameters)
  else:
    logging.info('No parameters() section found in "' + filename +'"')
  __paramsAvailable = True

  # Add the loaders
  if 'loaders' in loadfile.__dict__:
    loadfile.loaders()
  else:
    logging.info('No loaders() section found in "' + filename +'"')

  currFile = __currFile
  # Add the includes
  if 'includes' in loadfile.__dict__:
    loadfile.includes()
  else:
    logging.info('No includes() section found in "' + filename +'"')
  __currFile = currFile

  # Add the modules
  if 'modules' in loadfile.__dict__:
    loadfile.modules()
  else:
    logging.info('No modules() section found in "' + filename +'"')


######################################################################
def addParameter(name, default=None, description='', dataType=None):
  """Add a parameter to your loading script. 
  
  Parameters should only be added inside of the "parameters()" method of a loading script.
  """
  global __parameters

  if dataType is None:
    if default is not None:
      dataType = type(default)
    else:
      dataType = str
  
  logging.info('Registering parameter "' + name + '" ' + str(dataType))

  try:
    dataType(default)
  except ValueError:
    message = ''
    try:
      message = 'Default value "' + str(default) +\
          '" for parameter "' + name + '" cannot be converted into dataType ' + str(dataType) + ''
    except:
      message = 'Default value for parameter "' + \
          name + '" cannot be converted into dataType ' + str(dataType) + ''
    finally:
      fatal(message)

  if name in __parameters:
    logging.warn('Duplicate parameters added: "' + name + '"')

  value = dataType(default)
  if default is None: value = None

  lineno = str(__getLineNumber())

  __parameters[name] = {
      'default'     : default,
      'description' : description,
      'value'       : value,
      'dataType'    : dataType,
      'sourcefile'  : __currFile,
      'sourceline'  : lineno
      }

######################################################################
def getParameter(name):
  """Get the value of a parameter that was added with the addParameter method"""
  logging.info('Getting parameter "' + name + '"')


  if not __paramsAvailable:
    fatal('Trying to access a Parameter in parameters() method. Parameter values are not available here.')

  if name not in __parameters:
    fatal('No parameter named "' + name + '"')
  return __parameters[name]['value']

######################################################################
def __processLogs():
  """Write any buffered output from loaders to their respective log files."""
  global __loaders
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
def __processParameters(parameters):
  global __parameters
  logging.info('Setting Parameters')

  for paramname in parameters:
    if paramname not in __parameters:
      fatal('No parameter named "' + paramname + '". Use the --help option to learn how to list parameters.')
    try:
      paramvalue = __stringToParamValue(parameters[paramname], __parameters[paramname]['dataType'])
      logging.info('Setting parameter "' + paramname + '" to value [' + str(paramvalue) + ']')
      __parameters[paramname]['value'] = paramvalue
    except ValueError:
      parameter = __parameters[paramname]
      message =  'Could not set parameter "' + paramname + '"'
      message += ' to "' + parameters[paramname] + '" as ' + str(parameter['dataType'])
      message += ' (defined here: ' + parameter['sourcefile'] + ':' + str(parameter['sourceline']) + ')'
      fatal(message)

  for paramname in __parameters:
    if __parameters[paramname]['value'] is None:
      fatal('Parameter "' + paramname + '" was not set, and has no default value.')
