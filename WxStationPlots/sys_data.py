from metpy.units import units;
from metpy.plots import StationPlotLayout; #simple_layout
from metpy.plots.wx_symbols import current_weather   as cur_wx_sym;
from metpy.plots.wx_symbols import pressure_tendency as pres_tend_sym;
pres_tend_sym.chrs.append( ' ' );                                               # Append space for missing codes

domains = {
      'CONUS'           : {'limits' : (-120, -73, 23, 50), 'res' : '110m'},
      'Northeast'       : {'limits' : (-100, -73, 35, 50), 'res' : '50m'},
      'Southeast'       : {'limits' : (-100, -73, 23, 35), 'res' : '50m'},
      'Mid West'        : {'limits' : (-110, -85, 35, 50), 'res' : '50m'},
      'Southern Plains' : {'limits' : (-110, -85, 23, 35), 'res' : '50m'}};

# custom_layout = StationPlotLayout()
# custom_layout.add_barb('windU', 'windV', units='knots')
# custom_layout.add_value('NW', 'temperature', fmt='.0f', units='degF', color='darkred')
# custom_layout.add_value('SW', 'dewpoint',    fmt='.0f', units='degF', color='darkgreen')
# custom_layout.add_symbol('W', 'presWeather', wx_symbols.current_weather)
# custom_layout.add_value('E', 'precipitation', fmt='0.1f', units='inch', color='blue')

    
varNames = [
  'stationName',    'timeObs',   
  'temperature',    'dewpoint',
  'windDir',         'windSpeed',
  'seaLevelPress',  'pressChange3Hour', 'pressChangeChar',
#   'skyCoverType',   'skyLayerBase',     'skyCover',
  'visibility',     'presWeather'
];                                                                              # List of default products to download

varUnits = {
  'stationName'      : None,
  'timeObs'          : None,
#   'longitude'        : None,
#   'latitude'         : None,
  'temperature'      : units.degC,
  'dewpoint'         : units.degC,
  'windDir'          : units.degree,
  'windSpeed'        : units('knots'),
  'seaLevelPress'    : units('Pa'),
  'pressChange3Hour' : units('Pa'),
  'pressChangeChar'  : None,
  'visibility'       : units.us_statute_mile};   
multi_value_vars = ["presWeather", "skyCover", "skyLayerBase"]
  
colors = ['Black', 'DarkRed', 'Red', 'DarkOrange', 'Gold',
          'Green', 'Cyan', 'Blue', 'Purple']
sfcLookupTable = {
  'Station Name'     : {'variable' : 'stationName',      'units' : None,                  'symbol' : None,          'fmt' : ''},
  'Observation Time' : {'variable' : 'timeObs',          'units' : None,                  'symbol' : None,          'fmt' : ''},
#   'Longitude'        : {'variable' : 'longitude',        'units' : units.degrees_east,    'symbol' : None,          'fmt' : ''},
#   'Latitude'         : {'variable' : 'latitude',         'units' : units.degrees_north,   'symbol' : None,          'fmt' : ''},
  'Temperature'      : {'variable' : 'temperature',      'units' : units.degF,            'symbol' : None,          'fmt' : '.0f'},
  'Dew Point'        : {'variable' : 'dewpoint',         'units' : units.degF,            'symbol' : None,          'fmt' : '.0f'},
  'Wind Direction'   : {'variable' : 'windDir',          'units' : units.degree,          'symbol' : None,          'fmt' : ''},
  'Wind Speed'       : {'variable' : 'windSpeed',        'units' : units('knots'),        'symbol' : None,          'fmt' : ''},
  'MSLP'             : {'variable' : 'seaLevelPress',    'units' : units('mbar'),         'symbol' : None,          'fmt' : lambda v: format(10 * v, '03.0f')[-3:]},
  'MSLP Change'      : {'variable' : 'pressChange3Hour', 'units' : units('mbar'),         'symbol' : None,          'fmt' : lambda v: ('-' if v < 0 else '') + format(10 * abs(v), '02.0f')},
  'MSLP Change Sym'  : {'variable' : 'pressChangeChar',  'units' : None,                  'symbol' : pres_tend_sym, 'fmt' : ''},
  'Sky Cover'        : {'variable' : 'skyCover',         'units' : None,                  'symbol' : None,          'fmt' : ''},
  'Sky Cover Type'   : {'variable' : 'skyCoverType',     'units' : None,                  'symbol' : None,          'fmt' : ''},
  'Sky Cover Base'   : {'variable' : 'skyLayerBase',     'units' : None,                  'symbol' : None,          'fmt' : ''},
  'Visibility'       : {'variable' : 'visibility',       'units' : units.us_statute_mile, 'symbol' : None,          'fmt' : '.0f'},
  'Current Wx'       : {'variable' : 'presWeather',      'units' : None,                  'symbol' : cur_wx_sym,    'fmt' : ''},
}

  

sfcLayout = {
  (-1.0,  1.0) : {'name'     : 'Temperature',
                  'color'    : 'Black'},
  (-2.0,  0.0) : {'name'     : 'Visibility',
                  'color'    : 'Black'},
  (-1.0,  0.0) : {'name'     : 'Current Wx',
                  'color'    : 'Black'},  
  (-1.0, -1.0) : {'name'     : 'Dew Point',
                  'color'    : 'Black'},
  ( 1.0,  1.0) : {'name'     : 'MSLP',
                  'color'    : 'Black'},
  ( 1.0,  0.0) : {'name'     : 'MSLP Change',
                  'color'    : 'Black'},
#   ( 2.0,  0.0) : {'name'     : 'MSLP Change Sym',
#                   'color'    : 'Black'},
}
# sfcLayout = {
#   (-1.0,  1.0) : {'variable' : 'temperature',
#                   'name'     : 'Temperature',
#                   'units'    : units.degC,
#                   'color'    : 'black'},
#   (-2.0,  0.0) : {'variable' : 'visibility',
#                   'name'     : 'Visibility',
#                   'units'    : units.us_statute_mile,
#                   'color'    : 'black'},
#   (-1.0,  0.0) : {'variable' : 'presWeather',
#                   'name'     : 'Present Wx',
#                   'units'    : None,
#                   'color'    : 'black'},  
#   (-1.0, -1.0) : {'variable' : 'dewpoint',
#                   'name'     : 'Dew point',
#                   'units'    : units.degC,
#                   'color'    : 'black'},
#   ( 1.0,  1.0) : {'variable' : 'seaLevelPress',
#                   'name'     : 'MSLP',
#                   'units'    : units.mbar,
#                   'color'    : 'black'},
#   ( 1.0,  0.0) : {'variable' : 'pressChange3Hour',
#                   'name'     : 'MSLP change',
#                   'units'    : units.mbar,
#                   'color'    : 'black'}
#   ( 1.0,  0.0) : {'variable' : 'pressChange3Hour',
#                   'name'     : 'MSLP change',
#                   'units'    : units.mbar,
#                   'color'    : 'black'}
# }

#          'precip3Hour',  'autoStationType',  'maxTemp24Hour', 'snowWater', 'reportType', 'snowDepth', 'vertVisibility', 'wmoId',  'stationId', 'elevation', 'snowfall6Hour',  'skyCoverGenus', 'forecastHr', 'minTemp24Hour', 'refTime',  'maxTemp6Hour',  'precip24Hour', 'precip6Hour',  'tempFromTenths', 'altimeter', 'precip1Hour', 'dpFromTenths', 'pressChangeChar',  'minTemp6Hour']


