#Loading demand voltages for BBC 

from softioc import builder
import pandas

class BBCdemand:
  def __init__(self,boardList):
    self.boardList = boardList
    #create pv to place BBC voltages 
    self.placevalues = builder.boolOut("BBCplacevalues",ZNAM = 0, ONAM = 1, HIGH = 0.1, on_update=self.place_voltages)
    self.diction_ary = {}
    self.activefile = 1
    self.chooseFile = builder.longOut("BBC_setting", initial_value = self.activefile , on_update = self.request_change)
    self.reload = builder.boolOut("reload_BBC", ZNAM = 0, ONAM = 1, HIGH = 0.1, on_update = self.reload_dictionary)   
    self.fileInUse = builder.stringIn("BBCfilestatus") 
    self.turnoffBBC = builder.boolOut("BBCturnoff",ZNAM = 0, ONAM = 1, HIGH = 0.1, on_update = self.turnoff_BBC)  
    self.listofstringIns = []
    self.maximum = 10
    for i in range(self.maximum):
      self.listofstringIns.append(builder.stringIn("BBCfile"+str(i+1)))

  def place_voltages(self,x):
    #function called to place voltages
    if x == 0:
      return
    #file including the demand voltages
    try:
      f = open(self.diction_ary[self.activefile][0],'r') 
    except:
      self.fileInUse.set("File not found")
      return
    #loop which defines board with their channels and specific voltage
    for line in f:
      linelist= line.split()
      BoardID = int(linelist[0][1:-1])
      chanID =  int(linelist[1][:-1])
      voltage = float(linelist[2])
      self.boardList[BoardID].channels[chanID].pv_vset.set(voltage)
    
  def request_change(self,val):
    if val not in self.diction_ary:
      print "Number does not correlate to file in dictionary"
      return
    self.activefile = val
    self.fileInUse.set(self.diction_ary[val][1])
  
  #when content of file is changed
  def reload_dictionary(self,y=1):
    if y ==  0:
      return
    self.diction_ary.clear()
    for i in range(len(self.listofstringIns)):
      self.listofstringIns[i].set("")
    f = pandas.read_csv('BBCprofile.csv')
    for line in range(len(f)):
      if line >= self.maximum:
        return
      file_name = f['filename'][line]
      description = f['description'][line]
      self.diction_ary[line+1] = [file_name,description]
      self.listofstringIns[line].set(description)
             
  def turnoff_BBC(self,z):
    if z == 0:
      return
    self.boardList[0].setToZero()
    self.boardList[1].setToZero()
    self.boardList[2].setToZero()
    self.boardList[3].setToZero()

