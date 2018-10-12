import tkinter as tk
import numpy as np

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

import matplotlib.backends.backend_tkagg as tkagg
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from metpy.plots import StationPlot;

from ..Dialogs.stationLayoutDialog import stationLayoutDialog
from ..sys_data import domains
# import data;

from ..LambertConformalTicks import LambertConformalTicks;
class matplotFrame( tk.Frame ):
  def __init__(self, parent, width = 300, height = 200):
    tk.Frame.__init__(self, parent);
    self.stationLayout = stationLayoutDialog( self );
    self.setTraces();
    
    self.stnPlots = None;
    self.figure   = None;
    self.axes     = None;
    self.proj     = None;
    self.canvas   = None;
    self.obs      = None;
    self.xticks   = [x for x in range(-180, 180, 15)]
    self.yticks   = [y for y in range( -90,  90, 10)]
   
    self.PlateCarree = ccrs.PlateCarree()
    self.initMap()

  ##############################################################################
  def setTraces(self):
    for key, val in self.stationLayout.vars.items():
      val['name'].trace( 'w', lambda a,b,c,key=key: self.updateStations( key ));
      val['color'].trace('w', lambda a,b,c,key=key: self.updateStations( key ));

  ##############################################################################
  def initMap(self):
    if self.canvas is not None: 
      plt.close();
      self.canvas.get_tk_widget().destroy();

    self.figure = plt.figure( figsize=(8, 5) )
    self.canvas = FigureCanvasTkAgg( self.figure, self );
    
#     cent_lon = (domains[domain]['limits'][0] + domains[domain]['limits'][1])/2.0
#     cent_lat = (domains[domain]['limits'][2] + domains[domain]['limits'][3])/2.0
#     self.proj   = ccrs.LambertConformal(central_longitude=cent_lon, 
#                                    central_latitude=cent_lat,
#                                    standard_parallels=[35])
#     self.axes.coastlines( resolution = domains[domain]['res'], linewidth = 0.5 );
#     self.axes.add_feature( cfeature.BORDERS.with_scale(domains[domain]['res']), linewidth = 0.5 );
#     self.axes.add_feature( cfeature.STATES.with_scale( domains[domain]['res']), linewidth = 0.5 );
#     self.axes.set_extent( domains[domain]['limits'], crs = self.PlateCarree )

    self.proj   = ccrs.LambertConformal( standard_parallels=[35] )
    self.axes   = self.figure.add_subplot(1, 1, 1, projection = self.proj)
    plt.subplots_adjust(left = 0.05, bottom = 0.05, right = 0.95, top = 0.95);
    self.axes.coastlines( resolution ='50m', linewidth = 0.5 );
    self.axes.add_feature( cfeature.BORDERS.with_scale( '50m' ), linewidth = 0.5 );
    self.axes.add_feature( cfeature.STATES.with_scale(  '50m' ), linewidth = 0.5 );

    gl = self.axes.gridlines(xlocs = self.xticks, ylocs = self.yticks, linestyle='--', linewidth=0.5)
#     LambertConformalTicks(self.axes, xticks, yticks)    
    self.canvas.get_tk_widget().pack();
    if self.obs is not None:
      self.plotStations( self.obs );

  ##############################################################################
  def updateDomain(self, domain):
    self.axes.set_extent( domains[domain]['limits'], crs = self.PlateCarree )
    self.canvas.draw();

  ##############################################################################
  def updateStations(self, key):
    varName = self.stationLayout.update_value( key );                           # Update the variable in the station Layout
    if varName is False: return;                                                # If returns False, that means the item has not been fully removed yet so just return
    print( 'Updating station layout' );
    key = tuple( [i * 10 for i in key] );                                       # Update the key based on the size of the symbols
    if key in self.stnPlots.items:                                              # If the key is in the stnPlots.items attributes
      print( 'Found key!' )
      self.stnPlots.items.pop( key ).remove();                                  # Pop off the item from the list and remove it from the plot
    if varName is not True:                                                     # If varName is NOT True; then it must be as string representing a variable that must be added to the plot
      print(varName, varName in self.obs)
      
      self.stationLayout.plot( self.stnPlots, {varName : self.obs[varName]} );  # Pass just the new variable to plot to the stationLayout.plot method
    print( 'Drawing' )
    self.canvas.draw();                                                         # Update the plot
  ##############################################################################
  def plotStations(self, obs):
    self.obs = obs
    print( 'setting station plot')
    self.stnPlots = StationPlot(
      self.axes, self.obs['longitude'], self.obs['latitude'], clip_on = True,
      transform = self.PlateCarree)
    print( 'plotting')
    self.stationLayout.plot( self.stnPlots, self.obs );
    self.canvas.draw()
    print( 'Done plotting')

#     stationplot = StationPlot(ax, data['longitude'], data['latitude'], clip_on=True,
#                               transform=ccrs.PlateCarree(), fontsize=10)
#     stationplot.plot_text((2, 0), data['stid'])
#     custom_layout.plot(stationplot, data)


    