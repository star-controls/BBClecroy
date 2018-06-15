#!/usr/bin/python

# simulation of LeCroy 1440 with 1445A controler, boards 0-15, channels 0-15, negative polarity to -3000 V
#
# supported commands:
#
#   read (s,c)
#   read (s,c1-c2)
#   write (s,c) v
#   show status
#   on
#   off
#   set ramp (s,c) v
#   show ramp (s,c)
#   show ramp (s,c1-c2)
#
# log file: lecroyLog.txt, contains all commands issued to simulation with timestamp
#
# demand voltage is set by write command, readback voltage is set from demand
# and increased by 'delt' constant

import serial
import numpy as np
from datetime import datetime
import time
import threading

#name of serial port on the side of lecroy
port = "/dev/pts/7"

outterm="\r\n"

#number of boards and channels
nbd = 16
nch = 16

#arrays holding demand and measured voltages and current (boards 7 and 9)
dem = np.zeros((nbd,nch), dtype=np.float)
vol = np.zeros((nbd,nch), dtype=np.float)
current = np.empty(nch, dtype=np.float)
ramp = np.zeros((nbd,nch), dtype=np.float)

#maximal negative voltage
vmax = -3100

#correction to measured voltage
delt = 0.87

for ibd in range(nbd):
  for ich in range(nch):
    vol[ibd,ich] = dem[ibd,ich] + delt
    ramp[ibd,ich] = 100.;

#voltage on/off
hvOn = False

#initial current
for ich in range(nch):
  current[ich] = 0.812

#log file
logfile = "lecroyLog.txt"
nlog = 0 #num of lines in log file
nmaxlog = 900 #max num of lines before log file reset

#_____________________________________________________________________________
def loopCh():
  #simulates ramp-up and ramp-down, expected to be called every 0.1 sec
  #channels loop
  for ibd in range(nbd):
    for ich in range(nch):
      deltRamp = 0.06*ramp[ibd,ich]
      nomV0 = dem[ibd,ich] + deltRamp
      nomV1 = dem[ibd,ich] - deltRamp
      stepV = ramp[ibd,ich]/10.
      #HV on and ramp-up
      if hvOn == True and vol[ibd,ich] > nomV0:
        vol[ibd,ich] -= stepV
      #HV on and ramp-down
      if hvOn == True and vol[ibd,ich] < nomV1:
        vol[ibd,ich] += stepV
      #HV off, ramp to zero
      if hvOn == False and vol[ibd,ich] < -deltRamp:
        vol[ibd,ich] += stepV
        #channel reached zero
        if abs(vol[ibd,ich]) < 1.1*stepV:
          vol[ibd,ich] = delt
      #HV on and channel reached nominal
      if hvOn == True and abs(vol[ibd,ich] - dem[ibd,ich]) < 1.1*stepV:
        #if ibd == 0 and ich == 0: print "nominal"
        vol[ibd,ich] = dem[ibd,ich] + delt
      #if ibd == 0 and ich == 0:
        #print dem[ibd,ich], vol[ibd,ich]

runtask = True
#_____________________________________________________________________________
def simTask():
  #simulation task
  while runtask:
    loopCh()
    time.sleep(0.1)

#_____________________________________________________________________________
def get_bdch(line, bdch_list):
  #get board and channel number, sets list of board number and then channel
  #number(s)

  lineW = line.split(" ")
  bdch = lineW[1][1:-1].split(",")
  #get board number
  try:
    ibd = int(bdch[0])
  except:
    return False
  #verify board range
  if ibd < 0 or ibd > 15:
    return False
  #put board number to output list
  bdch_list.append(ibd)
  #determine whether to get single channel or range of channels
  if bdch[1].find("-") >= 0:
    ch_ran = bdch[1].split("-")
    try:
      ch_start = int(ch_ran[0])
      ch_end = int(ch_ran[1])
    except:
      return False
  else:
    try:
      ch_start = int(bdch[1])
    except:
      return False
    ch_end = ch_start
  #verify channel range
  if ch_start < 0 or ch_start > 15:
    return False
  if ch_end < 0 or ch_end > 15:
    return False
  #put start and end channel to output list
  bdch_list.append(ch_start)
  bdch_list.append(ch_end)
  return True


