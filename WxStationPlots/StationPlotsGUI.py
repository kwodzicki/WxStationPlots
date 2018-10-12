import tkinter as tk
from threading import Thread;
import os, psutil, time;

from metpy.plots import StationPlotLayout

from .Frames.matplotFrame import matplotFrame
from .awipsSurfaceObs import awipsSurfaceObs;
from . import sys_data;

process = psutil.Process(os.getpid())

class memUsage( tk.Frame ):
  def __init__(self, parent):
    tk.Frame.__init__(self, parent);
    self.strVar = tk.StringVar();
    tk.Label(self, text='Memory Usage: ').pack(side='left');
    tk.Label(self, textvariable = self.strVar).pack(side='left');
    self.thread = Thread(target = self.checkMemory, daemon = True);
  def checkMemory(self):
    mem = '{:4.2f} MB'.format( process.memory_info().rss * 1.0e-6 );
    self.strVar.set( mem );
    time.sleep(2.0)
    
class optionsFrame( tk.Frame ):
  def __init__(self, parent):
    tk.Frame.__init__(self, parent);
    self.cur_domain  = tk.StringVar();
    self.domainFrame = tk.Frame(self);
    tk.Label(self.domainFrame, text='Domain').pack()
    opts = [tag for tag in sys_data.domains];
    tk.OptionMenu(self.domainFrame, self.cur_domain, *opts).pack()
    self.domainFrame.pack();
    memUsage(self).pack(side='bottom')


  #########################
  def setDefaults(self):
    self.cur_domain.set( 'CONUS' );
  

class StationPlotsGUI( tk.Tk ):
  def __init__(self):
    tk.Tk.__init__(self);                                                       # Initialize the frame superclass
    self.initMenuBar( );
    self.srfObs = awipsSurfaceObs();                                  
    self.stnLayout = StationPlotLayout()
    
    self.plotFrame = matplotFrame( self );
    self.optFrame  = optionsFrame( self );

    self.optFrame.cur_domain.trace('w', self.updateDomain)

    update = tk.Button(self, text = 'Update Stations', command=self.updateObs)
    


    self.optFrame.setDefaults()
    update.grid(         row=0, column = 0, sticky='ew')
    self.optFrame.grid(  row=1, column = 0, sticky='nsew')
    self.plotFrame.grid( row=0, column = 1, sticky='nsew', rowspan = 2);

  def initMenuBar( self ):
    menu = tk.Menu( self );                                                     # Generate a menubar
    menu.add_command(label = 'Station Layout', command = self.stationLayout);   # Add a station layout option to the menu bar and set command to run on click
    self.configure( menu = menu );                                              # Add the menubar to root

  def stationLayout(self, *args):
    self.plotFrame.stationLayout.show()
        
  def updateObs(self, *args):
    obs = self.srfObs.getData(density = 4)
    self.plotFrame.plotStations( obs );
#     def sub():
#       obs = self.srfObs.getData(density = 2)
#       self.plotFrame.plotStations( obs );
#     Thread(target = sub).start()
  def updateDomain(self, *args):
    domain = self.optFrame.cur_domain.get();
    self.plotFrame.updateDomain( domain )
#     self.plotFrame.initMap( domain )


  