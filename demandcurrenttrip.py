from softioc import builder

class demandcurrenttrip:
  def __init__(self,boardList,relay):
    self.relay = relay
    self.boardList = boardList
    self.bdbegin = 0
    self.bdend = 15
    self.cnbegin = 0
    self.cnend = 15
    #these pvs were created because the user can pick from a range of boards and channels to
    #change their limits
    self.boardbegin = builder.longOut("CBbegin", initial_value = self.bdbegin)
    self.boardend = builder.longOut("CBend", initial_value = self.bdend)
    self.chanbegin = builder.longOut("CCbegin", initial_value = self.cnbegin)
    self.chanend = builder.longOut("CCend", initial_value = self.cnend)
    #this pv holds the new value for the limit
    self.tripval = builder.aOut("current_tripval", initial_value = 10)
    #this pv will be a button that the user can press to confirm their changes
    self.setlimit = builder.boolOut("setcurrenttrip", ZNAM = 0, ONAM = 1, HIGH = 0.1, on_update = self.set_limits)

  def set_limits(self,val):
    #in order to get the range of boards and channels, we must hold them at new values
    #objects cannot be converted to string, so a new value holds the number from the function called
    #from the object
    if val == 0:
      return
    value = self.tripval.get()
    startingboard = self.boardbegin.get()
    startingchannel = self.chanbegin.get()
    endingboard = self.boardend.get()
    endingchannel = self.chanend.get()
    boarddif = (endingboard - startingboard) + 1
    chandif = (endingchannel - startingchannel) + 1
    for i in range(boarddif):
      for j in range(chandif):
        boards = startingboard + i
        channels = startingchannel + j
        command = "set current trip ({0:d},{1:d}) {2:.0f}".format(boards,channels,value)
        #print command
        self.relay.put_cmd(command)

