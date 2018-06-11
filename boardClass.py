#this is a class that identifies the 16 boards, each having 16 channels
#when a function is called, have it say its baord ID


from chan import Channels
    
class Board:
    
  def __init__(self, ID, relay):
    #list of channels is created
    self.channels = []
    self.ID = ID
    #print "Hi, I am board",self.ID
    for i in range (16):
      self.channels.append(Channels(i,self.ID,relay))
  
  def setToZero(self):
    for i in range(len(self.channels)):
      #using the PV 'pv_vset', voltages can be set to zero, defined in chan.py
      self.channels[i].pv_vset.set(0)

  def reset_calc_limits(self):
    for i in range(len(self.channels)):
      #using the function reset_calc_limits (defined in chan.py) to put the calc
      #limits back to normal
      self.channels[i].reset_calc_limits()
