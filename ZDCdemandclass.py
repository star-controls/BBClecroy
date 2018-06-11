from softioc import builder
import pandas

class ZDCdemand:
  def __init__(self,boardList):
    self.boardList = boardList
    #PVs are created to carry out the functions defined below
    self.placevalues = builder.boolOut("ZDCplacevalues",ZNAM = 0, ONAM = 1, HIGH = 0.1, on_update=self.place_voltages)
    self.turnvoltageoff = builder.boolOut("turnoffZDC",ZNAM = 0, ONAM = 1, HIGH = 0.1, on_update=self.turnoff_ZDC)
    self.placevalues_ZDCSMD = builder.boolOut("ZDCSMDplacevalues",ZNAM = 0, ONAM = 1, HIGH = 0.1, on_update=self.place_voltages_ZDCSMD)
    self.turnSDMoff = builder.boolOut("turnoffSMD",ZNAM = 0,ONAM = 1, HIGH= 0.1, on_update=self.turnoff_ZDCSMD)

  def place_voltages(self,x):
    if x == 0:
      return
    #file is read as a comma seperated value file so that boards and their 
    #channels have a corresponding voltage 
    ff = pandas.read_csv('data/newfileZDC.csv')
    for line in range(len(ff)):
      BoardID = ff['BoardID'][line]
      chanID = ff['chanID'][line]
      voltage = ff['voltage'][line]
      #this sets the voltages to the right channel
      self.boardList[BoardID].channels[chanID].pv_vset.set(voltage)
  
  def place_voltages_ZDCSMD(self, x):
    if x == 0:
      return
    #same concept as last function, yet these values are for other channels
    f = pandas.read_csv('data/newvaluesZDC.csv')
    for line in range(len(f)):
      BoardID = f['BoardID'][line]
      chanID = f['chanID'][line]
      voltage = f['voltage'][line]
      #sets the voltages to the right channel
      self.boardList[BoardID].channels[chanID].pv_vset.set(voltage)
    
  def turnoff_ZDC(self,y):
    if y == 0:
      return
    #sets the right boards to zero voltage by calling setToZero function
    #defined in boardClass.py
    self.boardList[7].setToZero()
    self.boardList[9].setToZero()

  def turnoff_ZDCSMD(self,y):
    if y == 0:
      return
    #seperate function to turn ZDCSMD voltages to zero
    self.boardList[6].setToZero()
    
