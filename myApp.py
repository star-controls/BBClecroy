#example pythonIoc application
from softioc import builder
from boardClass import Board
from BBCdemandClass import BBCdemand
from VPDdemandclass import VPDdemand
from ZDCdemandclass import ZDCdemand
from PPHVdemandclass import PPHVdemand
from leCroy_com import lecroy_com
from demandramprateclass import demandramprate
from watchdog import watchdog
from datetime import datetime
import time
import threading


#port = "/dev/pts/4"
port = "/tmp/ttyV1"

#open serial connection
relay = lecroy_com(port)

Boards = []

#set device name, will be prefix for PV names
builder.SetDeviceName('BBCHV')

#Boards and their channels are created
for i in range (16):
    Boards.append(Board(i,relay))

#The boards created above run through the class as an object
#for these four different demand voltages
BBC_demands = BBCdemand(Boards)
VPD_demands = VPDdemand(Boards)
ZDC_demands = ZDCdemand(Boards)
PPHV_demands = PPHVdemand(Boards)

set_ramprate = demandramprate(Boards)

watch_dog = watchdog(15,Boards)

#make limits is set to False 
makelimits = False

print "Hi from myApp"




#create some PV, this is ai
#example_pv = builder.aIn("this_is_a_test")


#_____________________________________________________________________________
def do_read():
  #function to make some activity after ioc was started
  #print "Hi from do_something"  
  #function that reads through boards and their channels to pick out 
  # voltage and current within string, and then set those values to 
  #their corresponding placement
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

  
  global makelimits
  #makelimits is turned to true when show_limits function (defined within myApp.py) is called.
  #this is included in the do_read function because this is called very second as to be monitored 
  #frequently.
  if makelimits == True:
    #function used in minicom
    showlimits = relay.put_cmd_sync("show limits ("+str(demandlimits.get())+",0-15)").split('\n')
    counter = 0
    for i in range(len(showlimits)):
      #limitvals is a created string that holds what the user sees for demand limits (for each line)
      limitvals = ""
      #in order to reduce the size of each string, spaces and EOS are removed  
      new = showlimits[i].replace("\r","").split(" ")
      #therefore, if the strng is found to be empty, it is skipped over and only valuable characters
      #are appended
      for char in range(len(new)):
        if new[char] == "":
          continue
        limitvals+= new[char]+" "
      if limitvals == "":
        continue
      #each character is then appended to ListofLimits at corresponding counter
      ListofLimits[counter].set(limitvals)
      counter += 1
      #print ListofLimits[i].set(limitvals)
      #print ListofLimits[i].set("test") 
      #another = new.remove(' ')
    #then, makelimits is set to False again so that this part of the program doesn't keep running
    makelimits = False
    
  
  watch_dog.reset()
    
  #for i in range(len(status)):
    #print i, status[i]



def do_runreading():
  #function to read through boards and their channels
  #(with voltage and current) every second
  while True:
    time.sleep(2)
    try:
      do_read()
    except:
      relay.relay.close()
      watch_dog.handler()
      print "Some error has occured" , str(datetime.now())
      try:
        relay.relay.open()
        print "Serial connection was restored" , str(datetime.now())
      except:
        print "No serial connection" , str(datetime.now())
        


def do_startthread():
  #print Boards[13].channels[02].calc_pv.get()##prints out 'None'
  #commands are set at the beginning of the start up
  BBC_demands.reload_dictionary()
  VPD_demands.reload_dictionary()
  BBC_demands.request_change(1)
  VPD_demands.request_change(1)
  BBC_demands.place_voltages(1)
  VPD_demands.turnoff_VPD(1)
  PPHV_demands.turnoff_PPHV(1)
  ZDC_demands.turnoff_ZDCSMD(1)
  ZDC_demands.turnoff_ZDC(1)
  #watchdog is started up
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
  readstatus.set(1)
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
  readstatus.set(0)



#_____________________________________________________________________________________
def show_limits(z):
  if z == 0:
    return
  for i in range(len(ListofLimits)):
    ListofLimits[i].set("")
  #there is a delay of at most 10 seconds after the "Display" button is pressed to inform the user
  #that their request was recieved and something is happening
  ListofLimits[0].set("Reading in Progress")
  global makelimits
  makelimits = True

#a list is created to hold enough PVs to show all the lines that hold the demand limit information
ListofLimits = []
for i in range(25):
  #pv created to show each line of demand limits
  ListofLimits.append(builder.stringIn("limits_line"+str(i)))

#pv created to confirm which board the user wants to look at
demandlimits = builder.longOut("demandlimits")
#pv created to relay the confirmed board the user desires
showlimits = builder.boolOut("showlimits", ZNAM = 0, ONAM = 1, HIGH = 0.1, on_update=show_limits)
#pv created to turn lecroy on
turnon = builder.boolOut("on", ZNAM=0, ONAM = 1, HIGH = 0.1, on_update=on)
#pv created to turn lecroy off
turnoff = builder.boolOut("off", ZNAM = 0, ONAM = 1, HIGH = 0.1,on_update=off)
#pv created to check the status of the lecroy, either on or off
readstatus = builder.boolIn("showstatus",ZNAM = 0, ONAM = 1)


#pvname = '{0:02d}:{1:02d}:'.format(BoardID, chanID)
#placevalues = builder.aOut(pvname+"placevalues",on_update=place_voltages)
#( 1, 8)    -   0    +   1.87
  
