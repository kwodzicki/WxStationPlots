from awips.dataaccess import DataAccessLayer as DAL;
from dynamicserialize.dstypes.com.raytheon.uf.common.time import TimeRange;
from metpy.calc import reduce_point_density, wind_components;

from datetime import datetime, timedelta;
import numpy as np

from . import sys_data;
from . import utils;

class awipsSurfaceObs( object ):
  def __init__(self, server = "edex-cloud.unidata.ucar.edu"):
    DAL.changeEDEXHost( server );
    self.request = DAL.newDataRequest( "obs" )
    self.__vars  = DAL.getAvailableParameters(    self.request );
    self.__stids = DAL.getAvailableLocationNames( self.request );
    self.vars    = None;
    self.stids   = None;
    self.__locs  = self.__getLocations();

  ##############################################################################
  def __getLocations(self):
    '''
    A method to get station names, longitude, and latitude for
    all available stations.
    '''
    self.setVariables( ['stationName', 'longitude', 'latitude'] );              # Set the variables to download
    self.setStations();                                                         # Set the stations to download
    timerange = self.setTime();                                                 # Get time range for download
    res  = DAL.getGeometryData( self.request, timerange );                      # Download the data
    data = {};                                                                  # Initialize a structure to store data
    for i in range( len(res) ):                                                 # iterate over all responses
      if res[i].getString( 'stationName' ) not in data:                         # If the station name is NOT in data
        data[ res[i].getString( 'stationName' ) ] = {
          'longitude' : res[i].getNumber('longitude'),
          'latitude'  : res[i].getNumber('latitude'),
        };                                                                      # Create dictionary under station name key that contains the longitude and latitude for the station
    self.vars  = None;
    self.stids = None;
    return data;
  ##############################################################################
  def reduceDensity(self, density = None):
    if self.stids is None or density is None: return;
    nstIDs = len(self.stids);
    pnts = np.zeros( (nstIDs, 3,), dtype=np.float )    
    for i in range( nstIDs ):
      if self.stids[i] in self.__locs:
        pnts[i,0] = self.__locs[ self.stids[i] ]['longitude'];
        pnts[i,1] = self.__locs[ self.stids[i] ]['latitude'];
    filter = reduce_point_density( pnts, density)
    stids  = np.asarray( self.stids )[ filter ];
    self.stids = list( stids );
  ##############################################################################
  def setStations(self, stations = None, density = None):
    self.stids = self.__stids if stations is None else stations;
    self.reduceDensity( density );
    self.request.setLocationNames( *self.stids );
  ##############################################################################
  def setVariables(self, variables = sys_data.varNames):
    self.vars = self.__vars if variables is None else variables;
    if 'stationName' not in self.vars: self.vars.append( 'stationName' );       # Make certain that stationName is in the variables
    if 'timeObs'     not in self.vars: self.vars.append( 'timeObs'     );       # Make certain that timeObs is in the variables
    self.request.setParameters( *self.vars )
  ##############################################################################
  def setTime(self, dt = 1):
    if dt is None: dt = 1
    fmt       = "%Y-%m-%d %H:00:00";
    endTime   = datetime.utcnow();
    startTime = (endTime - timedelta(hours = dt)).strftime( fmt )
    endTime   = endTime.strftime( fmt )
    sRange    = datetime.strptime( startTime, "%Y-%m-%d %H:%M:%S")
    eRange    = datetime.strptime( endTime,   "%Y-%m-%d %H:%M:%S")
    return TimeRange(sRange, eRange);
  ##############################################################################
  def __reduceDensity(self, density):
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
  def getData(self,
        stations  = None, 
        variables = sys_data.varNames, 
        density   = None, 
        reverse   = True,
        dt        = 1):
    '''
    Name:
       getData
    Purpose:
       To download station data and convert to format useable by metpy
    '''
    obs = self.getRawData( 
        stations  = stations, 
        variables = variables, 
        density   = density, 
        reverse   = reverse,
        dt        = dt)
        
#     out = dict({var: [] for var in obs[ self.stids[0] ]});                    # Generate output dictionary that will hold all data
    out = dict( {var: [] for var in self.vars} );                               # Generate output dictionary that will hold all data
    out['longitude'] = []
    out['latitude']  = []
    for stid in obs:                                                            # Iterate over all stations in the observations
      for var in obs[stid]:                                                     # Iterate over all the variables in the observations
        if var not in out: continue;
        if type( obs[stid][var] ) is list:
          val = obs[stid][var][0];                                              # Set val to the newest variable value
        else:
          val = obs[stid][var];                                                 # Set val to the newest variable value
#         if val is None:
#           val = ''
#         else:
        if var == 'pressChangeChar':                                          # If the variable name is pressChangeChar
          val = int(val) if val.isdigit() else -1;                            # Convert all the string intergers to integers and replace any empty strings with -1
        elif var == 'presWeather':                                            # Else, if variable is presWeather
          val = utils.get_presWeather( val )
        elif var == 'skyCover':
          val = utils.get_cloud_cover( val )
        out[var].append( val );
    for var in out: 
      if var  in sys_data.varUnits:
        out[var] = np.array( out[var] );
        if out[var].dtype.type is np.float64:
          out[var][ out[var] == -9999.0 ] = 'nan'
