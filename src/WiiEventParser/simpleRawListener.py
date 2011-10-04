import socket
import WiiEventParser
import sys,os
try:
    import ParserSettings
except:
    filepath = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(os.path.dirname(filepath))
    import ParserSettings

parser = WiiEventParser.WiiEventParser()

parser.start() 
