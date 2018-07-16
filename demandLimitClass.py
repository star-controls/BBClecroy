from softioc import builder

class demandlimit:
  def __init__(self,boardList):
  self.boardList = boardList
  self.boardnumber = 0
  self.channelnumber = 0
  self.initialLimit = 100
  self.callboards = builder.longOut("Boardlimit", initial_value = self.boardnumber)
  self.callchannels = builder.longOut("chanlimit", intitial_value = self.channelnumber)
  #WRONGself.confirmcommand = builder.boolOut("limitconfirm", ZNAM = 0, ONAM = 1, HIGH = 0.1, on_update = self.confirm_limits)
  self.setlimit = builder.aOut("setlimit", on_update = self.set_limits, initial_value = self.initialLimit)
 
  def confirm_limits(self,board,channel):
    

  def set_limits(self,val):
    self.boardList[self.boardnumer].channels[self.channelnumber].setlimit.set(val)
 

"""
  for i in range(len(self.boardList)):
      for j in range(len(self.boardList[i].channels)):
        self.boardList[i].channels[j].setlimit.set(val)
"""
