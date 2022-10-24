#!/usr/bin/env python3

import json
import requests
import sys


settingsfile    = 'settings.json'


## Functions

def return_url ( settingsobject ):

    a = sys.argv
    url = ""

    if 'startgns3' in a[1:] or 'stopgns3' in a[1:]:
        toplevelkey = 'gns3'
        s = settingsobject[toplevelkey]
        url = s['prot']+s['serverip']+":"+s['serverport']+"/"+s['projecturi']+"/"+s['project']
        if 'startgns3' in a[1:]: url = url+"/"+s['nodesstarturi']
        if 'stopgns3' in a[1:]: url = url+"/"+s['nodesstopuri']
    elif 'launchawx' in a[1:]:
        toplevelkey = 'awx'
        s = settingsobject[toplevelkey]
        url = s['prot']+s['serverip']+":"+s['serverport']+"/"+s['projecturi']+"/"+s['jobtemplateid']+"/"+s['launchsuffix']
    
    else: #No cli arguments given
        print('\nusage : ' + sys.argv[0] + ' <option>\n')
        print(' - startgns3 : will start GNS3 project')
        print(' - stopgns3  : will stop GNS3 project')
        print(' - launchawx : will start job template on Ansible tower')
        print('=========================================================')
        sys.exit()

    return url

"""
    s = settingsobject[toplevelkey]
    a = sys.argv
    url = s['prot']+s['serverip']+":"+s['serverport']+"/"+s['projecturi']

    if 'startgns3' in a[1:]:
        url = url+"/"+s['project']+"/"+s['nodesstarturi']
    elif 'stopgns3' in a[1:]:
        url = url+"/"+s['project']+"/"+s['nodesstopuri']
    elif 'launchawx' in a[1:]:
        return url
    else:
        print('\nusage : ' + sys.argv[0] + ' <option>\n')
        print(' - startgns3 : will start GNS3 project')
        print(' - stopgns3  : will stop GNS3 project')
        print(' - launchawx : will start job template on Ansible tower')
        print('=========================================================')
        sys.exit()
        
    return url
"""

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
#r = request ( url, "post" )

print(url)

