#serial connection to lecory power supply

import serial
import time

class lecroy_com:
  #_____________________________________________________________________________
  def __init__(self, port):
    #commands queue
    self.queue = []
    #busy flags
    self.busy = False
    self.asyn = False
    self.in_put_cmd = False
    #open serial connection at a given port
    self.relay = serial.Serial(port, baudrate = 9600, bytesize=8, parity = 'N', stopbits = 1,
    timeout = None, xonxoff = False, rtscts = False, dsrdtr = False)
    self.outterm = "\r\n"
  #_____________________________________________________________________________
  def put_cmd(self, cmd=""):
    #asynchronous command
    if cmd != "": self.queue.append(cmd)
    #only one instance since now
    if self.in_put_cmd == True: return
    #lock the instance
    self.in_put_cmd = True
    #wait for synchronous command to finish
    while self.busy == True: time.sleep(0.1)
    #process the command queue
    while len(self.queue) > 0:
      #skip if synchronous command was issued
      if self.busy == True:
        break
      #raise asyn busy flag
      self.asyn = True
      self.run_cmd(self.queue.pop(0))
      self.asyn = False
    #unlock the instance
    self.in_put_cmd = False
  #_____________________________________________________________________________
  def put_cmd_sync(self, cmd):
    #synchronous command, expected to run at regular intervals
    self.busy = True
    #wait for asynchronous command in proggress
    while self.asyn == True: time.sleep(0.1)
    #process the command, capture the response
    resp = self.run_cmd(cmd)
    #print resp
    self.busy = False
    #finish any asynchronous commands
    self.put_cmd()
    return resp
  #_____________________________________________________________________________
  def run_cmd(self, cmd):
    #insert the command
    try:
      cmd += self.outterm
      for char in cmd:
        self.relay.write( char )
        self.relay.read()
      #get response of the command
      resp = ""
      char = ""
      #response loop
      while char != ">":
        #read character from serial line
        char = self.relay.read()
        #append the character to response string
        resp += char
        #return the response
      return resp
    except:
      print "Error with cmd occured"
      return ""
