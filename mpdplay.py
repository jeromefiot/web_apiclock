# -*- coding: utf-8 -*-
import urllib2
import json
import subprocess
import time

import sys
from mpd import MPDClient

path0=sys.argv[1]

# ####################### METEO ##################################### 
page_json = urllib2.urlopen('http://api.wunderground.com/api/0def10027afaebb7/conditions/q/FR/Paris.json')
# Je lis la page
json_string = page_json.read()
parsed_json = json.loads(json_string)
# la température en °C
current_temp = parsed_json['current_observation']['temp_c'] 
texte = "Debout les moules, la température est de " +str(current_temp)+" degré."
print texte
# lance espeak depuis le shell avec la temperature
commande = subprocess.Popen("espeak -s 155 -a 200 -vfr '"+texte+"'",shell=True)
time.sleep(5)

client = MPDClient()               # create client object
client.timeout = 10                # network timeout in seconds (floats allowed), default: None
client.idletimeout = None          # timeout for fetching the result of the idle command is handled seperately, default: None
client.connect("localhost", 6600)  # connect to localhost:6600
client.add(path0)
client.play()

if __name__ == "__main__":
    manager.run()