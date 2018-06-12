from softioc import builder

class demandramprate:
  def __init__(self, boardList):
    self.boardList = boardList
    self.ramprate = builder.aOut("placeramprate",on_update=self.set_ramp, initial_value=100)  
 
  def set_ramp(self, val):
    for i in range(len(self.boardList)):
      for j in range(len(self.boardList[i].channels)):
        self.boardList[i].channels[j].ramprate.set(val)
        
    
    
