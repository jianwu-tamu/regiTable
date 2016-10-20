import sys
import threading
import time
from Tkinter import *     # for rtTester class

class ResettableTimer(threading.Thread):
  """
  The ResettableTimer class is a timer whose counting loop can be reset
  arbitrarily. Its duration is configurable. Commands can be specified
  for both expiration and update. Its update resolution can also be
  specified. Resettable timer keeps counting until the "run" method
  is explicitly killed with the "kill" method.
  """
  def __init__(self, maxtime, expire, watch_id, inc=None):
    """
    @param maxtime: time in seconds before expiration after resetting
                    in seconds
    @param expire: function called when timer expires
    @param inc: amount by which timer increments before
                updating in seconds, default is maxtime/2
    """
    self.maxtime = maxtime
    self.expire = expire
    self.watch_id = watch_id
    self.started = False
    if inc:
      self.inc = inc
    else:
      self.inc = maxtime/2
    self.counter = 0
    threading.Thread.__init__(self)
    self.setDaemon(True)

  def reset(self):
    """
    Fully rewinds the timer and makes the timer active, such that
    the expire and update commands will be called when appropriate.
    """
    self.counter = 0

  def run(self):
    """
    Run the timer loop.
    """
    self.started = True
    self.counter = 0
    while self.counter < self.maxtime:
        self.counter += self.inc
        time.sleep(self.inc)
    self.expire(self.watch_id)
