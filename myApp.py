#example pythonIoc application
from softioc import builder
from boardClass import Board
from BBCdemandClass import BBCdemand
from VPDdemandclass import VPDdemand
from ZDCdemandclass import ZDCdemand
from PPHVdemandclass import PPHVdemand
from leCroy_com import lecroy_com
from watchdog import watchdog
import time
import threading


port = "/dev/pts/3"
#port = "/dev/ttyS2"

#open serial connection
relay = lecroy_com(port)

Boards = []

#set device name, will be prefix for PV names
builder.SetDeviceName('BBCHV')

#Boards and their channels are created
for i in range (16):
    Boards.append(Board(i,relay))

#The boards created above run through as an object
#for these four different demand voltages
BBC_demands = BBCdemand(Boards)
VPD_demands = VPDdemand(Boards)
ZDC_demands = ZDCdemand(Boards)
PPHV_demands = PPHVdemand(Boards)

watch_dog = watchdog(10,Boards)

print "Hi from myApp"



#create some PV, this is ai
#example_pv = builder.aIn("this_is_a_test")


#_____________________________________________________________________________
def do_read():
  #function to make some activity after ioc was started
  #print "Hi from do_something"  
  #function that reads through boards and their channels to pick out 
  # voltage and current, and then set those values to their corresponding 
  #placement
  for i in range (16):
    command = "read ({0:d},0-15)".format(i)
    #insert command
    response = relay.put_cmd_sync(command).split('\n')
    #print response
    #print repr(response)
    for j in range(len(response)):
      #for k in range(len(response[j])):
        #print k,response[j][k]
      if len(response[j]) < 4 or response[j].find('>') >= 0:
         continue

      if response[j].find("Channel") >=0:       
         continue

      if len(response[j]) < 13:
        continue
      voltage = float(response[j][23:30])
      
      if response[j][22] == "-":
        voltage = voltage*(-1)
      ichan = int(response[j][6:8])
      Boards[i].channels[ichan].pv_vmon.set((-1)*voltage)

      if len(response[j]) < 34:
        continue
      current = float(response[j][33:40])

      if response[j][31] == "-":
          current = current*(-1)
      Boards[i].channels[ichan].pv_current.set(current)
      response[j] = ""
  status = relay.put_cmd_sync("show status").split('\n')
  if status[7].find("off") >= 0:
    readstatus.set(0)
  if status[7].find("on") >= 0:
    readstatus.set(1)

   
  watch_dog.reset()
    
  #for i in range(len(status)):
    #print i, status[i]

def do_runreading():
  #function to read through boards and their channels
  #(with voltage and current) every second
  while True:
    time.sleep(1)
    do_read()


def do_startthread():
  #print Boards[13].channels[02].calc_pv.get()##prints out 'None'
  BBC_demands.place_voltages(1)
  VPD_demands.turnoff_VPD(1)
  PPHV_demands.turnoff_PPHV(1)
  ZDC_demands.turnoff_ZDCSMD(1)
  ZDC_demands.turnoff_ZDC(1)
  watch_dog.start()
  t = threading.Thread(target=do_runreading)
  t.daemon = True
  t.start()



#__________________________________________________________________________________
def on(x):
  #turns the lecroy on
  if x == 0:
    return
  print "lecroy is on" 
  command = "on"
  relay.put_cmd(command)
  #char = relay.read()
  #while char != '\r':
      #read character from serial line
   #   char = relay.read()
    #  print char
      
   


#__________________________________________________________________________________
def off(x):
  #turns the lecroy off
  if x == 0:
    return
  print "lecroy is off"
  command = "off"
  relay.put_cmd(command)


#_____________________________________________________________________________________


#pv created to turn lecroy on
turnon = builder.boolOut("on", ZNAM=0, ONAM = 1, HIGH = 0.1, on_update=on)
#pv created to turn lecroy off
turnoff = builder.boolOut("off", ZNAM = 0, ONAM = 1, HIGH = 0.1,on_update=off)
#pv created to check the status of the lecroy, either on or off
readstatus = builder.boolIn("showstatus",ZNAM = 0, ONAM = 1)


#pvname = '{0:02d}:{1:02d}:'.format(BoardID, chanID)
#placevalues = builder.aOut(pvname+"placevalues",on_update=place_voltages)
#( 1, 8)    -   0    +   1.87
  
