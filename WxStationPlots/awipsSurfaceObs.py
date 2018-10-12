from awips.dataaccess import DataAccessLayer as DAL;
from dynamicserialize.dstypes.com.raytheon.uf.common.time import TimeRange;
from metpy.calc import reduce_point_density, wind_components;
from metpy.plots import wx_code_map;

from datetime import datetime, timedelta;
import numpy as np

# from WxStationPlots import sys_data;
from . import sys_data;

def get_cloud_cover(code):
  if code is None:
    return 0;
  elif 'OVC' in code:
    return 1;
  elif 'BKN' in code:
    return 6;
  elif 'SCT' in code:
    return 4;
  elif 'FEW' in code:
    return 2;
  else:
    return 0;
    
class awipsSurfaceObs( object ):
  def __init__(self, server = "edex-cloud.unidata.ucar.edu"):
    DAL.changeEDEXHost( server );
    self.request = DAL.newDataRequest( "obs" )
    self.__vars  = DAL.getAvailableParameters(    self.request );
    self.__stids = DAL.getAvailableLocationNames( self.request );
    
    self.vars    = None;
    self.stids   = None;
  ##############################################################################
  def setDensity(self, density):
    self.setVariables( ['longitude', 'latitude', 'stationName', 'timeObs'] );
    timerange = self.setTime();
    res   = DAL.getGeometryData( self.request, timerange );
    pnts  = [];
    stids = [];
    for i in range( len(res) ):
      if res[i].getString( 'stationName' ) not in stids:
        stids.append( (res[i].getString( 'stationName' ), res[i].get )
        pnts.append( 
          (res[i].getNumber('longitude'), res[i].getNumber('latitude'), 0, )
        );
    filter = reduce_point_density( np.asarray(pnts), density)
    stids  = np.asarray(stids)[ filter ];
    return list( stids ); 
    
  ##############################################################################
  def setStations(self, stations = None):
    self.stids = self.__stids if stations is None else stations;
    self.request.setLocationNames( *self.stids );
#     if stations is None:
#       self.request.setLocationNames( *self.__stids );
#       return self.__stids
#     else:
#       self.request.setLocationNames( *stations );
#       return stations
  ##############################################################################
  def setVariables(self, variables = sys_data.varNames):
    self.vars = self.__vars if variables is None else variables;
    self.request.setParameters( *self.vars )
#     if variables is None:
#       self.request.setParameters( *self.__vars )
#       return self.__vars;
#     else:
#       self.request.setParameters( *variables )
#       return variables;
  ##############################################################################
  def setTime(self):
    lastHour = datetime.utcnow() - timedelta(hours = 1)
    start    = lastHour.strftime( "%Y-%m-%d %H" );
    sRange   = datetime.strptime( "{}:00:00".format(start), "%Y-%m-%d %H:%M:%S")
    eRange   = datetime.strptime( "{}:59:59".format(start), "%Y-%m-%d %H:%M:%S")
    return TimeRange(sRange, eRange);
  ##############################################################################
  def reduceDensity(self, density):
    self.setVariables( ['longitude', 'latitude', 'stationName'] );
    timerange = self.setTime();
    res   = DAL.getGeometryData( self.request, timerange );
    pnts  = [];
    stids = [];
    for i in range( len(res) ):
      if res[i].getString( 'stationName' ) not in stids:
        stids.append( res[i].getString( 'stationName' ) )
        pnts.append( 
          (res[i].getNumber('longitude'), res[i].getNumber('latitude'), 0, )
        );
    filter = reduce_point_density( np.asarray(pnts), density)
    stids  = np.asarray(stids)[ filter ];
    return list( stids ); 
  ##############################################################################
  def getData(self, stations = None, variables = sys_data.varNames, density = None):
    stids = self.setStations( stations );
    if density is not None:
      stids = self.reduceDensity( density );
      stids = self.setStations( stids );
    vars  = self.setVariables( variables );
    timerange = self.setTime();

    obs = dict( {var: [] for var in vars} )
    res = DAL.getGeometryData( self.request, timerange );
    
    station_names  = [];
    pres_weather   = [];
    sky_cov        = [];
    sky_layer_base = [];
    for ob in res:                                                              # Iterate over all objects in the response
      avail_params = ob.getParameters();                                        # Get the parameters in the response
      if "presWeather" in avail_params:                                         # If presWeather is in the avail_parameters
        pres_weather.append( ob.getString("presWeather") );                     # Append the present weather value to the pres_weather list
      elif "skyCover" in avail_params and "skyLayerBase" in avail_params:       # Else if skyCover and skyLayerBase are in the available parameters
        sky_cov.append( ob.getString("skyCover") );                             # Append the skyCover the sky_cov list
        sky_layer_base.append( ob.getNumber("skyLayerBase") );                  # Append the skyLayerBase ot the sky_layer_base list
      else:                                                                     # Else
        if ob.getString('stationName') not in station_names:                    # If the name of the station is NOT in the station_name list
          station_names.append( ob.getString('stationName') );                  # Append the station name to the station_names list
          for var in vars:                                                      # Iterate over all the products
            if var not in avail_params:                                        # If product is not in list of available products
              obs[var].append( None );                                         # Append None to the list under the product key in the obs dictionary
            elif var not in sys_data.multi_value_vars:                             # If product NOT in multi_value_vars list
              if var == 'timeObs':                                             # If the product is timeObs
                date = datetime.fromtimestamp( ob.getNumber(var)/1000.0 );     # Get the time and convert to datetime object
                obs[var].append( date );                                       # Append the date to the list under the prod key in the obs dictionary
              else:                                                             # Else
                try:                                                            # Try to 
                  obs[var].append( ob.getNumber(var) );                       # Get number for the given product and append the to list under the prod key the obs dictionary
                except TypeError:                                               # On exception
                  obs[var].append( ob.getString(var) );                       # Get string for the given product and append the to list under the prod key the obs dictionary

          obs['presWeather'].append(pres_weather);
          obs['skyCover'].append(sky_cov);
          obs['skyLayerBase'].append(sky_layer_base);
          pres_weather   = [];
          sky_cov        = [];
          sky_layer_base = [];
        
    for tag in obs:
      if tag in sys_data.varUnits:
        obs[tag] = np.array( obs[tag] );
#         if tag == 'windDir': 
#           obs[tag][ obs[tag] == -9999.0 ] = 'nan';
        if obs[tag].dtype.type is np.float64:
          obs[tag][ obs[tag] == -9999.0 ] = 'nan';
        elif tag == 'pressChangeChar':
          obs[tag] = [ int(i) if i.isdigit() else -1 for i in obs[tag] ];       # Convert all the string intergers to integers and replace any empty strings with -1
        if sys_data.varUnits[tag] is not None:
          obs[tag] = obs[tag] * sys_data.varUnits[tag];
    if 'presWeather' in obs:
      weather = []
      for wx in obs['presWeather']:
        key = '';
        if wx is not None:
          if type(wx) is list:
            key = wx[0]
          elif ' ' in wx:
            key = wx.split()[0]
          elif type(wx) is str:
            key = wx;          
        try:
          weather.append( wx_code_map[ key ] );
        except:
          weather.append( wx_code_map[ '' ] );
      obs['presWeather'] = weather
#         print( type(wx), wx)
#       weather = [ '' if s is None else s.split()[0] for s in obs['presWeather'] ]
    if 'skyCover' in obs:
      obs['skyCover'] = [get_cloud_cover(x) for x in obs['skyCover']]
    if 'windDir' in obs and 'windSpeed' in obs:
      u, v = wind_components(obs['windSpeed'], obs['windDir'])
      obs['windU'] = u;
      obs['windV'] = v;
    return obs
  ##############################################################################
  def getRawData(self, stations = None, variables = sys_data.varNames, density = None):
    stids = self.setStations( stations );
    if density is not None:
      stids = self.reduceDensity( density );
      stids = self.setStations( stids );
    vars  = self.setVariables( variables );
    timerange = self.setTime();

    obs = dict( {var: [] for var in vars} )
    res = DAL.getGeometryData( self.request, timerange );
    
    station_names  = [];
    pres_weather   = [];
    sky_cov        = [];
    sky_layer_base = [];
    for ob in res:                                                              # Iterate over all objects in the response
      avail_params = ob.getParameters();                                        # Get the parameters in the response
      if "presWeather" in avail_params:                                         # If presWeather is in the avail_parameters
        pres_weather.append( ob.getString("presWeather") );                     # Append the present weather value to the pres_weather list
      elif "skyCover" in avail_params and "skyLayerBase" in avail_params:       # Else if skyCover and skyLayerBase are in the available parameters
        sky_cov.append( ob.getString("skyCover") );                             # Append the skyCover the sky_cov list
        sky_layer_base.append( ob.getNumber("skyLayerBase") );                  # Append the skyLayerBase ot the sky_layer_base list
      else:                                                                     # Else
        if ob.getString('stationName') not in station_names:                    # If the name of the station is NOT in the station_name list
          station_names.append( ob.getString('stationName') );                  # Append the station name to the station_names list
          for var in vars:                                                      # Iterate over all the products
            if var not in avail_params:                                        # If product is not in list of available products
              obs[var].append( None );                                         # Append None to the list under the product key in the obs dictionary
            elif var not in sys_data.multi_value_vars:                             # If product NOT in multi_value_vars list
              if var == 'timeObs':                                             # If the product is timeObs
                date = datetime.fromtimestamp( ob.getNumber(var)/1000.0 );     # Get the time and convert to datetime object
                obs[var].append( date );                                       # Append the date to the list under the prod key in the obs dictionary
              else:                                                             # Else
                try:                                                            # Try to 
                  obs[var].append( ob.getNumber(var) );                       # Get number for the given product and append the to list under the prod key the obs dictionary
                except TypeError:                                               # On exception
                  obs[var].append( ob.getString(var) );                       # Get string for the given product and append the to list under the prod key the obs dictionary

          obs['presWeather'].append(pres_weather);
          obs['skyCover'].append(sky_cov);
          obs['skyLayerBase'].append(sky_layer_base);
          pres_weather   = [];
          sky_cov        = [];
          sky_layer_base = [];
        
    for tag in obs:
      if tag in sys_data.varUnits:
        obs[tag] = np.array( obs[tag] );
#         if tag == 'windDir': 
#           obs[tag][ obs[tag] == -9999.0 ] = 'nan';
        if obs[tag].dtype.type is np.float64:
          obs[tag][ obs[tag] == -9999.0 ] = 'nan';
        elif tag == 'pressChangeChar':
          obs[tag] = [ int(i) if i.isdigit() else -1 for i in obs[tag] ];       # Convert all the string intergers to integers and replace any empty strings with -1
        if sys_data.varUnits[tag] is not None:
          obs[tag] = obs[tag] * sys_data.varUnits[tag];
    if 'presWeather' in obs:
      weather = []
      for wx in obs['presWeather']:
        key = '';
        if wx is not None:
          if type(wx) is list:
            key = wx[0]
          elif ' ' in wx:
            key = wx.split()[0]
          elif type(wx) is str:
            key = wx;          
        try:
          weather.append( wx_code_map[ key ] );
        except:
          weather.append( wx_code_map[ '' ] );
      obs['presWeather'] = weather
#         print( type(wx), wx)
#       weather = [ '' if s is None else s.split()[0] for s in obs['presWeather'] ]
    if 'skyCover' in obs:
      obs['skyCover'] = [get_cloud_cover(x) for x in obs['skyCover']]
    if 'windDir' in obs and 'windSpeed' in obs:
      u, v = wind_components(obs['windSpeed'], obs['windDir'])
      obs['windU'] = u;
      obs['windV'] = v;
    return obs