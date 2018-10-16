from metpy.plots import wx_code_map;

#Some code for utc offset 
# import datetime, import pytz
# from tzwhere.tzwhere import tzwhere
# tz = tz.tzwhere()
# def UTCOffset( 
# timezone_str = tzwhere.tzNameAt(37.3880961, -5.9823299) # Seville coordinates
# timezone_str
# #> Europe/Madrid
# 
# timezone = pytz.timezone(timezone_str)
# dt = datetime.datetime.now()
# timezone.utcoffset(dt)
# 


def get_presWeather( code ):
  if code is None: code = '';
  if type(code) is list:
    key = code[0]
    if len(key) == 0: key = '';
  elif ' ' in code:
    key = code.split()[0]
  elif type(code) is str:
    key = code;          
  try:
    return wx_code_map[ key ];
  except:
    return wx_code_map[ '' ];


################################################################################
def checkVars( vars ):
  if 'longitude' in vars: vars.remove('longitude');
  if 'latitude'  in vars: vars.remove('latitude');
  return vars;


################################################################################
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

################################################################################
def nestedDictSort( input, key, reverse = False ):
  '''
  Function to sort lists at the bottom of nested dictionaries
  '''
  try:                                                                          # Try to (for python2)
    for k, v in input.iteritems():                                              # Iterate over the key, value pairs in the input dictionary
      if isinstance(v, dict):                                                   # If the value is a dictionary instance
        nestedDictSort( v, key, reverse );                                      # Call the function again on v
      else:                                                                     # Else, reached the bottom of the nesting
        try:
          input[k] = [
            x for _,x in sorted(zip(input[ key ], v), reverse = reverse)
          ];                                                                    # Sort the list based on the 'date' key that (should) be in the dictionary
        except:
          pass
  except:                                                                       # On exception (python3)
    for k, v in input.items():                                                  # Iterate over the key, value pairs in the input dictionary
      if isinstance(v, dict):                                                   # If the value is a dictionary instance
        nestedDictSort( v, key, reverse );                                      # Call the function again on v
      else:                                                                     # Else, reached the bottom of the nesting
        try:
          input[k] = [
            x for _,x in sorted(zip(input[ key ], v), reverse = reverse)
          ];                                                                    # Sort the list based on the 'date' key that (should) be in the dictionary
        except:
          pass
  return input                                                                  # Return the dictionary


