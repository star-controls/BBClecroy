#Loading demand voltages for BBC 

from softioc import builder

class BBCdemand:
  def __init__(self,boardList):
    self.boardList = boardList
    #create pv to place BBC voltages 
    self.placevalues = builder.boolOut("BBCplacevalues",ZNAM = 0, ONAM = 1, HIGH = 0.1, on_update=self.place_voltages)
   
  #function called to place voltages
  def place_voltages(self,x):
    if x == 0:
      return
    #file including the demand voltages
    f = open('data/demand_fixed_highgain_polB_20180419.bbc','r')
    #loop which defines board with their channels and specific voltage
    for line in f:
      linelist= line.split()
      BoardID = int(linelist[0][1:-1])
      chanID =  int(linelist[1][:-1])
      voltage = float(linelist[2])
      self.boardList[BoardID].channels[chanID].pv_vset.set(voltage)
    
 
