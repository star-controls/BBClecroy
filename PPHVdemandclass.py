from softioc import builder
import pandas

class PPHVdemand:

  def __init__(self,boardList):
    self.boardList = boardList
    self.placevalues = builder.boolOut("PPHVplacevalues",ZNAM = 0, ONAM = 1, HIGH = 0.1, on_update=self.place_voltages)
    self.turnvoltageoff = builder.boolOut("turnoffPPHV",ZNAM = 0, ONAM = 1, HIGH = 0.1, on_update=self.turnoff_PPHV)
    self.indicator = builder.boolIn("indicator", ZNAM = 0, ONAM = 1)
    #boolIN put zero when off put one when on

  def place_voltages(self,x):
    if x == 0:
      return
    #comma seperated value file formating allows us to define board and their 
    #channels with each corresponding demand voltage
    f = pandas.read_csv('data/PPHVvalues.csv')
    for line in range(len(f)):
      BoardID = f['BoardID'][line]
      chanID = f['chanID'][line]
      voltage = f['voltage'][line]
      #assigns each demand voltage to the correct channel
      self.boardList[BoardID].channels[chanID].pv_vset.set(voltage)
    self.indicator.set(1)
    
  def turnoff_PPHV(self,y):
    if y == 0:
      return
    #setToZero function is called, defined in boardClass.py
    self.boardList[5].setToZero()
    self.indicator.set(0)

    
    
   
    
