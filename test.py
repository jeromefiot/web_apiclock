# -*- coding: utf-8 -*-
import urllib2
import json
import subprocess

def parle():
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

if __name__ == "__main__":
    parle()