#_____________________________________________________________________________
def do_show_ramp(rel, line):

  #read ramp for a given channel
  #returns True when successfully executed

  #discard 'show' word for get_bdch call
  line = line[line.find("ramp"):]

  #get board and channel number
  bdch_list = []
  if get_bdch(line, bdch_list) == False:
    return False
  ibd = bdch_list[0]
  #determine whether to read single channel or range of channels
  if len(bdch_list) == 2:
    ch_start = bdch_list[1]
    ch_end = ch_start
  else:
    ch_start = bdch_list[1]
    ch_end = bdch_list[2]

  #put ramp for all requested channels
  for ich in range(ch_start, ch_end+1):
    read_chan_ramp(rel, ibd, ich)

  return True

#_____________________________________________________________________________
def read_chan_ramp(rel, ibd, ich):

  if (ibd == 7 or ibd == 9) and ich > 7:
    return True

  if ibd == 4 or ibd == 8 or ibd == 10 or ibd == 11:
    return True

  resp = " ({0:2d},{1:2d}) {2:4.0f}".format(ibd, ich, ramp[ibd,ich])

  rel.write(resp+outterm)

  return True

#_____________________________________________________________________________
def do_read(rel, line):

  #read a given channel
  #returns True when successfully executed

  #get board and channel number
  bdch_list = []
  if get_bdch(line, bdch_list) == False:
    return False
  ibd = bdch_list[0]
  #determine whether to read single channel or range of channels
  if len(bdch_list) == 2:
    ch_start = bdch_list[1]
    ch_end = ch_start
  else:
    ch_start = bdch_list[1]
    ch_end = bdch_list[2]

  #form the output to serial relay
  rel.write("   Channel    Demand   Voltage   Current"+outterm)
  #put all requested channels
  for ich in range(ch_start, ch_end+1):
    read_chan(rel, ibd, ich)

  return True

#_____________________________________________________________________________
def read_chan(rel, ibd, ich):

  #get voltages and current from arrays
  try:
    demRead = dem[ibd,ich]
    volRead = vol[ibd,ich]
    curRead = current[ich]
  except:
    return False

  #introduce random noise
  noise = np.random.rand()
  #uniform number -3 to 3
  noise = noise*6.-3.
  volRead += noise

  #put some current for non-zero voltage
  if abs(volRead) > 10:
    curRead = -519.625

  #make sign symbol for voltages and current
  demSign="-"
  volSign="-"
  curSign="-"
  if demRead > 0:
    demSign = "+"
  else:
    demRead=abs(demRead)

  if volRead > 0:
    volSign = "+"
  else:
    volRead=abs(volRead)

  if curRead > 0:
    curSign = "+"
  else:
    curRead=abs(curRead)

  #form the output to serial relay
  #board 4, 8, 10 and 11 are not present
  if ibd == 4 or ibd == 8 or ibd == 10 or ibd == 11:
    resp = "  (%2d,%2d) " % (ibd, ich)

  #boards 7 and 9 have 8 channels 0-7 and give also current
  #demand voltage is to one digit and current to three
  elif ibd == 7 or ibd == 9:
    if ich > 7:
      resp = "  (%2d,%2d) " % (ibd, ich)
    else:
      resp = "  (%2d,%2d)    %1s%6.1f  %1s%7.2f %1s%8.3f" % (ibd, ich, demSign, demRead, volSign, volRead, curSign, curRead)

  else:
    resp = "  (%2d,%2d)    %1s%4.0f    %1s%7.2f" % (ibd, ich, demSign, demRead, volSign, volRead)

  rel.write(resp+outterm)

  return True

#_____________________________________________________________________________
def do_set_ramp(rel, line):

  #set ramp rate for a given channel
  #returns True when successfully executed

  #discard 'set' word for get_bdch call
  line = line[line.find("ramp"):]

  #get board and channel number and ramp rate
  bdch_list = []
  if get_bdch(line, bdch_list) == False:
    return False
  ibd = bdch_list[0]
  ich = bdch_list[1]
  #now proceed to ramp rate
  lineW = line.split(" ")
  try:
    ramp_val = float(lineW[2])
  except:
    return False

  #put ramp rate to array
  try:
    ramp[ibd,ich] = ramp_val
  except:
    return False

  return True

