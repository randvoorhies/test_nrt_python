#!/usr/bin/env python

import threading
import time
import paramiko
import sys

def runloader(pipe, hostname, username=None, password=None):
  print 'Connecting'

  # Connect to the remote machine

  while not channel.exit_status_ready():
    # Check the pipe for any messages from the parent process
    if pipe.poll():
      message = pipe.recv()
      print 'Got Message:', message
      sys.stdout.flush()

    if channel.recv_ready():
      print channel.recv(4)
    else:
      time.sleep(0.5)

  exit_status = channel.recv_exit_status()
  print 'Channel exited with status', exit_status
  print channel.recv_stderr(1024)

class loader:

  def __monitor_connection(self):
    print 'Monitoring Connection'
    while self.running and not self.channel.exit_status_ready():
      if self.channel.recv_ready():
        print self.channel.recv(1028)

    if self.channel.exit_status_ready():
      exit_status = self.channel.recv_exit_status()
      print 'Channel exited with status', exit_status
      print self.channel.recv_stderr(1024)

  def __init__(self, hostname, username=None, password=None):
    print 'Starting loader', hostname

    sshclient = paramiko.SSHClient()
    sshclient.load_system_host_keys()
    sshclient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    sshclient.connect(hostname, username=username, password=password)
    transport = sshclient.get_transport()
    self.channel = transport.open_session()
    self.channel.exec_command('/Users/rand/Desktop/spin')

    self.running = True
    self.thread = threading.Thread(target = self.__monitor_connection)
    self.thread.start()

  def __del__(self):
    print 'Quitting loader'

    self.running = False
    self.thread.join()



if __name__ == '__main__':
  l = loader('127.0.0.1')
  print 'Sleeping...'
  time.sleep(5)
  print 'Done sleeping'
