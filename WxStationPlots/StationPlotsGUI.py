import tkinter as tk
from threading import Thread;
import os, time;

from metpy.plots import StationPlotLayout

from .Frames import matplotFrame, optionsFrame;
from .awipsSurfaceObs import awipsSurfaceObs;
from . import sys_data;
      
class StationPlotsGUI( tk.Tk ):
  def __init__(self):
    tk.Tk.__init__(self);                                                       # Initialize the frame superclass
    self.initMenuBar( );
    self.srfObs = awipsSurfaceObs();                                  
    self.stnLayout = StationPlotLayout()
    
    self.plotFrame = matplotFrame( self );
    self.optFrame  = optionsFrame( self );

    self.optFrame.cur_domain.trace('w', self.updateDomain)

    update = tk.Button(self, text = 'Update Stations')
    update.configure( command = lambda : Thread( target = self.updateObs ).start() )
    


    self.optFrame.setDefaults()
    update.grid(         row=0, column = 0, sticky='ew')
    self.optFrame.grid(  row=1, column = 0, sticky='nsew')
    self.plotFrame.grid( row=0, column = 1, sticky='nsew', rowspan = 2);

  ##############################################################################
  def initMenuBar( self ):
    menu = tk.Menu( self );                                                     # Generate a menubar
    menu.add_command(label = 'Station Layout', command = self.stationLayout);   # Add a station layout option to the menu bar and set command to run on click
    self.configure( menu = menu );                                              # Add the menubar to root

  ##############################################################################
  def stationLayout(self, *args):
    self.plotFrame.stationLayout.show()
        
  ##############################################################################
  def updateObs(self, *args):
    self.optFrame.startLoad()
    try:
      obs = self.srfObs.getData(density = 4)
      self.plotFrame.plotStations( obs );
    except Exception as err:
      print( err );
    self.optFrame.stopLoad();
  ##############################################################################
  def updateDomain(self, *args):
    domain = self.optFrame.cur_domain.get();
    self.plotFrame.updateDomain( domain )
#     self.plotFrame.initMap( domain )


  