#         elif var == 'pressChangeChar':
#           out[var] 
        if sys_data.varUnits[var] is not None:
          out[var] = out[var] * sys_data.varUnits[var];
    out['longitude'] = np.array( out['longitude'] )
    out['latitude']  = np.array( out['latitude' ] )

    if 'windDir' in out and 'windSpeed' in out:
      u, v = wind_components(out['windSpeed'], out['windDir'])
      out['windU'] = u;
      out['windV'] = v;
    for key in out:
      print( key, '  :  ', out[key] )
    return out
  ##############################################################################
  def getRawData(self, 
        stations  = None, 
        variables = sys_data.varNames, 
        density   = None, 
        reverse   = True,
        dt        = 1):
    '''
    Name:
       getRawData
    Purpose:
       A method to download data from the awips API. Data are downloaded
       in 'raw' format and stored in a dictionary. Time series data are
       stored in descending order by default. The dictionary is
       organized as follows:
           'Station ID' : 
                'longitude'  : scalar
                'latitude'   : scalar
                'UTCOffset'  : scalar
                'variable1'  : list
                'variable2'  : list
    Inputs:
       None.
    Outputs:
       Returns a dictionary containing the data.
    Keywords:
       stations  : List of station IDs to download data for.
                    Default is to get all available stations.
       variables : List of variables to download.
                    Default is all variables in sys_data.varNames.
       density   : Set to a distance (in degrees) of radius in which
                    two stations should not exists. Used to thin data.
       reverse   : Set to False to return data in ascending time order.
                    Default is descending order, i.e., newest first.
       dt        : Time (in hours) in the past (relative to NOW) to grab
                    data for.
                    Default is 1 hour.
    '''
    self.setStations( stations, density );
    self.setVariables( utils.checkVars( variables ) );
    timerange = self.setTime( dt );
    res = DAL.getGeometryData( self.request, timerange );
    
    data = {}
    station_names  = [];
    pres_weather   = [];
    sky_cov        = [];
    sky_cov_type   = [];
    sky_layer_base = [];
    variables      = self.vars;
    if 'stationName' in variables: variables.remove('stationName');
    for ob in res:                                                              # Iterate over all objects in the response
      avail_params = ob.getParameters();                                        # Get the parameters in the response
      if "presWeather" in avail_params:                                         # If presWeather is in the avail_parameters
        pres_weather.append( ob.getString("presWeather") );                     # Append the present weather value to the pres_weather list
      elif "skyCover" in avail_params:                                          # Else if skyCover and skyLayerBase are in the available parameters
        sky_cov.append( ob.getString("skyCover") );                             # Append the skyCover the sky_cov list
      elif "skyCoverType" in avail_params:                                      # Else if skyCover and skyLayerBase are in the available parameters
        sky_cov_type.append( ob.getString("skyCoverType") );                    # Append the skyLayerBase ot the sky_layer_base list
      elif "skyLayerBase" in avail_params:                                      # Else if skyCover and skyLayerBase are in the available parameters
        sky_layer_base.append( ob.getNumber("skyLayerBase") );                  # Append the skyLayerBase ot the sky_layer_base list
      else:                                                                     # Else
        stID = ob.getString('stationName');                                     # Get the station id
        if stID not in data:                                                    # If the name of the station is NOT in the station_name list
          data[ stID ] = {
            'longitude' : self.__locs[ stID ]['longitude'],
            'latitude'  : self.__locs[ stID ]['latitude'],
            'utcOffset' : np.nan
          };                                                                    # Initialize dictionary under station name with longitude, latitude, and utcOffset tags, all set to NaN
          for var in variables: data[ stID ][var] = [];                         # Initialize empty list for each variable
        for var in variables:                                                   # Iterate over all the products
          if var not in avail_params:                                           # If product is not in list of available products
            data[stID][var].append( None );                                     # Append None to the list under the product key in the obs dictionary
          elif var not in sys_data.multi_value_vars:                            # If product NOT in multi_value_vars list
            if var == 'timeObs':                                                # If the product is timeObs
              date = datetime.fromtimestamp( ob.getNumber(var)/1000.0 );        # Get the time and convert to datetime object
              data[stID][var].append( date );                                   # Append the date to the list under the prod key in the obs dictionary
            else:                                                               # Else
              try:                                                              # Try to 
                data[stID][var].append( ob.getNumber(var) );                    # Get number for the given product and append the to list under the prod key the obs dictionary
              except TypeError:                                                 # On exception
                data[stID][var].append( ob.getString(var) );                    # Get string for the given product and append the to list under the prod key the obs dictionary
        if 'presWeather' in data[stID]: 
          data[stID]['presWeather'].append(pres_weather);
        if 'skyCover' in data[stID]: 
          data[stID]['skyCover'].append(sky_cov);
        if 'skyCoverType' in data[stID]: 
          data[stID]['skyCoverType'].append(sky_cov_type);
        if 'skyLayerBase' in data[stID]: 
          data[stID]['skyLayerBase'].append(sky_layer_base);
        pres_weather   = [];
        sky_cov        = [];
        sky_layer_base = [];
    return utils.nestedDictSort(data, 'timeObs', reverse = reverse);