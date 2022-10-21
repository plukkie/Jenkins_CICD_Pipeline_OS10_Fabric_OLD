#!/usr/bin/env python3

import json
import requests


settingsfile    = 'settings.json'


## Functions
def readsettings ( jsonfile ):

    try:
        f       = open(jsonfile)
        data    = json.load(f)

    except:
        result  = { "tryerror" : "Error reading settings file " + jsonfile }

    else:
        result = data
    
    f.close()
    return result


def request ( url, reqtype, jsondata={} ):
    
    gns3items   = settings['gns3']
    if reqtype == 'post': r = requests.post (url, data = jsondata )

########################
##### MAIN PROGRAM #####
########################


settings = readsettings ( settingsfile ) #Read settings to JSON object

# Start all nodes in GNS3 project
s   = settings['gns3']
url = s['prot']+s['serverip']+":"+s['serverport']+"/"+s['projecturi']+"/"+s['project']+"/"+s['nodesstarturi']
r = request ( url, "post" )


