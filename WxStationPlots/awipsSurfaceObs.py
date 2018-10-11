from awips.dataaccess import DataAccessLayer as DAL;
from dynamicserialize.dstypes.com.raytheon.uf.common.time import TimeRange;
from metpy.calc import reduce_point_density
from datetime import datetime, timedelta;
import numpy as np

prods = ['stationName',    'timeObs',          'longitude',       'latitude', 
         'temperature',    'dewpoint',         'windDir',         'windSpeed',
         'seaLevelPress',  'pressChange3Hour', 'pressChangeChar',
         'skyCoverType',   'skyLayerBase',     'skyCover',
         'visibility',     'presWeather'];                                      # List of default products to download
         
#          'precip3Hour',  'autoStationType',  'maxTemp24Hour', 'snowWater', 'reportType', 'snowDepth', 'vertVisibility', 'wmoId',  'stationId', 'elevation', 'snowfall6Hour',  'skyCoverGenus', 'forecastHr', 'minTemp24Hour', 'refTime',  'maxTemp6Hour',  'precip24Hour', 'precip6Hour',  'tempFromTenths', 'altimeter', 'precip1Hour', 'dpFromTenths', 'pressChangeChar',  'minTemp6Hour']
class awipsSurfaceObs( object ):
  multi_value_prods = ["presWeather", "skyCover", "skyLayerBase"]
  def __init__(self, server = "edex-cloud.unidata.ucar.edu"):
    DAL.changeEDEXHost( server );
    self.request = DAL.newDataRequest( "obs" )
    self.prods   = DAL.getAvailableParameters(    self.request );
    self.stids   = DAL.getAvailableLocationNames( self.request );

  ##############################################################################
  def setStations(self, stations = None):
    if stations is None:
      self.request.setLocationNames( *self.stids );
      return self.stids
    else:
      self.request.setLocationNames( *stations );
      return stations
  ##############################################################################
  def setProducts(self, products = prods):
    if products is None:
      self.request.setParameters( *self.prods )
      return self.prods;
    else:
      self.request.setParameters( *products )
      return products;
  ##############################################################################
  def setTime(self):
    lastHour = datetime.utcnow() - timedelta(hours = 1)
    start    = lastHour.strftime( "%Y-%m-%d %H" );
    sRange   = datetime.strptime( "{}:00:00".format(start), "%Y-%m-%d %H:%M:%S")
    eRange   = datetime.strptime( "{}:59:59".format(start), "%Y-%m-%d %H:%M:%S")
    return TimeRange(sRange, eRange);
  ##############################################################################
  def reduceDensity(self, density):
    self.setProducts( ['longitude', 'latitude', 'stationName'] );
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
  def getData(self, stations = None, products = prods, density = None):
    stids = self.setStations( stations );
    if density is not None:
      stids = self.reduceDensity( density );
      stids = self.setStations( stids );
    prods = self.setProducts( products );
    timerange = self.setTime();

    obs = dict( {prod: [] for prod in prods} )
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
          for prod in prods:                                                    # Iterate over all the products
            if prod not in avail_params:                                        # If product is not in list of available products
              obs[prod].append( None );                                         # Append None to the list under the product key in the obs dictionary
            elif prod not in self.multi_value_prods:                            # If product NOT in multi_value_prods list
              if prod == 'timeObs':                                             # If the product is timeObs
                date = datetime.fromtimestamp( ob.getNumber(prod)/1000.0 );     # Get the time and convert to datetime object
                obs[prod].append( date );                                       # Append the date to the list under the prod key in the obs dictionary
              else:                                                             # Else
                try:                                                            # Try to 
                  obs[prod].append( ob.getNumber(prod) );                       # Get number for the given product and append the to list under the prod key the obs dictionary
                except TypeError:                                               # On exception
                  obs[prod].append( ob.getString(prod) );                       # Get string for the given product and append the to list under the prod key the obs dictionary

          obs['presWeather'].append(pres_weather);
          obs['skyCover'].append(sky_cov);
          obs['skyLayerBase'].append(sky_layer_base);
          pres_weather   = [];
          sky_cov        = [];
          sky_layer_base = [];
    return obs


