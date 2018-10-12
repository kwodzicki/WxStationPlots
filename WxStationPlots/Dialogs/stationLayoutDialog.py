#!/usr/bin/env python
import tkinter as tk
from metpy.plots import StationPlotLayout
from ..sys_data import colors, sfcLayout, sfcLookupTable;

varOpts  = [''] + list( sfcLookupTable.keys() );

class stationLayoutDialog( StationPlotLayout ):
  def __init__(self, parent):
    StationPlotLayout.__init__(self);
    self.add_barb('windU', 'windV', units='knots', linewidth=0.5);
    self.parent = parent
#     tk.Toplevel( parent );
#     tk.Frame.__init__(self, self.root);
    
    self.nCol   = 5;
    self.nRow   = 5;
    self.vars   = {};
    self.traces = {};
    self.sCol = -(self.nCol // 2)
    self.sRow = -(self.nRow // 2)
    for i in range(self.sCol, self.sCol + self.nCol):
      for j in range(self.sRow, self.sRow + self.nRow):
        key = self.key(i,j)
        self.vars[ key ] = {
          'name'  : tk.StringVar(),
          'color' : tk.StringVar()
        }
        if key in sfcLayout:
          self.vars[ key ]['name'].set(  sfcLayout[ key ]['name']  )
          self.vars[ key ]['color'].set( sfcLayout[ key ]['color'] )
          self.update_value( key );
# custom_layout.add_value((-1.0,  1.0,), 'air_temp',           fmt='.0f',  units='degF', color='darkred')
# custom_layout.add_value((-1.0, -1.0,), 'dew_temp', fmt='.0f',  units='degF', color='darkgreen')
# custom_layout.add_value(( 1.0,  1.0,),  'precip',   fmt='0.1f', units='inch', color='blue')
# custom_layout.add_value(( 1.0,  1.0,), 'slp',      fmt='0.0f', units='mbar', color='black')

  ##############################################################################
  def key(self, i, j): 
    '''
    A method to generate keys for the vars dictionary. These keys
    are plotting locations in the station plot.
    '''
    return (i,j,);

  ##############################################################################
  def stnLoc2ColRow(self, i, j): 
    '''
    A method to convert the station location (relative to center)
    to column,row values for gridding)
    '''
    return i + (self.nCol//2), (self.nRow//2) - j;
  ##############################################################################
  def show(self):
    root = tk.Toplevel( self.parent );
    canvas = tk.Canvas(root,  width=128, height=128, borderwidth=0)
    canvas.create_oval(16, 16, 112, 112, outline="black", width=6)
    canvas.grid(row = 2, column = 2)

    for i in range(self.sCol, self.sCol + self.nCol):
      for j in range(self.sRow, self.sRow + self.nRow):
        self.addOption( root, i, j );

  ##############################################################################
  def addOption(self, root, i, j):
    if i == 0 and j == 0: return
    frame    = tk.Frame(root);
    key      = self.key(i,j);
    varMenu  = tk.OptionMenu(frame, self.vars[key]['name'],  *varOpts)
    colMenu  = tk.OptionMenu(frame, self.vars[key]['color'], *colors)
    varMenu.configure( width = 10 );
    varMenu.pack(side = 'top', expand = True, fill = 'x')
    colMenu.pack(side = 'top', expand = True, fill = 'x')
    col, row = self.stnLoc2ColRow(i,j)
    frame.grid( column = col, row = row, padx = 16, pady = 16 );
    

  ##############################################################################
  def update_value(self, key, *args): 
    name  = self.vars[key]['name'].get();                                       # Get the value of the name string for the given key
    color = self.vars[key]['color'].get();                                      # Get the value of the color string for the given key
    if name == '':                                                              # If the name string is empty
      if color != '':                                                           # If the color string is NOT empty
        self.vars[key]['color'].set('');                                        # Set the color string to empty; this will cause this method to run again (due to a trace), which is why we check if the color string is empty so we don't fall into an infinite loop
        self.pop( key );                                                        # If the color hasn't been reset, then the plotting symbol hasn't been popped off yet, so pop it off
        return False;                                                           # Return False; i.e., no update occurred
      return True;                                                              # Return True because all information has been removed so we want the plot to update
    elif color == '':                                                           # Else, if the color is NOT set
      self.vars[key]['color'].set( 'Black' );                                   # Set the color to Black; this will trigger this method again through a trace
      return False;                                                             # Return False from the method; because setting the color causes this method to run again through a trace, we don't want to set up the plot while the plot is being updated by the traced call
    info = sfcLookupTable[name]
    if info['symbol'] is None:
      self.add_value( key, info['variable'], 
        color = color, 
        units = info['units'],
        fmt   = info['fmt']
      );                                                                          # Add the value to the station plot
    else:
      self.add_symbol( key, info['variable'], info['symbol'], 
        color = color, 
      );
    return sfcLookupTable[ name ]['variable'];                                  # Return True
if __name__ == "__main__":
  root = tk.Tk()
  inst = stationLayoutDialog( root );
  root.mainloop()
  
