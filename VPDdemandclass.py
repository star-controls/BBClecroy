from softioc import builder, softioc
import pandas

class VPDdemand:
  def __init__(self,boardList):
    self.boardList = boardList
    #pv created to place VPD demand voltages
    self.placevalues = builder.boolOut("VPDplacevalues",ZNAM = 0, ONAM = 1, HIGH = 0.1, on_update=self.place_voltages)
    #pv created to turn VPD voltages to 0   
    self.turnvoltageoff = builder.boolOut("turnoffVPD",ZNAM = 0, ONAM = 1, HIGH = 0.1, on_update=self.turnoff_VPD)
    self.activefile = 1 
    self.dictionary = {}   
    self.chooseFile = builder.longOut("VPD_setting", initial_value = self.activefile , on_update = self.request_change) 
    self.reload = builder.boolOut("reload_VPD", ZNAM = 0, ONAM = 1, HIGH = 0.1, on_update = self.reload_dictionary)
    self.fileInUse = builder.stringIn("VPDfilestatus")
    self.listofstringIns = []
    self.maximum = 10  
    for i in range(self.maximum):
      self.listofstringIns.append(builder.stringIn("VPDfile"+str(i+1)))

    
  def place_voltages(self,x):
    if x == 0:
      return
    #file including the demand voltages
    try:
      f = open(self.dictionary[self.activefile][0],'r') 
    except:
      self.fileInUse.set("File not found")
      return
    #VPD voltages start at board 13 and end at board 15
    BoardID = 13
    chanID = 0
    #the file only contains one number on each line
    #corresponding to demand voltages

    #loop which defines board with their channels and specific voltage        
    for line in f:
      voltage = float(line)
      self.boardList[BoardID].channels[chanID].pv_vset.set(voltage)
      chanID += 1
      if chanID > 15:
        chanID = 0
        BoardID += 1
    #the channels listed in this file below are not used and their
    #alarms need to be overrided
    ff = pandas.read_csv('data/overrideVPD.csv')
    for line in range(len(ff)):
      bd = ff['BoardID'][line]
      ch = ff['chanID'][line]
      self.boardList[bd].channels[ch].calc_high.put(350)
      self.boardList[bd].channels[ch].calc_hihi.put(350)

  def request_change(self,val):
    if val not in self.dictionary:
      print "Number does not correlate to file in dictionary"
      return
    self.activefile = val
    self.fileInUse.set(self.dictionary[val][1])

  #when content of file is changed
  def reload_dictionary(self,y=1):
    if y == 0:
      return 
    self.dictionary.clear()
    for i in range(len(self.listofstringIns)):
      self.listofstringIns[i].set("")
    f = pandas.read_csv('VPDprofile.csv')
    for line in range(len(f)):
      if line >= self.maximum:
        return
      filename = f['filename'][line]
      description = f['description'][line]
      self.dictionary[line+1] = [filename,description]
      self.listofstringIns[line].set(description)

  def turnoff_VPD(self,y):
    if y == 0:
      return
    #voltages are put to zero by the function setToZero() defined in boardClass.py
    self.boardList[13].setToZero()
    self.boardList[14].setToZero()
    self.boardList[15].setToZero()
    #calc limits are reset by function reset_calc_limits() function 
    #defined in boardClass.py
    self.boardList[13].reset_calc_limits()
    self.boardList[14].reset_calc_limits()
    self.boardList[15].reset_calc_limits()

      

