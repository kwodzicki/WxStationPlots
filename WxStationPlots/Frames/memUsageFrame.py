import tkinter as tk;
import os, psutil;

process = psutil.Process(os.getpid())

class memUsageFrame( tk.Frame ):
  def __init__(self, parent):
    tk.Frame.__init__(self, parent);
    self.strVar = tk.StringVar();
    tk.Label(self, text='Memory Usage: ').pack(side='left');
    tk.Label(self, textvariable = self.strVar).pack(side='left');
    self.after_id = self.after(2000, self.checkMemory);
  def checkMemory(self):
    mem = '{:4.2f} MB'.format( process.memory_info().rss * 1.0e-6 );
    self.strVar.set( mem );
