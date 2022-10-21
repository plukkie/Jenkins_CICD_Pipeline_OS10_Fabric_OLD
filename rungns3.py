#!/usr/bin/env python3

import json
import requests
import sys


settingsfile    = 'settings.json'


## Functions
def return_url ( settingsobject):
    
    s = settingsobject['gns3']
    a = sys.argv
    if 'start' in a[1:]:
        gns3call = 'nodesstarturi'
    elif 'stop' in a[1:]:
        gns3call = 'nodesstopuri'
    else:
        print('please provide GNS3 api call type "start/stop"\n')
        sys.exit()
        
    url = s['prot']+s['serverip']+":"+s['serverport']+"/"+s['projecturi']+"/"+s['project']+"/"+s[gns3call]
    return url

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
url = return_url ( settings )
r = request ( url, "post" )


