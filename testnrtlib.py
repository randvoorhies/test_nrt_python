#!/usr/bin/env python

import threading
import time
import paramiko

import signal
import sys

loaders = []

def signal_handler(signal, frame):
  for loader in loaders:
    loader.close()
  sys.exit(0)

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

    self.sshclient = paramiko.SSHClient()
    self.sshclient.load_system_host_keys()
    self.sshclient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    self.sshclient.connect(hostname, username=username, password=password)
    self.transport = self.sshclient.get_transport()
    self.channel = self.transport.open_session()
    self.channel.exec_command('/Users/rand/Desktop/spin')

    self.running = True
    self.thread = threading.Thread(target = self.__monitor_connection)
    self.thread.start()
    loaders.append(self)

  def close(self):
    print 'Closing loader connection'
    self.running = False
    self.thread.join()

  def __del__(self):
    self.close()




if __name__ == '__main__':
  signal.signal(signal.SIGINT, signal_handler)
  l = loader('127.0.0.1', 'rand')
  print 'Sleeping...'
  time.sleep(2)
  print 'Done sleeping'