#_____________________________________________________________________________
def do_write(rel, line):

  #write demand voltage to a given channel
  #returns True when successfully executed

  #get board and channel number and demand voltage
  bdch_list = []
  if get_bdch(line, bdch_list) == False:
    return False
  ibd = bdch_list[0]
  ich = bdch_list[1]
  #now proceed to voltage
  lineW = line.split(" ")
  try:
    demvolt = float(lineW[2])
  except:
    return False

  #check the range of demand voltage
  if demvolt > 0 or demvolt < vmax:
    return False

  #put demand voltage to array
  try:
    dem[ibd,ich] = demvolt
  except:
    return False

  return True

#_____________________________________________________________________________
def do_on(rel, line):

  #set voltage on
  rel.write("HV turn on."+outterm)
  global hvOn
  hvOn = True

  return True

#_____________________________________________________________________________
def do_off(rel, line):

  #set voltage off
  global hvOn
  hvOn = False

  return True

#_____________________________________________________________________________
def do_show_status(rel, line):

  #show status of lecroy
  rel.write(outterm)
  rel.write(outterm)
  rel.write("LeCroy 1445A Version 3.09"+outterm)
  rel.write(outterm)
  rel.write("WARNING: Uncalibrated Operation"+outterm)
  rel.write("Cold start on reboot"+outterm)
  if hvOn == True:
    rel.write("The high voltage is currently on."+outterm)
  else:
    rel.write("The high voltage is currently off."+outterm)

  return True

#_____________________________________________________________________________
def cmdread(rel, line):

  #function to decode individual commands
  #returns True when quit from command loop is requested

  logput(line)

  stat = False

  if line.startswith("read ("):
    stat = do_read(rel, line)

  elif line.startswith("write ("):
    stat = do_write(rel, line)

  elif line.startswith("set ramp ("):
    stat = do_set_ramp(rel, line)

  elif line.startswith("show ramp ("):
    stat = do_show_ramp(rel, line)

  elif line == "on":
    stat = do_on(rel, line)

  elif line == "off":
    stat = do_off(rel, line)

  elif line == "show status":
    stat = do_show_status(rel, line)

  elif line == "":
    stat = True

  elif line == "quit":
    rel.write("quit"+outterm)
    return True

  else:
    stat = False

  if stat == False:
    rel.write("Unrecognized Command"+outterm)

  return False


#_____________________________________________________________________________
def cmdloop(rel):

  #function to maintain the command prompt

  prompt=" 0> "

  rel.write(outterm+prompt)

  #text of command, case insensitive
  line=""
  #original characters upper/lower case for backspace
  linePrint=""
  leave = False

  #line loop
  while True:
    #read character from serial line
    char = rel.read()

    #return
    if char == "\r":
      rel.write(outterm)
      leave = cmdread(rel, line)
      if leave == True:
        rel.write(outterm)
        break

      rel.write(outterm+prompt)
      line = ""
      linePrint = ""
      continue

    #backspace
    if char == "\b":
      #flush terminal
      rel.write("\r")
      for i in range(len(prompt+line)):
        rel.write(" ")

      #remove last character of line
      if len(line) > 0:
        line = line[0:-1]
        linePrint = linePrint[0:-1]

      #put line to terminal
      rel.write("\r"+prompt+linePrint)
      continue

    #now accept only standard characters (except delete)
    if ord(char) < 32 or ord(char) > 126:
      continue

    #send character back to terminal
    rel.write(char)
    linePrint += char

    #case insensitivity, transform upper case to lower case
    if ord(char) >= 65 and ord(char) <= 90:
      char = chr( ord(char)+32 )

    #append character to line
    line += char

  #end of line loop

#_____________________________________________________________________________
def logput(msg):

  #put message to log file

  log = open(logfile, "a")
  log.write(str(datetime.now()) + "   " + msg + "\n")

  #reset file if max number of lines was exceeded
  global nlog
  nlog += 1
  if nlog > nmaxlog:
    log.close()
    log = open(logfile, "w")
    log.write(str(datetime.now()) + "   " + msg + "\n")

  log.close()

#_____________________________________________________________________________
if __name__ == '__main__':

  #start the simulation loop
  tid = threading.Thread(target=simTask)
  tid.start()

  #open serial connection
  relay = serial.Serial(port, 9600)

  #loop over commands
  cmdloop(relay)

  #close the connection
  relay.close()

  #stop the simulation loop
  runtask = False

























