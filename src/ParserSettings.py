""" Wii Event Parser Constants """
X_POS = 60 
X_NEG = -60
Y_POS = 50
Y_NEG = -40
Z_POS = 70
Z_NEG = -45
TIME_DELTA = .3
XZ_LOCKOUT_THRESHOLD = 40
WEP_PORT = 75154
ROLL_THRESHOLD = .3
PITCH_THRESHOLD = .2
ROLL_PITCH_LOCKOUT_THRESHOLD = 30
MAX_WIIMOTES = 7
""" Boolean value to enable logging for both parsers """
IS_LOGGING = True

""" Game Event Parser Constants """
GEP_BIND_PREFIX = 'bind_'
GEP_BIND_PREFIX_LEN = len(GEP_BIND_PREFIX)
GEP_PORT = 76543
GEP_HOST = 'localhost'
GAME_PORT = 37177
GAME_HOST = 'localhost'
GEP_FILTERED_EVENTS = ('FlickX', 'Roll', 'Pitch')



# I think this is in milliseconds
GEP_COMBO_TIMEOUT = .25
GEP_ROLL_TIMEOUT = .4

GEP_EVENT_FLICK = 'Flick'
GEP_EVENT_FLICKX = 'FlickX'
GEP_EVENT_FLICKY = 'FlickY'
GEP_EVENT_FLICKZ = 'FlickZ'

GEP_EVENT_ROLL = 'Roll'
GEP_EVENT_PITCH = 'Pitch'

GEP_FILTER_EVENTS = [
					GEP_EVENT_FLICKY, 
					GEP_EVENT_ROLL, 
					GEP_EVENT_PITCH
					]
GEP_SERIES_EVENTS = [
					GEP_EVENT_ROLL, 
					GEP_EVENT_PITCH
					]

GEP_EVENT_TIMEOUT = 'Timeout=x'
GEP_EVENT_LOCK = 'Lock'
GEP_EVENT_RELEASE_LOCK = 'ReleaseLock'
