import tkinter as tk
import numpy as np;

def hex_to_rgb( hex ):
  '''
  Converts hex to 3 element rgb values:
    Ex. #FFFFFF -> [255,255,255]
  '''
  return [ int(hex[i:i+2], 16) for i in range(1, len(hex), 2) ]

def rgb_to_hex( r, g = None, b = None ):
  '''
  Converts 3 element rgb values to hex:
    Ex. [255,255,255] -> #FFFFFF
  '''
  rgb = r if g is None and b is None else [r, g, b]          # Assumine first input is all values
  rgb = np.clip(rgb, 0, 255).astype( np.uint8 );
  hex = ['{:02x}'.format(i) for i in rgb]
  return '#{}'.format( ''.join( hex ) );
    
def colorGradient( start, end, ncolors, hex=True ):
  if type(start) is str: start = hex_to_rgb( start );                           # Convert start point to RGB if hex
  if type(end)   is str: end   = hex_to_rgb( end   );                           # Convert end   point to RGB if hex
  r = np.linspace( start[0], end[0], ncolors, dtype = np.uint8 );               # Interpolate red values
  g = np.linspace( start[1], end[1], ncolors, dtype = np.uint8 );               # Interpolate green values
  b = np.linspace( start[2], end[2], ncolors, dtype = np.uint8 );               # Interpolate blue values
  colors = [None] * ncolors;
  if hex:
    for i in range( ncolors ):
      colors[i] = rgb_to_hex( r[i], g[i], b[i] );
  return colors;

            
class loadingIconCanvas( tk.Canvas ):
  def __init__(self, parent, width = 16, height = 16, **kwargs):
    tk.Canvas.__init__(self, parent, width=width, height=height, **kwargs)
    self.dot     =  0;                                                          # Current dot index number
    self.ndots   = 12;                                                          # Number of dots in the loading icon
    self.dots    = [];                                                          # List to store all dot objects
    self.dt      = round( 5.0e2 / self.ndots);                                  # Rate at which the dots 'spin', in milliseconds
    self.colors  = colorGradient( [150]*3, self['background'], self.ndots );    # Gradient for dots
    self.afterID = None;                                                        # Handel to the after method call
    ang = np.linspace(0, 2*np.pi, self.ndots, False) - np.pi/2.0;               # Generate list of angles (in radians) ranging form -pi/2 and going clockwise to almost -pi/2
    r1  = width / 3;                                                            # Set radius for main circle that small circles follow
    r2  = r1    / 4;                                                            # Set radius of smaller circles
    x   = r1 * np.cos( ang ) + width  / 2.0;                                    # Compute x values for points along the larger circle
    y   = r1 * np.sin( ang ) + height / 2.0;                                    # Compute y values for points along the larger circle

    for i in range(self.ndots):                                                 # Iterate over the number of dots
      coord = (x[i]-r2, y[i]+r2, x[i]+r2, y[i]-r2,);                            # Define the coordinates for the ith small circle
      self.dots.append( 
        self.create_oval(coord, fill = self['background'], width = 0 ) 
      );                                                                        # Create a circle on the canvas with a color that matches the background with no border line
  ##############################################################################
  def startLoad(self):    
    '''
    Method for making dots spin
    '''
    for i in range(self.ndots):                                                 # Iterate over all the dots
      id = (self.dot + i) % self.ndots;                                         # Set index for dot by using i to offset the self.dot index, ensuring is not larger than self.ndots
      self.itemconfig( self.dots[id], fill = self.colors[i] );                  # Change the color for the dot at id to be the color[i]
    self.dot = (self.dot + 1) % self.ndots;                                     # Increment the dot number, ensuring it is not larger than self.ndots
    self.afterID = self.after(self.dt, self.startLoad);                         # Call the after method so that the dots keep spinning
  ##############################################################################
  def stopLoad(self):
    '''
    Method to disappear the dots; i.e., stop them spinning
    '''
    if self.afterID is not None:                                                # If the afterID is NOT None
      self.after_cancel( self.afterID );                                        # Cancel the after_cancel method
      self.afterID = None;                                                      # Set the afterID attribute to None
      self.dot     = 0;                                                         # Reset dot to zero; loading starts with darkest circle at top ALWAYS
      for i in range(self.ndots):                                               # Iterate over all the dots
        self.itemconfig( self.dots[i], fill = self['background'] );             # Set the dot color to match the canvas background
