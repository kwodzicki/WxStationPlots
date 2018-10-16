import tkinter as tk
from .memUsageFrame import memUsageFrame;
from ..Canvas.loadingIconCanvas import loadingIconCanvas
from .. import sys_data;

class optionsFrame( tk.Frame ):
  def __init__(self, parent):
    tk.Frame.__init__(self, parent);
    self.cur_domain  = tk.StringVar();
    self.domainFrame = tk.Frame(self);
    tk.Label(self.domainFrame, text='Domain').pack()
    opts = [tag for tag in sys_data.domains];
    tk.OptionMenu(self.domainFrame, self.cur_domain, *opts).pack()
    self.domainFrame.pack();
    self.memUse  = memUsageFrame(self)
    self.loading = loadingIconCanvas(self.memUse);
    self.loading.pack(side = 'left');
    self.memUse.pack(side='bottom', anchor='w')

  #########################
  def setDefaults(self):
    self.cur_domain.set( 'CONUS' );
  #########################
  def startLoad(self):
    self.loading.startLoad();
  #########################
  def stopLoad(self):
    self.loading.stopLoad();
